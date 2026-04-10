#!/usr/bin/env python3
import sys

if __name__ == "__main__":
    from src.bot import main
    import asyncio
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()