import tkinter as tk
from tkinter import messagebox
import argparse

from engine import check_win, config, create_initial_board, size
from visuals import draw_game


WIDTH = 600
HEIGHT = 600
CELL = WIDTH // size


def generate_moves(board, row, col):
    moves = []
    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]

    board_size = len(board)

    for dr, dc in directions:
        nr = row + dr
        nc = col + dc

        if 0 <= nr < board_size and 0 <= nc < board_size and board[nr][nc] == 0:
            moves.append((nr, nc))

    return moves


def redraw():
    draw_game(canvas, board, selected, legal_moves, CELL)


def advance_turn():
    global current_player
    current_player = 2 if current_player == 1 else 1


def handle_click(event):
    global selected, legal_moves

    row = event.y // CELL
    col = event.x // CELL

    if not (0 <= row < size and 0 <= col < size):
        return

    if selected is None:
        if board[row][col] == current_player:
            selected = (row, col)
            legal_moves = generate_moves(board, row, col)
    else:
        if (row, col) in legal_moves:
            sr, sc = selected
            board[row][col] = current_player
            board[sr][sc] = 0

            won = any(
                check_win(board, current_player, pattern_name)
                for pattern_name in config.player_patterns[current_player]
            )
            if won:
                redraw()
                messagebox.showinfo("Pattern Game", f"Player {current_player} wins!")
                root.destroy()
                return

            advance_turn()

        selected = None
        legal_moves = []

    redraw()


root = tk.Tk()
parser = argparse.ArgumentParser(description="Play the 3x3 Pattern Game.")
parser.add_argument("--layout", choices=["corners", "staggered"], default="corners")
args = parser.parse_args()

board = create_initial_board(args.layout)
selected = None
legal_moves = []
current_player = 1

root.title(f"Pattern Game 3x3 ({args.layout})")
root.resizable(False, False)

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="white", highlightthickness=0)
canvas.pack()
canvas.bind("<Button-1>", handle_click)

redraw()
root.mainloop()
