import modular_gui.engine as engine


ALL_BOARD_TOKENS = {
    engine.EMPTY,
    engine.RED_SINGLE,
    engine.GREEN_SINGLE,
    engine.RED_LONG,
    engine.GREEN_LONG,
    engine.JOKER,
    engine.BLOCKED,
}


def create_board(board_size):
    if board_size not in (4, 5, 6):
        raise ValueError(f"Unsupported board size: {board_size}")

    return engine.create_initial_board(board_size)


def board_to_notation_rows(board):
    rows = []

    for row in board:
        tokens = []

        for cell in row:
            if cell not in ALL_BOARD_TOKENS:
                raise ValueError(f"Unknown board cell: {cell}")

            tokens.append(cell)

        rows.append(" ".join(tokens))

    return rows


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

    max_step = 2 if engine.is_long_range_piece(board[row][col]) else 1
    board_size = len(board)

    for dr, dc in directions:
        for step in range(1, max_step + 1):
            nr = row + dr * step
            nc = col + dc * step

            if (
                0 <= nr < board_size
                and 0 <= nc < board_size
                and board[nr][nc] == engine.EMPTY
            ):
                moves.append((nr, nc))

    return moves


def get_all_moves(board, player):
    all_moves = []
    size = len(board)

    for row in range(size):
        for col in range(size):
            cell = board[row][col]

            if not engine.is_player_piece(cell, player) or engine.is_joker(cell):
                continue

            for next_row, next_col in generate_moves(board, row, col):
                all_moves.append(((row, col), (next_row, next_col)))

    return all_moves


def apply_move(board, move):
    (src_row, src_col), (dst_row, dst_col) = move
    board[dst_row][dst_col] = board[src_row][src_col]
    board[src_row][src_col] = engine.EMPTY


def player_has_win(board, player):
    return any(
        engine.check_win(board, player, pattern_name)
        for pattern_name in engine.config.player_patterns[player]
    )


def _pattern_is_win(board, player, pattern):
    opponent = 2 if player == 1 else 1

    start_row, start_col = pattern[0]
    middle_row, middle_col = pattern[1]
    end_row, end_col = pattern[2]

    start_cell = engine.get_cell(board, start_row, start_col)
    middle_cell = engine.get_cell(board, middle_row, middle_col)
    end_cell = engine.get_cell(board, end_row, end_col)

    return (
        start_cell is not None
        and middle_cell is not None
        and end_cell is not None
        and engine.endpoint_matches_player(start_cell, player)
        and engine.owner_of(middle_cell) == opponent
        and engine.endpoint_matches_player(end_cell, player)
    )


def wins_including_cell(board, player, moved_cell):
    engine.ensure_patterns_for_board(board)

    wins = []

    for pattern_name in engine.config.player_patterns[player]:
        for pattern in engine.PATTERNS[pattern_name]:
            if moved_cell not in pattern:
                continue

            if _pattern_is_win(board, player, pattern):
                wins.append((pattern_name, pattern))

    return wins


def resolve_move_outcome(board, mover, moved_cell):
    opponent = 2 if mover == 1 else 1

    mover_wins = wins_including_cell(board, mover, moved_cell)
    opponent_wins = wins_including_cell(board, opponent, moved_cell)

    if mover_wins and opponent_wins:
        return {
            "status": "draw",
            "winner": 0,
            "reason": "dual_pattern",
        }

    if opponent_wins:
        return {
            "status": "win",
            "winner": opponent,
            "reason": "self_sabotage",
        }

    if mover_wins:
        return {
            "status": "win",
            "winner": mover,
            "reason": "pattern",
        }

    return {
        "status": "none",
        "winner": None,
        "reason": None,
    }
