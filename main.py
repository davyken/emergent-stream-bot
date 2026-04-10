import sys
import os

sys.path.insert(0, '/usr/lib/python3.12')

from src.bot import main
import asyncio

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    finally:
        loop.close()