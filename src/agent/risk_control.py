from typing import Any, List, Optional

from pydantic import Field

from src.agent.mcp import MCPAgent
from src.prompt.risk_control import RISK_SYSTEM_PROMPT
from src.schema import Message
from src.tool import Terminate, ToolCollection
from src.tool.risk_control import RiskControlTool


class RiskControlAgent(MCPAgent):
    """Risk analysis agent focused on identifying and quantifying investment risks."""

    name: str = "risk_control_agent"
    description: str = "Analyzes financial risks and proposes risk control strategies for stock investments."
    system_prompt: str = RISK_SYSTEM_PROMPT

    # Initialize with FinGenius tools with proper type annotation
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            RiskControlTool(),
            Terminate(),
        )
    )
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    async def run(
        self, request: Optional[str] = None, stock_code: Optional[str] = None
    ) -> Any:
        """Run risk analysis on the given stock.

        Args:
            request: Optional initial request to process. If provided, overrides stock_code parameter.
            stock_code: The stock code/ticker to analyze

        Returns:
            Dictionary containing comprehensive risk analysis
        """
        # If stock_code is provided but request is not, create request from stock_code
        if stock_code and not request:
            # Set up system message about the stock being analyzed
            self.memory.add_message(
                Message.system_message(
                    f"You are now analyzing risk factors for stock: {stock_code}. "
                    f"Gather relevant financial data and perform comprehensive risk assessment."
                )
            )
            request = f"Perform a comprehensive risk analysis for {stock_code}"

        # Call parent implementation with the request
        return await super().run(request)
