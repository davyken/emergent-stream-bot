#!/usr/bin/env python3
import asyncio
import nest_asyncio
nest_asyncio.apply()

if __name__ == "__main__":
    from src.bot import main
    asyncio.run(main())