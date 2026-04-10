import sys
import os

# Fix for Python 3.12/3.14 broken stdlib
sys.path.insert(0, '/usr/lib/python3.12')

from src.bot import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())