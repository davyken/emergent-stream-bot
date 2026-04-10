#!/usr/bin/env python3

if __name__ == "__main__":
    from src.bot import main
    import asyncio
    
    async def run():
        await main()
    
    with asyncio.Runner() as runner:
        runner.run(run())