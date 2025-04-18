from typing import Any, List, Optional

from pydantic import Field

from src.agent.mcp import MCPAgent
from src.prompt.technical_analysis import TECHNICAL_ANALYSIS_SYSTEM_PROMPT

from src.agent.toolcall import ToolCallAgent
from src.schema import Message
from src.tool import Terminate, ToolCollection
from src.tool.technical_analysis import TechnicalAnalysisTool


class TechnicalAnalysisAgent(MCPAgent):
    """Technical analysis agent applying technical indicators to stock analysis."""

    name: str = "technical_analysis_agent"
    description: str = (
        "Applies technical analysis and chart patterns to stock market analysis."
    )

    system_prompt: str = TECHNICAL_ANALYSIS_SYSTEM_PROMPT

    # Initialize with FinGenius tools with proper type annotation
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            TechnicalAnalysisTool(),
            Terminate(),
        )
    )
    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    async def run(
        self, request: Optional[str] = None, stock_code: Optional[str] = None
    ) -> Any:
        """Run technical analysis on the given stock using technical indicators.

        Args:
            request: Optional initial request to process. If provided, overrides stock_code parameter.
            stock_code: The stock code/ticker to analyze

        Returns:
            Dictionary containing technical analysis insights
        """
        # If stock_code is provided but request is not, create request from stock_code
        if stock_code and not request:
            # Set up system message about the stock being analyzed
            self.memory.add_message(
                Message.system_message(
                    f"You are now performing technical analysis for stock: {stock_code}. "
                    f"Evaluate price trends, chart patterns, and key technical indicators "
                    f"to formulate short and medium-term trading strategies."
                )
            )
            request = (
                f"Analyze technical indicators and chart patterns for {stock_code}"
            )

        # Call parent implementation with the request
        return await super().run(request)
