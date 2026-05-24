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

            if not (
                0 <= nr < board_size
                and 0 <= nc < board_size
            ):
                continue

            if step == 2:

                middle_row = row + dr
                middle_col = col + dc

                if (
                    board[middle_row][middle_col]
                    != engine.EMPTY
                ):
                    continue

            if (
                board[nr][nc]
                == engine.EMPTY
            ):

                moves.append(
                    (nr, nc)
                )

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


def _shape_is_win(
    board,
    player,
    shape_name,
):

    size = len(board)

    opponent = (
        2 if player == 1 else 1
    )

    matches = []

    def endpoint(cell):

        return engine.endpoint_matches_player(
            cell,
            player,
        )

    def middle(cell):

        return (
            engine.owner_of(cell)
            == opponent
        )

    for r in range(size):

        for c in range(size):

            try:

                if shape_name == "triangle_up":

                    a = board[r + 1][c]
                    b = board[r][c + 1]
                    d = board[r + 1][c + 2]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r + 1, c),
                                (r, c + 1),
                                (r + 1, c + 2),
                            ]
                        )

                elif shape_name == "triangle_down":

                    a = board[r][c]
                    b = board[r + 1][c + 1]
                    d = board[r][c + 2]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r, c),
                                (r + 1, c + 1),
                                (r, c + 2),
                            ]
                        )

                elif shape_name == "triangle_left":

                    a = board[r][c]
                    b = board[r + 1][c + 1]
                    d = board[r + 2][c]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r, c),
                                (r + 1, c + 1),
                                (r + 2, c),
                            ]
                        )

                elif shape_name == "triangle_right":

                    a = board[r][c + 1]
                    b = board[r + 1][c]
                    d = board[r + 2][c + 1]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r, c + 1),
                                (r + 1, c),
                                (r + 2, c + 1),
                            ]
                        )

                elif shape_name == "corner_ul":

                    a = board[r][c + 1]
                    b = board[r][c]
                    d = board[r + 1][c]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r, c + 1),
                                (r, c),
                                (r + 1, c),
                            ]
                        )

                elif shape_name == "corner_ur":

                    a = board[r][c]
                    b = board[r][c + 1]
                    d = board[r + 1][c + 1]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r, c),
                                (r, c + 1),
                                (r + 1, c + 1),
                            ]
                        )

                elif shape_name == "corner_dl":

                    a = board[r][c]
                    b = board[r + 1][c]
                    d = board[r + 1][c + 1]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r, c),
                                (r + 1, c),
                                (r + 1, c + 1),
                            ]
                        )

                elif shape_name == "corner_dr":

                    a = board[r][c + 1]
                    b = board[r + 1][c + 1]
                    d = board[r + 1][c]

                    if (
                        endpoint(a)
                        and middle(b)
                        and endpoint(d)
                    ):

                        matches.append(
                            [
                                (r, c + 1),
                                (r + 1, c + 1),
                                (r + 1, c),
                            ]
                        )

            except IndexError:

                pass

    return matches

def get_all_matching_patterns(
    board,
    player,
):

    engine.ensure_patterns_for_board(
        board
    )

    matches = {}

    all_patterns = (

        list(engine.PATTERNS.keys())
        + list(engine.SHAPE_PATTERNS.keys())
    )

    for pattern_name in all_patterns:

        matches[pattern_name] = []

        if pattern_name in engine.PATTERNS:

            pattern_list = (
                engine.PATTERNS[
                    pattern_name
                ]
            )

            for pattern in pattern_list:

                if _pattern_is_win(
                    board,
                    player,
                    pattern,
                ):

                    matches[
                        pattern_name
                    ].append(pattern)

        else:

            found = _shape_is_win(
                board,
                player,
                pattern_name,
            )

            matches[
                pattern_name
            ].extend(found)

    return matches


def wins_including_cell(
    board,
    player,
    moved_cell,
):

    matches = get_all_matching_patterns(
        board,
        player,
    )

    counts = {}

    for pattern_name, pattern_matches in (
        matches.items()
    ):

        if moved_cell is None:

            counts[
                pattern_name
            ] = len(pattern_matches)

            continue

        filtered = []

        for pattern in pattern_matches:

            if moved_cell in pattern:
                filtered.append(pattern)

        counts[
            pattern_name
        ] = len(filtered)

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

    if not enabled_results:
        return True

    if group_config["mode"] == "and":

        return all(enabled_results)

    return any(enabled_results)


def get_required_highlight_patterns(
    board,
    player,
):

    matches = get_all_matching_patterns(
        board,
        player,
    )

    groups = (
        engine.config
        .player_pattern_groups[player]
    )

    highlighted = []

    for group in groups.values():

        patterns = group["patterns"]

        for pattern_name, needed in (
            patterns.items()
        ):

            if needed <= 0:
                continue

            pattern_matches = matches.get(
                pattern_name,
                [],
            )

            if len(pattern_matches) >= needed:

                highlighted.extend(
                    pattern_matches[:needed]
                )

    return highlighted


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