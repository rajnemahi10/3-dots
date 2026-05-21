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

## Board Notation

Use compact notation tokens in examples/tests:

- . = empty
- X = unplayable square (expanded border notation)
- r = red single-step
- R = red long-range
- g = green single-step
- G = green long-range
- J = joker (expanded border notation)

Example 4x4 row format:

. R g .

Expanded 4x4 with border notation:

X X J X J X
J . R g . X
X r . . . J
J . . . g X
X . r G . J
X J X J X X

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

Each size uses one canonical starting board notation.

## Run

From the repository root:

python -m modular_gui.main

## Tests

From the repository root:

python -m unittest discover -s modular_gui/tests -p "test_*.py"
