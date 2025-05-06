import asyncio
import random
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from src.agent.base import AgentState, BaseAgent
from src.agent.toolcall import ToolCallAgent
from src.environment.base import BaseEnvironment
from src.logger import logger
from src.prompt.battle import (
    EVENT_TYPES,
    VOTE_OPTIONS,
    get_agent_instructions,
    get_broadcast_message,
    get_report_context,
)
from src.tool.base import BaseTool, ToolResult
from src.tool.battle import Battle
from src.tool.terminate import Terminate
from src.tool.tool_collection import ToolCollection


class BattleState(BaseModel):
    """Battle state tracking"""

    active_agents: Dict[str, str] = Field(default_factory=dict)
    voted_agents: Dict[str, str] = Field(default_factory=dict)
    terminated_agents: Dict[str, bool] = Field(default_factory=dict)
    battle_history: List[Dict[str, Any]] = Field(default_factory=list)
    vote_results: Dict[str, int] = Field(
        default_factory=lambda: {option: 0 for option in VOTE_OPTIONS}
    )
    battle_highlights: List[Dict[str, Any]] = Field(default_factory=list)
    battle_over: bool = Field(default=False)

    def is_agent_active(self, agent_id: str) -> bool:
        """Check if agent is active and can participate"""
        return (
            agent_id in self.active_agents
            and agent_id not in self.voted_agents
            and agent_id not in self.terminated_agents
        )

    def add_event(self, event_type: str, agent_id: str, **kwargs) -> Dict[str, Any]:
        """Add event to history and return the event"""
        event = {
            "type": event_type,
            "agent_id": agent_id,
            "agent_name": self.active_agents.get(agent_id, "Unknown"),
            **kwargs,
        }
        self.battle_history.append(event)
        return event

    def mark_terminated(self, agent_id: str, reason: str) -> None:
        """Mark agent as terminated"""
        self.terminated_agents[agent_id] = True

    def record_vote(self, agent_id: str, vote: str) -> None:
        """Record agent vote"""
        self.voted_agents[agent_id] = vote
        self.vote_results[vote] += 1

        # Check if battle is over
        if len(self.voted_agents) + len(self.terminated_agents) == len(
            self.active_agents
        ):
            self.battle_over = True

    def add_highlight(self, agent_name: str, content: str) -> None:
        """Add highlight if content is significant"""
        if len(content) > 20:  # Simple heuristic
            self.battle_highlights.append({"agent": agent_name, "point": content})

    def all_agents_decided(self) -> bool:
        """Check if all agents have voted or terminated"""
        return all(
            agent_id in self.voted_agents or agent_id in self.terminated_agents
            for agent_id in self.active_agents
        )


class BattleEnvironment(BaseEnvironment):
    """Environment for agents to battle and vote on stock sentiment"""

    name: str = Field(default="battle_environment")
    description: str = Field(default="Environment for stock market battles")
    state: BattleState = Field(default_factory=BattleState)
    tools: Dict[str, BaseTool] = Field(default_factory=dict)
    max_steps: int = Field(default=3, description="Maximum steps for each agent")

    async def initialize(self) -> None:
        """Initialize the battle environment"""
        await super().initialize()
        self.state = BattleState()
        logger.info(f"Battle environment initialized (max_steps={self.max_steps})")

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with battle tools and instructions"""
        super().register_agent(agent)
        agent_id = agent.name
        self.state.active_agents[agent_id] = agent.name

        # Set max_steps for the agent
        if hasattr(agent, "max_steps"):
            agent.max_steps = self.max_steps

        if isinstance(agent, ToolCallAgent) and hasattr(agent, "available_tools"):
            battle_tool = Battle(agent_id=agent_id)
            battle_tool.controller = self
            self.tools[agent_id] = battle_tool
            agent.available_tools = ToolCollection(battle_tool, Terminate())

            # Use agent-specific information to generate battle instructions
            agent_description = getattr(agent, "description", "")
            agent_instructions = get_agent_instructions(agent.name, agent_description)
            agent.update_memory("system", agent_instructions)

    async def run(self, report: Dict[str, Any]) -> Dict[str, Any]:
        """Run the battle environment"""
        if not self.agents:
            return {"error": "No agents registered"}

        await self._send_initial_context(report)

        while not self.state.battle_over:
            await self._run_agent_steps()
            if self.state.all_agents_decided():
                self.state.battle_over = True
                break

        return self._prepare_results()

    async def handle_speak(self, agent_id: str, content: str) -> ToolResult:
        """Handle agent speaking action"""
        if not self.state.is_agent_active(agent_id):
            return ToolResult(error=self._get_error_message(agent_id))

        event = self.state.add_event(EVENT_TYPES["speak"], agent_id, content=content)
        self.state.add_highlight(event["agent_name"], content)
        await self._broadcast_message(agent_id, content, EVENT_TYPES["speak"])

        return ToolResult(output=f"Message sent: {content}")

    async def handle_vote(self, agent_id: str, vote: str) -> ToolResult:
        """Handle agent voting action"""
        if not self.state.is_agent_active(agent_id):
            return ToolResult(error=self._get_error_message(agent_id))

        if vote not in VOTE_OPTIONS:
            return ToolResult(
                error=f"Invalid vote option. Must be one of: {', '.join(VOTE_OPTIONS)}"
            )

        self.state.record_vote(agent_id, vote)
        self.state.add_event(EVENT_TYPES["vote"], agent_id, vote=vote)
        await self._broadcast_message(agent_id, f"voted {vote}", EVENT_TYPES["vote"])

        return ToolResult(output=f"Vote recorded: {vote}")

    async def cleanup(self) -> None:
        """Clean up battle resources"""
        for tool in self.tools.values():
            tool.controller = None
        await super().cleanup()

    # Private helper methods
    def _get_error_message(self, agent_id: str) -> str:
        """Get appropriate error message for agent"""
        if agent_id not in self.state.active_agents:
            return f"Agent {agent_id} is not registered"
        return f"Agent {agent_id} has already {agent_id in self.state.voted_agents and 'voted' or 'terminated'}"

    async def _run_agent_steps(self) -> None:
        """Run steps for active agents"""
        active_agents = [
            (agent_id, agent)
            for agent_id, agent in self.agents.items()
            if self.state.is_agent_active(agent_id) and hasattr(agent, "step")
        ]

        if not active_agents:
            return

        # Check and terminate agents that reached max steps
        for agent_id, agent in active_agents:
            if hasattr(agent, "current_step") and hasattr(agent, "max_steps"):
                if agent.current_step >= agent.max_steps:
                    self._terminate_agent(agent_id, EVENT_TYPES["max_steps_reached"])
                    continue

        # Run steps for remaining active agents
        tasks = {
            asyncio.create_task(agent.step()): agent_id
            for agent_id, agent in active_agents
            if agent_id not in self.state.terminated_agents
        }

        if not tasks:
            return

        completed, pending = await asyncio.wait(
            tasks.keys(), timeout=10, return_when=asyncio.ALL_COMPLETED
        )

        # Cancel pending tasks and increment step counter
        for task in pending:
            task.cancel()

        # Update step counter for completed agents
        for task in completed:
            agent_id = tasks.get(task)
            if agent_id and agent_id in self.agents:
                agent = self.agents[agent_id]
                if hasattr(agent, "current_step"):
                    agent.current_step += 1

                # Check if agent terminated itself
                if hasattr(agent, "state") and agent.state == AgentState.FINISHED:
                    self._terminate_agent(agent_id, EVENT_TYPES["terminate"])

    def _terminate_agent(self, agent_id: str, reason: str) -> None:
        """Mark agent as terminated and add event"""
        self.state.mark_terminated(agent_id, reason)
        self.state.add_event(reason, agent_id)

    async def _broadcast_message(
        self, sender_id: str, content: str, action_type: str
    ) -> None:
        """Broadcast message to all agents except sender"""
        sender_name = self.state.active_agents.get(sender_id, "Unknown")
        message = get_broadcast_message(sender_name, content, action_type)

        for agent_id, agent in self.agents.items():
            if agent_id != sender_id:
                agent.update_memory("system", message)

    async def _send_initial_context(self, report: Dict[str, Any]) -> None:
        """Send initial context to all agents"""
        summary = report.get("summary", {}).get(
            "executive_summary", "A stock analysis has been conducted."
        )
        pros = report.get("pros_and_cons", {}).get("pros", [])
        cons = report.get("pros_and_cons", {}).get("cons", [])

        context = get_report_context(summary, pros, cons)

        for agent in self.agents.values():
            agent.update_memory("system", context)

    def _prepare_results(self) -> Dict[str, Any]:
        """Prepare final battle results"""
        bullish = self.state.vote_results["bullish"]
        bearish = self.state.vote_results["bearish"]

        final_decision = (
            "Bullish"
            if bullish > bearish
            else "Bearish"
            if bearish > bullish
            else random.choice(VOTE_OPTIONS)
        )

        return {
            "final_decision": final_decision,
            "vote_count": {"bullish": bullish, "bearish": bearish},
            "battle_history": self.state.battle_history,
            "battle_highlights": self.state.battle_highlights[:5],
        }
