# !/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from typing import Any, Dict

from src.environment.battle import BattleEnvironment
from src.environment.research import ResearchEnvironment
from src.logger import logger
from src.tool.tts_tool import TTSTool


async def run_stock_pipeline(stock_code: str):
    """Research a stock using the agent team and run the battle."""
    logger.info(f"Researching stock {stock_code}...")

    # Initialize environments
    research_env = await ResearchEnvironment.create()
    battle_env = await BattleEnvironment.create()

    try:
        # Run stock research
        research_result = await research_env.run(stock_code)
        if not research_result:
            logger.error("Research failed to produce results")
            return {"error": "Research failed", "stock_code": stock_code}

        logger.info("\n=== Research Complete! Starting Battle ===\n")

        # Register agents for battle
        agent_names = [
            "sentiment_agent",
            "risk_control_agent",
            "hot_money_agent",
            "technical_analysis_agent",
        ]
        for name in agent_names:
            agent = research_env.get_agent(name)
            if agent:
                # Reset agent's execution state before battle
                agent.reset_execution_state()
                battle_env.register_agent(agent)
            else:
                logger.warning(f"Agent {name} not available for battle")

        # Run battle and combine results
        battle_result = await battle_env.run(research_result)
        if not battle_result:
            logger.error("Battle failed to produce results")
            return {
                "error": "Battle failed",
                "stock_code": stock_code,
                **research_result,
            }

        logger.info("\n=== Battle Complete! ===\n")

        return {**research_result, "battle_result": battle_result}
    except Exception as e:
        logger.error(f"Pipeline execution failed: {str(e)}")
        return {"error": str(e), "stock_code": stock_code}
    finally:
        await research_env.cleanup()
        await battle_env.cleanup()


async def announce_result_with_tts(results: Dict[str, Any]):
    """使用TTS工具播报最终的博弈结果"""
    try:
        battle_result = results.get("battle_result", {})
        final_decision = battle_result.get("final_decision", "Unknown")
        vote_count = battle_result.get("vote_count", {})
        stock_code = results.get("stock_code", "未知股票")

        if final_decision == "Unknown":
            tts_text = f"对{stock_code}的分析结果不明确，无法给出明确的建议。"
        else:
            bullish_count = vote_count.get("bullish", 0)
            bearish_count = vote_count.get("bearish", 0)

            if final_decision == "bullish":
                decision_text = "看涨"
            else:
                decision_text = "看跌"

            tts_text = f"股票{stock_code}的最终预测结果是{decision_text}。看涨票数{bullish_count}，看跌票数{bearish_count}。"

            # 添加一些关键战斗点
            if battle_result.get("battle_highlights"):
                tts_text += "关键分析点包括："
                for i, highlight in enumerate(
                    battle_result["battle_highlights"][:3]
                ):  # 只取前3个要点
                    agent = highlight.get("agent", "")
                    point = highlight.get("point", "")
                    tts_text += f"{agent}认为{point}。"

        # 初始化TTS工具并播报结果
        tts_tool = TTSTool()
        output_file = f"results/{stock_code}_result.mp3"

        # 执行TTS转换并播放
        await tts_tool.execute(text=tts_text, output_file=output_file)

        logger.info(f"结果语音播报已保存至: {output_file}")

    except Exception as e:
        logger.error(f"语音播报失败: {str(e)}")


def display_results(
    results: Dict[str, Any], output_format: str = "text", output_file: str = None
):
    """Display or save research results."""
    # Handle JSON output
    if output_format == "json":
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {output_file}")
        else:
            print(json.dumps(results, indent=2, ensure_ascii=False))
        return

    # Prepare output destination
    out_file = open(output_file, "w", encoding="utf-8") if output_file else sys.stdout

    try:
        # Display basic information
        print(
            f"\n===== Stock Research: {results.get('stock_code')} =====", file=out_file
        )

        # Display battle results
        battle_result = results.get("battle_result", {})
        final_decision = battle_result.get("final_decision", "Unknown")
        vote_count = battle_result.get("vote_count", {})
        if final_decision != "Unknown":
            print(
                f"\nFinal Decision: {final_decision} "
                f"(Bullish: {vote_count.get('bullish', 0)}, "
                f"Bearish: {vote_count.get('bearish', 0)})",
                file=out_file,
            )

        # Display research results
        report = results.get("report", "")
        if isinstance(report, str):
            print("\nResearch Report:", file=out_file)
            print(report, file=out_file)

        # Display battle highlights
        if battle_result.get("battle_highlights"):
            print("\nKey Battle Points:", file=out_file)
            for highlight in battle_result["battle_highlights"]:
                print(
                    f"{highlight.get('agent', '')}: {highlight.get('point', '')}",
                    file=out_file,
                )

    finally:
        if output_file:
            out_file.close()
            logger.info(f"Results saved to {output_file}")


async def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="FinGenius Stock Research")
    parser.add_argument("stock_code", help="Stock code to research (e.g., AAPL, MSFT)")
    parser.add_argument(
        "-f",
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument("-o", "--output", help="Save results to file")
    parser.add_argument(
        "--tts", action="store_true", help="Enable text-to-speech for the final result"
    )

    args = parser.parse_args()

    try:
        results = await run_stock_pipeline(args.stock_code)
        display_results(results, args.format, args.output)

        # 如果启用了TTS选项，播报结果
        if args.tts:
            # 确保results目录存在
            import os

            os.makedirs("results", exist_ok=True)
            await announce_result_with_tts(results)

    except KeyboardInterrupt:
        logger.info("Research interrupted")
        return 1
    except Exception as e:
        logger.error(f"Error during research: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
