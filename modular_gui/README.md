# Modular GUI

This folder contains a modular Tkinter game app that reuses the existing project logic.

## Files

- main.py: Tkinter GUI entry point with dropdowns for P1, P2, and board size.
- engine.py: Local copy of engine rules, layouts, and joker/pattern logic.
- board.py: Shared board helpers (create board, generate/list/apply moves, win check).
- visuals.py: Local copy of Tkinter drawing helpers.
- ai_random.py: Random move strategy.
- ai_heuristic.py: Copied heuristic strategy logic.
- ai_minimax.py: Copied minimax strategy logic.
- ai_monte_carlo.py: Copied Monte Carlo strategy logic.
- __init__.py: Package marker.

This package is self-contained: it does not import engine or AI logic from the project root.

## Strategy Values

Use one of these values for each player in the GUI:

- human
- random
- heuristic
- minimax
- monte_carlo

## Board Size Values

- 4
- 5
- 6

Board size maps to existing layouts from engine_4x4.py:

- 4 -> crossfire_4x4
- 5 -> center_warfare_5x5
- 6 -> competitive_6x6

## Run

From the repository root:

python -m modular_gui.main
