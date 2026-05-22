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

    if board_size not in (4, 5, 6, 7):

        raise ValueError(
            f"Unsupported board size: {board_size}"
        )

    return engine.create_initial_board(
        board_size
    )


def board_to_notation_rows(board):

    rows = []

    for row in board:

        tokens = []

        for cell in row:

            if cell not in ALL_BOARD_TOKENS:

                raise ValueError(
                    f"Unknown board cell: {cell}"
                )

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

    piece = board[row][col]

    if engine.is_long_range_piece(piece):
        allowed_steps = [2]
    else:
        allowed_steps = [1]

    board_size = len(board)

    for dr, dc in directions:

        for step in allowed_steps:

            nr = row + dr * step
            nc = col + dc * step

            if (

                0 <= nr < board_size
                and 0 <= nc < board_size
                and board[nr][nc]
                == engine.EMPTY
            ):
                moves.append((nr, nc))

    return moves


def get_all_moves(board, player):

    all_moves = []

    size = len(board)

    for row in range(size):

        for col in range(size):

            cell = board[row][col]

            if (
                not engine.is_player_piece(
                    cell,
                    player,
                )
                or engine.is_joker(cell)
            ):
                continue

            for next_row, next_col in generate_moves(
                board,
                row,
                col,
            ):

                all_moves.append(

                    (
                        (row, col),
                        (next_row, next_col),
                    )
                )

    return all_moves


def apply_move(board, move):

    (src_row, src_col), (
        dst_row,
        dst_col,
    ) = move

    board[dst_row][dst_col] = (
        board[src_row][src_col]
    )

    board[src_row][src_col] = engine.EMPTY


def _pattern_is_win(
    board,
    player,
    pattern,
):

    opponent = (
        2 if player == 1 else 1
    )

    start_row, start_col = pattern[0]
    middle_row, middle_col = pattern[1]
    end_row, end_col = pattern[2]

    start_cell = engine.get_cell(
        board,
        start_row,
        start_col,
    )

    middle_cell = engine.get_cell(
        board,
        middle_row,
        middle_col,
    )

    end_cell = engine.get_cell(
        board,
        end_row,
        end_col,
    )

    return (

        start_cell is not None
        and middle_cell is not None
        and end_cell is not None

        and engine.endpoint_matches_player(
            start_cell,
            player,
        )

        and engine.owner_of(
            middle_cell
        ) == opponent

        and engine.endpoint_matches_player(
            end_cell,
            player,
        )
    )


def wins_including_cell(
    board,
    player,
    moved_cell,
):

    engine.ensure_patterns_for_board(
        board
    )

    counts = {}

    all_patterns = (

        list(engine.PATTERNS.keys())
        + list(engine.SHAPE_PATTERNS.keys())
    )

    for pattern_name in all_patterns:

        counts[pattern_name] = 0

        # LINE PATTERNS
        if pattern_name in engine.PATTERNS:

            pattern_list = (
                engine.PATTERNS[
                    pattern_name
                ]
            )

            for pattern in pattern_list:

                if (
                    moved_cell is not None
                    and moved_cell not in pattern
                ):
                    continue

                if _pattern_is_win(
                    board,
                    player,
                    pattern,
                ):
                    counts[
                        pattern_name
                    ] += 1

        # SHAPE PATTERNS
        else:

            for offsets in (
                engine.SHAPE_PATTERNS[
                    pattern_name
                ]
            ):

                size = len(board)

                max_r = max(
                    dr
                    for dr, dc
                    in offsets
                )

                max_c = max(
                    dc
                    for dr, dc
                    in offsets
                )

                for row in range(
                    size - max_r
                ):

                    for col in range(
                        size - max_c
                    ):

                        cells = []

                        for dr, dc in offsets:

                            cells.append(
                                (
                                    row + dr,
                                    col + dc,
                                )
                            )

                        if (
                            moved_cell
                            is not None
                            and moved_cell
                            not in cells
                        ):
                            continue

                        if engine.check_shape_win(
                            board,
                            player,
                            offsets,
                        ):
                            counts[
                                pattern_name
                            ] += 1

    return counts


def evaluate_group(
    group_config,
    counts,
):

    patterns = group_config[
        "patterns"
    ]

    enabled_results = []

    for pattern_name, needed_count in (
        patterns.items()
    ):

        if needed_count <= 0:
            continue

        actual_count = counts.get(
            pattern_name,
            0,
        )

        enabled_results.append(

            actual_count
            >= needed_count
        )

    # ignored if empty
    if not enabled_results:
        return True

    if group_config["mode"] == "and":

        return all(enabled_results)

    return any(enabled_results)


def player_has_win(board, player):

    counts = wins_including_cell(
        board,
        player,
        None,
    )

    groups = (
        engine.config
        .player_pattern_groups[player]
    )

    return all(

        evaluate_group(
            group,
            counts,
        )

        for group in groups.values()
    )


def resolve_move_outcome(
    board,
    mover,
    moved_cell,
):

    opponent = (
        2 if mover == 1 else 1
    )

    mover_counts = wins_including_cell(
        board,
        mover,
        moved_cell,
    )

    opponent_counts = wins_including_cell(
        board,
        opponent,
        moved_cell,
    )

    mover_groups = (
        engine.config
        .player_pattern_groups[mover]
    )

    opponent_groups = (
        engine.config
        .player_pattern_groups[opponent]
    )

    mover_success = all(

        evaluate_group(
            group,
            mover_counts,
        )

        for group
        in mover_groups.values()
    )

    opponent_success = all(

        evaluate_group(
            group,
            opponent_counts,
        )

        for group
        in opponent_groups.values()
    )

    if (
        mover_success
        and opponent_success
    ):

        return {

            "status": "draw",
            "winner": 0,
            "reason": "dual_pattern",
        }

    if opponent_success:

        return {

            "status": "win",
            "winner": opponent,
            "reason": "self_sabotage",
        }

    if mover_success:

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