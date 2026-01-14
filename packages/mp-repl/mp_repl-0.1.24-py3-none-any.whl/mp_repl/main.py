#!/usr/bin/env python3
"""mp-repl 入口"""
import asyncio
import sys

def main():
    from mp_repl.repl import Repl
    repl = Repl()
    try:
        asyncio.run(repl.run())
    except KeyboardInterrupt:
        print("\nBye!")
        sys.exit(0)

if __name__ == "__main__":
    main()
