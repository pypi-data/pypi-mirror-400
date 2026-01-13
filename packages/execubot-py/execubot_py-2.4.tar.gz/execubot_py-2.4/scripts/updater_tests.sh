#! /usr/bin/env bash
#
# Copyright (C) 2025, Florent Gallaire <fgallaire@gmail.com>
# Copyright (C) 2025, Célia Piquet <cepiquet@proton.me>

EXEC_PATH=$(dirname "$0")

if [ $# -eq 0 ]
then
	echo "Usage: updater_tests.sh [FILE]..."
else
	execubot-cli extractor $* >> "$EXEC_PATH"/../tests/extractor.out
	execubot-cli solver $* >> "$EXEC_PATH"/../tests/solver.out
	execubot-cli grid $* >> "$EXEC_PATH"/../tests/grid.out
	execubot-cli generator $* >> "$EXEC_PATH"/../tests/generator.out
	execubot-cli difficulty $* >> "$EXEC_PATH"/../tests/difficulty.out
	execubot-cli tags $* >> "$EXEC_PATH"/../tests/tags.out
fi
