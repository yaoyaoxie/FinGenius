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
    max_steps: int = Field(default=3, description="Maximum steps for each agent")

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
            "sentiment_agent": await SentimentAgent.create(max_steps=self.max_steps),
            "risk_control_agent": await RiskControlAgent.create(max_steps=self.max_steps),
            "hot_money_agent": await HotMoneyAgent.create(max_steps=self.max_steps),
            "technical_analysis_agent": await TechnicalAnalysisAgent.create(max_steps=self.max_steps),
            "report_agent": await ReportAgent.create(max_steps=self.max_steps),
        }

        # Register all agents
        for agent in specialized_agents.values():
            self.register_agent(agent)

        logger.info(f"Research environment initialized with specialized agents (max_steps={self.max_steps})")

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
                    f"金融专家对{stock_code}的研究结果如下：",
                    f"情感分析：{results.get('sentiment', '暂无数据')}",
                    f"风险分析：{results.get('risk', '暂无数据')}",
                    f"游资分析：{results.get('hot_money', '暂无数据')}",
                    f"技术面分析：{results.get('technical', '暂无数据')}",
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
                    request=f"基于专家研究结果为股票{stock_code}生成一份综合报告"
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
