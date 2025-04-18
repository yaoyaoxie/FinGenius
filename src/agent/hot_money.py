from typing import Any, List, Optional

from pydantic import Field

from src.agent.mcp import MCPAgent
from src.prompt.hot_money import HOT_MONEY_SYSTEM_PROMPT

from src.schema import Message
from src.tool import Terminate, ToolCollection
from src.tool.hot_money import HotMoneyTool


class HotMoneyAgent(MCPAgent):
    """Hot money analysis agent focused on institutional trading patterns."""

    name: str = "hot_money_agent"
    description: str = (
        "Analyzes institutional trading patterns, fund positions, and capital flows."
    )

    system_prompt: str = HOT_MONEY_SYSTEM_PROMPT

    # Initialize with FinGenius tools with proper type annotation
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            HotMoneyTool(),
            Terminate(),
        )
    )
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    async def run(
            self, request: Optional[str] = None, stock_code: Optional[str] = None
    ) -> Any:
        """Run institutional trading analysis on the given stock.

        Args:
            request: Optional initial request to process. If provided, overrides stock_code parameter.
            stock_code: The stock code/ticker to analyze

        Returns:
            Dictionary containing institutional trading analysis
        """
        # If stock_code is provided but request is not, create request from stock_code
        if stock_code and not request:
            # Set up system message about the stock being analyzed
            self.memory.add_message(
                Message.system_message(
                    f"You are now analyzing institutional trading patterns for stock: {stock_code}. "
                    f"Identify major institutional investors, track recent changes in ownership, "
                    f"and analyze trading patterns for smart money movement."
                )
            )
            request = (
                f"Analyze institutional trading and fund positions for {stock_code}"
            )

        # Call parent implementation with the request
        return await super().run(request)
