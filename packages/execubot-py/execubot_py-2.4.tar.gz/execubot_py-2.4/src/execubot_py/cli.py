# Copyright (C) 2025, Florent Gallaire <fgallaire@gmail.com>

"""Execubot.

Usage: execubot-cli (extractor | solver | generator | grid | tags | difficulty) <FILE>...

Options:
  -h --help     Show this screen.
  -v --version  Show version.
"""

import os
from docopt import docopt
from natsort import natsorted
from . import extractor, solve, stdgrid, generate, difficulty, tags

def main() -> int:
    """Execubot CLI"""
    args = docopt(__doc__, version='Execubot 2.4')
    natsorted_files = natsorted(args['<FILE>'])
    for level in natsorted_files:
        basename = os.path.basename(level)
        if args['extractor']:
            print(basename, extractor(level), sep=": ")
        elif args['solver']:
            print(basename, solve(level), sep=": ")
        elif args['generator']:
            print(basename, generate(level), sep=": ")
        elif args['grid']:
            print(basename, stdgrid(extractor(level)["grid"]), sep=": ")
        elif args['tags']:
            print(basename, tags(extractor(level)["code"]), sep=": ")
        elif args['difficulty']:
            print(basename, difficulty(extractor(level)["code"]), sep=": ")
    return 0
