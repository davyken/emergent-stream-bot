#!/usr/bin/env python3
import asyncio
import sys
import os

# Ensure the root directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from src.bot import main
    asyncio.run(main())