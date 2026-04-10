import sys
import os
import asyncio
import nest_asyncio

sys.path.insert(0, '/usr/lib/python3.12')
nest_asyncio.apply()

if __name__ == "__main__":
    from src.bot import main
    asyncio.run(main())