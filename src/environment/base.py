from abc import abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field

from src.agent.base import BaseAgent
from src.logger import logger


class BaseEnvironment(BaseModel):
    """Base environment class for all environments"""

    name: str = Field(default="base_environment")
    description: str = Field(default="Base environment class")
    agents: Dict[str, BaseAgent] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    async def create(cls, **kwargs) -> "BaseEnvironment":
        """Factory method to create and initialize an environment"""
        instance = cls(**kwargs)
        await instance.initialize()
        return instance

    async def initialize(self) -> None:
        """Initialize the environment. Override in subclasses."""
        logger.info(f"Initializing {self.name} environment")

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent with the environment"""
        self.agents[agent.name] = agent
        logger.debug(f"Agent {agent.name} registered in {self.name}")

    # Alias for register_agent for better API flexibility
    def add_agent(self, agent: BaseAgent) -> None:
        """Alias for register_agent"""
        self.register_agent(agent)

    def get_agent(self, agent_name: str) -> Optional[BaseAgent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)

    @abstractmethod
    async def run(self, **kwargs) -> Dict[str, Any]:
        """Run the environment. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement run method")

    async def cleanup(self) -> None:
        """Clean up resources when done"""
        logger.info(f"Cleaning up {self.name} environment")


class EnvironmentType(str, Enum):
    """Enum of available environment types"""

    RESEARCH = "research"
    BATTLE = "battle"
