import asyncio
from typing import Any, Dict

from pydantic import Field

from src.agent.hot_money import HotMoneyAgent
from src.agent.report import ReportAgent
from src.agent.risk_control import RiskControlAgent
from src.agent.sentiment import SentimentAgent
from src.agent.technical_analysis import TechnicalAnalysisAgent
from src.environment.base import BaseEnvironment
from src.logger import logger
from src.schema import Message
from src.tool.stock_info_request import StockInfoRequest


class ResearchEnvironment(BaseEnvironment):
    """Environment for stock research using multiple specialized agents."""

    name: str = Field(default="research_environment")
    description: str = Field(default="Environment for comprehensive stock research")
    results: Dict[str, Any] = Field(default_factory=dict)

    # Analysis mapping for agent roles
    analysis_mapping: Dict[str, str] = Field(
        default={
            "sentiment_agent": "sentiment",
            "risk_control_agent": "risk",
            "hot_money_agent": "hot_money",
            "technical_analysis_agent": "technical",
        }
    )

    async def initialize(self) -> None:
        """Initialize the research environment with specialized agents."""
        await super().initialize()

        # Create specialized analysis agents
        specialized_agents = {
            "sentiment_agent": await SentimentAgent.create(),
            "risk_control_agent": await RiskControlAgent.create(),
            "hot_money_agent": await HotMoneyAgent.create(),
            "technical_analysis_agent": await TechnicalAnalysisAgent.create(),
            "report_agent": await ReportAgent.create(),
        }

        # Register all agents
        for agent in specialized_agents.values():
            self.register_agent(agent)

        logger.info("Research environment initialized with specialized agents")

    async def run(self, stock_code: str) -> Dict[str, Any]:
        """Run research on the given stock code using all specialist agents."""
        logger.info(f"Running research on stock {stock_code}")

        try:
            # 获取股票基本信息
            basic_info_tool = StockInfoRequest()
            basic_info_result = await basic_info_tool.execute(stock_code=stock_code)

            if basic_info_result.error:
                logger.error(f"Error getting basic info: {basic_info_result.error}")
            else:
                # 将基本信息添加到每个agent的上下文中
                stock_info_message = f"""
                股票代码: {stock_code}
                当前交易日: {basic_info_result.output.get('current_trading_day', '未知')}
                基本信息: {basic_info_result.output.get('basic_info', '{}')}
                """

                for agent_key in self.analysis_mapping.keys():
                    agent = self.get_agent(agent_key)
                    if agent and hasattr(agent, "memory"):
                        agent.memory.add_message(
                            Message.system_message(stock_info_message)
                        )
                        logger.info(f"Added basic stock info to {agent_key}'s context")

            # Run analysis tasks concurrently for each specialist agent
            tasks = {
                result_key: self.agents[agent_key].run(stock_code)
                for agent_key, result_key in self.analysis_mapping.items()
                if agent_key in self.agents
            }

            if not tasks:
                return {
                    "error": "No specialist agents available",
                    "stock_code": stock_code,
                }

            results = dict(zip(tasks.keys(), await asyncio.gather(*tasks.values())))

            # 添加基本信息到结果中
            if not basic_info_result.error:
                results["basic_info"] = basic_info_result.output

            # Prepare summary for report agent
            summary = "\n\n".join(
                [
                    f"Specialist agent research for {stock_code}:",
                    f"Sentiment Analysis: {results.get('sentiment', 'Not available')}",
                    f"Risk Analysis: {results.get('risk', 'Not available')}",
                    f"Hot Money Analysis: {results.get('hot_money', 'Not available')}",
                    f"Technical Analysis: {results.get('technical', 'Not available')}",
                ]
            )

            # Generate final report
            report_agent = self.get_agent("report_agent")
            if report_agent:
                # 也将股票基本信息添加到报告agent的上下文中
                if not basic_info_result.error:
                    report_agent.memory.add_message(
                        Message.system_message(stock_info_message)
                    )

                report_agent.memory.add_message(Message.system_message(summary))
                report = await report_agent.run(
                    request=f"Generate a comprehensive report for stock {stock_code} based on specialist research"
                )
                results["report"] = report

            # Store and return complete results
            self.results = {**results, "stock_code": stock_code}
            return self.results

        except Exception as e:
            logger.error(f"Error in research: {str(e)}")
            return {"error": str(e), "stock_code": stock_code}

    async def cleanup(self) -> None:
        """Clean up all agent resources."""
        cleanup_tasks = [
            agent.cleanup()
            for agent in self.agents.values()
            if hasattr(agent, "cleanup")
        ]

        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks)

        await super().cleanup()
