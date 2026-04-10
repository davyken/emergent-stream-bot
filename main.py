import sys
import os
import threading

sys.path.insert(0, '/usr/lib/python3.12')

from src.bot import main
import asyncio

def run_bot():
    asyncio.run(main())

if __name__ == "__main__":
    t = threading.Thread(target=run_bot, daemon=True)
    t.start()
    t.join()