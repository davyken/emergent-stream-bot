#!/usr/bin/env python3
import sys
import os

# Patch sys.path to ensure stdlib is found first
stdlib = '/usr/lib/python3.12'
if stdlib not in sys.path:
    sys.path.insert(0, stdlib)

# Pre-import broken modules before any other imports
import email.parser
import http.client
import urllib.request

# Now run the bot
if __name__ == "__main__":
    from src.bot import main
    import asyncio
    asyncio.run(main())