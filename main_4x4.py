import argparse
import random
import tkinter as tk
from tkinter import messagebox

from engine_4x4 import (
    check_win,
    config,
    create_initial_board,
    is_joker,
    is_long_range_piece,
    is_player_piece,
)

from visuals import draw_game

from simulate_4x4 import (
    choose_heuristic_move,
    choose_minimax_move,
    choose_monte_carlo_move,
)

BOARD_PIXELS = 600
MARGIN = 80

PLAYER_COLORS = {
    1: "Red",
    2: "Green",
}


def generate_moves(board, row, col):

    moves = []

    directions = [
        (-1,0),
        (1,0),
        (0,-1),
        (0,1),
        (-1,-1),
        (-1,1),
        (1,-1),
        (1,1),
    ]

    board_size = len(board)

    max_step = 2 if is_long_range_piece(board[row][col]) else 1

    for dr, dc in directions:

        for step in range(1, max_step + 1):

            nr = row + dr * step
            nc = col + dc * step

            if 0 <= nr < board_size and 0 <= nc < board_size:

                if board[nr][nc] == 0:
                    moves.append((nr, nc))

    return moves


def get_all_moves(board, player):

    all_moves = []

    size = len(board)

    for r in range(size):
        for c in range(size):

            if is_player_piece(board[r][c], player):

                moves = generate_moves(board, r, c)

                for move in moves:
                    all_moves.append(((r, c), move))

    return all_moves


def choose_ai_move(board, player, strategy):

    all_moves = get_all_moves(board, player)

    if not all_moves:
        return None

    rng = random.Random()

    if strategy == "random":
        return rng.choice(all_moves)

    if strategy == "heuristic":

        return choose_heuristic_move(
            board,
            player,
            all_moves,
            rng,
            set(),
        )

    if strategy == "minimax":

        return choose_minimax_move(
            board,
            player,
            all_moves,
            rng,
            3,
        )

    if strategy == "monte_carlo":

        return choose_monte_carlo_move(
            board,
            player,
            all_moves,
            rng,
            24,
            8,
        )

    return rng.choice(all_moves)


def run_game(
    layout,
    auto_play=False,
    player1_strategy="monte_carlo",
    player2_strategy="monte_carlo",
):

    board = create_initial_board(layout)

    size = len(board)

    cell = BOARD_PIXELS // size

    canvas_size = BOARD_PIXELS + 2 * MARGIN

    selected = None
    legal_moves = []
    current_player = 1

    root = tk.Tk()

    root.title(f"Pattern Game ({layout})")

    root.resizable(False, False)

    canvas = tk.Canvas(
        root,
        width=canvas_size,
        height=canvas_size,
        bg="white",
        highlightthickness=0,
    )

    canvas.pack()

    def redraw():

        draw_game(
            canvas,
            board,
            selected,
            legal_moves,
            cell,
            origin_x=MARGIN,
            origin_y=MARGIN,
        )

    def advance_turn():

        nonlocal current_player

        current_player = 2 if current_player == 1 else 1

    def ai_step():

        nonlocal current_player

        strategy = (
            player1_strategy
            if current_player == 1
            else player2_strategy
        )

        move = choose_ai_move(
            board,
            current_player,
            strategy,
        )

        if move is None:

            messagebox.showinfo(
                "Simulation",
                "Draw: no legal moves."
            )

            return

        (sr, sc), (tr, tc) = move

        board[tr][tc] = board[sr][sc]
        board[sr][sc] = 0

        redraw()

        won = any(
            check_win(board, current_player, pattern_name)
            for pattern_name in config.player_patterns[current_player]
        )

        if won:

            messagebox.showinfo(
                "Simulation",
                f"{PLAYER_COLORS[current_player]} wins!"
            )

            return

        advance_turn()

        root.after(250, ai_step)

    def handle_click(event):

        nonlocal selected
        nonlocal legal_moves
        nonlocal current_player

        if auto_play:
            return

        row = (event.y - MARGIN) // cell
        col = (event.x - MARGIN) // cell

        if not (0 <= row < size and 0 <= col < size):
            return

        if selected is None:

            if is_player_piece(board[row][col], current_player):

                if not is_joker(board[row][col]):

                    selected = (row, col)

                    legal_moves = generate_moves(board, row, col)

        else:

            if (row, col) in legal_moves:

                sr, sc = selected

                board[row][col] = board[sr][sc]
                board[sr][sc] = 0

                redraw()

                won = any(
                    check_win(board, current_player, pattern_name)
                    for pattern_name in config.player_patterns[current_player]
                )

                if won:

                    messagebox.showinfo(
                        "Pattern Game",
                        f"{PLAYER_COLORS[current_player]} wins!"
                    )

                    root.destroy()
                    return

                advance_turn()

            selected = None
            legal_moves = []

        redraw()

    canvas.bind("<Button-1>", handle_click)

    redraw()

    if auto_play:
        root.after(500, ai_step)

    root.mainloop()


def main():

    parser = argparse.ArgumentParser(description="Pattern Game")

    parser.add_argument(
        "--layout",
        choices=[
            "crossfire_4x4",
            "rotational_4x4",
            "center_warfare_5x5",
            "dual_pressure_5x5",
            "competitive_6x6",
        ],
        default="crossfire_4x4",
    )

    parser.add_argument(
        "--simulate",
        action="store_true",
    )

    parser.add_argument(
        "--player-1-strategy",
        choices=[
            "random",
            "heuristic",
            "minimax",
            "monte_carlo",
        ],
        default="monte_carlo",
    )

    parser.add_argument(
        "--player-2-strategy",
        choices=[
            "random",
            "heuristic",
            "minimax",
            "monte_carlo",
        ],
        default="monte_carlo",
    )

    args = parser.parse_args()

    run_game(
        args.layout,
        auto_play=args.simulate,
        player1_strategy=args.player_1_strategy,
        player2_strategy=args.player_2_strategy,
    )


if __name__ == "__main__":
    main()