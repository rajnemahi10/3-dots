from modular_gui.engine import (
    check_win,
    config,
    create_initial_board,
    is_joker,
    is_long_range_piece,
    is_player_piece,
)


SIZE_TO_LAYOUT = {
    4: "crossfire_4x4",
    5: "center_warfare_5x5",
    6: "competitive_6x6",
}


def create_board(board_size):
    layout = SIZE_TO_LAYOUT.get(board_size)

    if layout is None:
        raise ValueError(f"Unsupported board size: {board_size}")

    return create_initial_board(layout)


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

    max_step = 2 if is_long_range_piece(board[row][col]) else 1
    board_size = len(board)

    for dr, dc in directions:
        for step in range(1, max_step + 1):
            nr = row + dr * step
            nc = col + dc * step

            if 0 <= nr < board_size and 0 <= nc < board_size and board[nr][nc] == 0:
                moves.append((nr, nc))

    return moves


def get_all_moves(board, player):
    all_moves = []
    size = len(board)

    for row in range(size):
        for col in range(size):
            cell = board[row][col]

            if not is_player_piece(cell, player) or is_joker(cell):
                continue

            for next_row, next_col in generate_moves(board, row, col):
                all_moves.append(((row, col), (next_row, next_col)))

    return all_moves


def apply_move(board, move):
    (src_row, src_col), (dst_row, dst_col) = move
    board[dst_row][dst_col] = board[src_row][src_col]
    board[src_row][src_col] = 0


def player_has_win(board, player):
    return any(
        check_win(board, player, pattern_name)
        for pattern_name in config.player_patterns[player]
    )
