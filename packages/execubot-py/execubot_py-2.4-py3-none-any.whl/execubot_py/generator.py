# Copyright (C) 2025, Florent Gallaire <fgallaire@gmail.com>
# Copyright (C) 2025, Célia Piquet <cepiquet@proton.me>

"""Module providing the Level class and its convenient functions."""

import json
from .solver import Execubot, Grid, extractor


class Level(Execubot):
    """JSON level generator."""
    difficulties = [("not", 0.25), (" or ", 0.25), ("and", 0.25),
                    ("if", 1), ("elif", 2), ("else", 4),
                    ("while", 10), ("for", 20), ("def", 40)]

    def __init__(self, code: str, grid: Grid, row: int, col: int, lang: str,
                 level_id: int, message: str, author: str):
        super().__init__(code, grid, row, col, lang)
        self.row = row
        self.col = col
        self.lang = lang
        self.level_id = level_id
        self.message = message
        self.author = author

    @classmethod
    def tags(cls, code: str) -> list[str]:
        """Return the level tags."""
        res = []
        tags_available = [tag for tag, diff in cls.difficulties]
        for keyword in tags_available[::-1]:
            if keyword == "if" and ("else" in res or "elif" in res):
                continue
            if keyword in code:
                res.append(keyword.strip())
        if len(res) == 0:
            return ["instr"]
        return res

    @classmethod
    def difficulty(cls, code: str) -> int:
        """Return the level difficulty."""
        level_diff = 0
        for keyword, diff in cls.difficulties:
            if keyword in code:
                level_diff += diff
        return level_diff

    def solver_js(self) -> list[list[str | int]]:
        """Return the level JavaScript solution."""
        return [list(tuple_) for tuple_ in self.solver()]

    def generator(self) -> str:
        """Return the level JSON code."""
        jsond = {
            "id": self.level_id,
            "answer": self.solver_js(),
            "grid": self.grid,
            "code": self.code,
            "row": self.row,
            "col": self.col,
            "difficulty": self.difficulty(self.code),
            "tags": self.tags(self.code),
        }
        if self.message:
            jsond["message"] = self.message
        if self.author:
            jsond["author"] = self.author
        if self.lang != "en":
            jsond["lang"] = self.lang
        return json.dumps(jsond)


def tags(code: str) -> list[str]:
    """Convenient interface to the tags @classmethod."""
    return Level.tags(code)


def difficulty(code: str) -> int:
    """Convenient interface to the difficulty @classmethod."""
    return Level.difficulty(code)


def generator(code: str, grid: Grid, row: int = 0, col: int = 0, lang: str = "en",
              level_id: int = 0, message: str = '', author: str = '') -> str:
    """Convenient interface to the generator method."""
    return Level(code, grid, row, col, lang, level_id, message, author).generator()


def generate(level: str) -> str:
    """Convenient generate function."""
    return generator(**extractor(level))
