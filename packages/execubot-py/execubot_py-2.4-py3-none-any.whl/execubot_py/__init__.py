# Copyright (C) 2025, Florent Gallaire <fgallaire@gmail.com>

"""
Package providing the Execubot project Python code.
https://execubot.fr
"""

from .solver import solve, extractor, stdgrid
from .generator import generate, tags, difficulty

__all__ = ["solve", "extractor", "stdgrid", "generate", "tags", "difficulty"]
