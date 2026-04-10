import sys
import os

sys.path.insert(0, '/usr/lib/python3.12')

from src.bot import main
import asyncio

async def run():
    await main()

if __name__ == "__main__":
    with asyncio.Runner() as runner:
        runner.run(run())