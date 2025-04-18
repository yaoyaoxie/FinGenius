from typing import Any, List, Optional

from pydantic import Field

from src.agent.mcp import MCPAgent
from src.prompt.sentiment import SENTIMENT_SYSTEM_PROMPT

from src.agent.toolcall import ToolCallAgent
from src.schema import Message
from src.tool import Terminate, ToolCollection
from src.tool.sentiment import SentimentTool
from src.tool.web_search import WebSearch


class SentimentAgent(MCPAgent):
    """Sentiment analysis agent focused on market sentiment and news."""

    name: str = "sentiment_agent"
    description: str = "Analyzes market sentiment, news, and social media for insights on stock performance."
    system_prompt: str = SENTIMENT_SYSTEM_PROMPT

    # Initialize with FinGenius tools with proper type annotation
    available_tools: ToolCollection = Field(
        default_factory=lambda: ToolCollection(
            SentimentTool(),
            WebSearch(),
            Terminate(),
        )
    )

    special_tool_names: List[str] = Field(default_factory=lambda: [Terminate().name])

    async def run(
        self, request: Optional[str] = None, stock_code: Optional[str] = None
    ) -> Any:
        """Run sentiment analysis on the given stock.

        Args:
            request: Optional initial request to process. If provided, overrides stock_code parameter.
            stock_code: The stock code/ticker to analyze

        Returns:
            Dictionary containing sentiment analysis results
        """
        # If stock_code is provided but request is not, create request from stock_code
        if stock_code and not request:
            # Set up system message about the stock being analyzed
            self.memory.add_message(
                Message.system_message(
                    f"You are now analyzing market sentiment for stock: {stock_code}. "
                    f"Gather relevant news articles, social media data, and evaluate overall sentiment."
                )
            )
            request = f"Analyze market sentiment and news for {stock_code}"

        # Call parent implementation with the request
        return await super().run(request)
