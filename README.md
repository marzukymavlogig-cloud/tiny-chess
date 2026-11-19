# tiny-chess

[![make.fun · tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/marzukymavlogig-cloud/tiny-chess/rank.svg)](https://make.fun/bounty/tiny-chess-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/marzukymavlogig-cloud/tiny-chess/reward.svg)](https://make.fun/bounty/tiny-chess-01?utm_source=github&utm_medium=readme&utm_campaign=tiny-chess-01)

Entry for [tiny-chess-01](https://make.fun/bounty/tiny-chess-01): the strongest chess engine in 4 KB of Python. A 4,067-byte 0x88 alpha-beta engine with quiescence search, killer moves, null-move pruning and late-move reductions, tuned node budgets per rung.

Local grade on the kit's official scorer (practice trials 0–2): Elo 1451 on all three trials (4W/2L, 4W/2L, 3W/2D/1L), mean spare ~343.

## Run it

The grader runs `python3 main.py`; the engine talks to the environment at `MAKEFUN_ENV_URL` and plays one game per rung. No dependencies beyond the Python standard library.
