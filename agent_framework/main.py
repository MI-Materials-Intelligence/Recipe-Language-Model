import argparse
import asyncio
import warnings
import logging
import sys

# 在导入任何其他模块之前，先配置根日志记录器，屏蔽所有 INFO 级别的日志
logging.basicConfig(level=logging.ERROR, stream=sys.stderr, format='%(levelname)s: %(message)s')

# 屏蔽 Pydantic V2 警告
warnings.filterwarnings("ignore", message=".*underscore_attrs_are_private.*")

# 强制降低特定库的日志级别
logging.getLogger("browser_use").setLevel(logging.CRITICAL)
logging.getLogger("root").setLevel(logging.CRITICAL)  # browser_use 的 telemetry
logging.getLogger("sandbox").setLevel(logging.CRITICAL)  # daytona sandbox

from app.agent.MIAgent import MIAgent
from app.logger import logger


async def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Run Manus agent with a prompt")
    parser.add_argument(
        "--prompt", type=str, required=False, help="Input prompt for the agent"
    )
    args = parser.parse_args()

    # Create and initialize Manus agent
    agent = await MIAgent.create()
    try:
        # Use command line prompt if provided, otherwise ask for input
        prompt = args.prompt if args.prompt else input("Enter your prompt: ")
        if not prompt.strip():
            logger.warning("Empty prompt provided.")
            return

        logger.warning("Processing your request...")
        await agent.run(prompt)
        logger.info("Request processing completed.")
    except KeyboardInterrupt:
        logger.warning("Operation interrupted.")
    finally:
        # Ensure agent resources are cleaned up before exiting
        await agent.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
