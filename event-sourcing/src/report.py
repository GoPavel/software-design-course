import argparse
import asyncio
import logging
import random
import sys
from datetime import datetime
from typing import Type

import schematics

logger = logging.getLogger("report")


async def main(args):
    pass


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    parser = argparse.ArgumentParser(description="Statistic report client")
    subparsers = parser.add_subparsers(dest='command', help="sub-command help")



    asyncio.run(main(parser.parse_args()))

# TODO:
#   1. make model for report in mongo
#   2. when we run module it aggregate new inforamation,
#                            add to current in mongo
#                            show short report in soncole