#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
from typing import Any, Dict

from src.environment.battle import BattleEnvironment
from src.environment.research import ResearchEnvironment
from src.logger import logger


async def run_stock_pipeline(stock_code: str) -> Dict[str, Any]:
    """Research a stock using the agent team and run the battle."""
    logger.info(f"Researching stock {stock_code}...")

    # Initialize environments
    research_env = await ResearchEnvironment.create()
    battle_env = await BattleEnvironment.create()

    try:
        # Run stock research
        research_result = await research_env.run(stock_code)
        logger.info("\n=== Research Complete! Starting Battle ===\n")

        # Register agents for battle
        agent_names = [
            "sentiment_agent",
            "risk_control_agent",
            "market_maker_agent",
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

        # Combine results
        final_result = {**research_result, "battle_result": battle_result}
        logger.info("\n=== Battle Complete! ===\n")

        return final_result
    finally:
        await research_env.cleanup()
        await battle_env.cleanup()


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

    args = parser.parse_args()

    try:
        results = await run_stock_pipeline(args.stock_code)
        display_results(results, args.format, args.output)
    except KeyboardInterrupt:
        logger.info("Research interrupted")
        return 1
    except Exception as e:
        logger.error(f"Error during research: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
