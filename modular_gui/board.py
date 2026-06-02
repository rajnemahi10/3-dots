from functools import lru_cache
import random

import modular_gui.engine as engine


ALL_BOARD_TOKENS = {

    engine.EMPTY,
    engine.RED_SINGLE,
    engine.GREEN_SINGLE,
    engine.RED_LONG,
    engine.GREEN_LONG,
    engine.RED_SWIFT,
    engine.GREEN_SWIFT,
    engine.JOKER,
    engine.BLOCKED,
}


SHAPE_ANCHORS_BY_SIZE = {}
ZOBRIST_SEED = 1729
ZOBRIST_TABLES = {}


def freeze_board(board):

    return tuple(
        tuple(row)
        for row in board
    )


def thaw_board(board_key):

    return [
        list(row)
        for row in board_key
    ]


def _transform_coord(
    coord,
    size,
    transform_id,
):
    if coord is None:
        return None

    row, col = coord

    if transform_id == 0:
        return (row, col)
    if transform_id == 1:
        return (col, size - 1 - row)
    if transform_id == 2:
        return (size - 1 - row, size - 1 - col)
    if transform_id == 3:
        return (size - 1 - col, row)
    if transform_id == 4:
        return (row, size - 1 - col)
    if transform_id == 5:
        return (size - 1 - row, col)
    if transform_id == 6:
        return (col, row)

    return (
        size - 1 - col,
        size - 1 - row,
    )


def _transform_move(
    move,
    size,
    transform_id,
):
    if move is None:
        return None

    return (
        _transform_coord(
            move[0],
            size,
            transform_id,
        ),
        _transform_coord(
            move[1],
            size,
            transform_id,
        ),
    )


def _transform_board_key(
    board_key,
    transform_id,
):
    size = len(board_key)
    transformed = [
        [None] * size
        for _ in range(size)
    ]

    for row in range(size):

        for col in range(size):

            next_row, next_col = (
                _transform_coord(
                    (row, col),
                    size,
                    transform_id,
                )
            )

            transformed[next_row][
                next_col
            ] = board_key[row][col]

    return tuple(
        tuple(row)
        for row in transformed
    )


def _zobrist_table(size):
    cached = ZOBRIST_TABLES.get(size)

    if cached is not None:
        return cached

    rng = random.Random(
        ZOBRIST_SEED + size
    )

    tokens = tuple(
        sorted(ALL_BOARD_TOKENS)
    )

    table = {}

    for row in range(size):

        for col in range(size):

            for token in tokens:

                table[
                    (row, col, token)
                ] = rng.getrandbits(64)

    ZOBRIST_TABLES[size] = table

    return table


def zobrist_hash(board):
    board_key = (
        board
        if isinstance(board, tuple)
        else freeze_board(board)
    )

    table = _zobrist_table(
        len(board_key)
    )
    value = 0

    for row, cells in enumerate(board_key):

        for col, cell in enumerate(cells):

            value ^= table[
                (row, col, cell)
            ]

    return value


def canonicalize_board_state(
    board,
    moved_cell=None,
    move=None,
):
    board_key = (
        board
        if isinstance(board, tuple)
        else freeze_board(board)
    )

    size = len(board_key)
    best = None

    for transform_id in range(8):
        transformed_board = (
            _transform_board_key(
                board_key,
                transform_id,
            )
        )
        transformed_cell = (
            _transform_coord(
                moved_cell,
                size,
                transform_id,
            )
        )
        transformed_move = (
            _transform_move(
                move,
                size,
                transform_id,
            )
        )

        candidate = (
            transformed_board,
            transformed_cell,
            transformed_move,
        )

        if best is None or candidate < best:
            best = candidate

    canonical_board, canonical_cell, (
        canonical_move
    ) = best

    return (
        zobrist_hash(canonical_board),
        canonical_board,
        canonical_cell,
        canonical_move,
    )


def canonical_board_cache_key(board):
    zobrist_value, board_key, _cell, _move = (
        canonicalize_board_state(board)
    )

    return (
        zobrist_value,
        board_key,
    )


def canonical_state_cache_key(
    board,
    player=None,
    moved_cell=None,
    move=None,
    extra=(),
):
    zobrist_value, board_key, canonical_cell, canonical_move = (
        canonicalize_board_state(
            board,
            moved_cell=moved_cell,
            move=move,
        )
    )

    if not isinstance(extra, tuple):
        extra = (extra,)

    return (
        zobrist_value,
        board_key,
        player,
        canonical_cell,
        canonical_move,
    ) + extra


def rules_signature():

    signature = []

    for player in sorted(
        engine.config.player_pattern_groups
    ):

        groups = (
            engine.config
            .player_pattern_groups[player]
        )

        player_signature = []

        for group_name in sorted(groups):

            group = groups[group_name]

            player_signature.append(
                (
                    group_name,
                    group["mode"],
                    tuple(
                        sorted(
                            group["patterns"].items()
                        )
                    ),
                )
            )

        signature.append(
            (
                player,
                tuple(player_signature),
            )
        )

    return tuple(signature)


def _shape_specifications():

    return {
        "triangle_up": (
            (1, 0),
            (0, 1),
            (1, 2),
        ),
        "triangle_down": (
            (0, 0),
            (1, 1),
            (0, 2),
        ),
        "triangle_left": (
            (0, 0),
            (1, 1),
            (2, 0),
        ),
        "triangle_right": (
            (0, 1),
            (1, 0),
            (2, 1),
        ),
        "corner_ul": (
            (0, 1),
            (0, 0),
            (1, 0),
        ),
        "corner_ur": (
            (0, 0),
            (0, 1),
            (1, 1),
        ),
        "corner_dl": (
            (0, 0),
            (1, 0),
            (1, 1),
        ),
        "corner_dr": (
            (0, 1),
            (1, 1),
            (1, 0),
        ),

        "octagon_ul": (
            (0,0),
            (0,1),
            (1,2),
        ),

        "octagon_ur": (
            (0,2),
            (0,1),
            (1,0),
        ),

        "octagon_dr": (
            (0,0),
            (1,1),
            (1,2),
        ),

        "octagon_dl": (
            (0,2),
            (1,1),
            (1,0),
        ),
    }


def get_shape_anchors(size):

    cached = SHAPE_ANCHORS_BY_SIZE.get(
        size
    )

    if cached is not None:
        return cached

    anchors = {}

    for shape_name, offsets in (
        _shape_specifications().items()
    ):

        max_row = max(
            row
            for row, _col in offsets
        )

        max_col = max(
            col
            for _row, col in offsets
        )

        shape_anchors = []

        for row in range(
            size - max_row
        ):

            for col in range(
                size - max_col
            ):

                shape_anchors.append(
                    tuple(
                        (
                            row + off_row,
                            col + off_col,
                        )
                        for off_row, off_col in offsets
                    )
                )

        anchors[shape_name] = tuple(
            shape_anchors
        )

    SHAPE_ANCHORS_BY_SIZE[size] = anchors

    return anchors


def clear_caches():

    SHAPE_ANCHORS_BY_SIZE.clear()

    _cached_generate_moves.cache_clear()
    _cached_get_all_moves.cache_clear()
    _cached_get_all_matching_patterns.cache_clear()
    _cached_wins_including_cell.cache_clear()
    _cached_resolve_move_outcome.cache_clear()


def cache_report():

    return {
        "generate_moves": (
            _cached_generate_moves.cache_info()
        ),
        "get_all_moves": (
            _cached_get_all_moves.cache_info()
        ),
        "get_all_matching_patterns": (
            _cached_get_all_matching_patterns
            .cache_info()
        ),
        "wins_including_cell": (
            _cached_wins_including_cell
            .cache_info()
        ),
        "resolve_move_outcome": (
            _cached_resolve_move_outcome
            .cache_info()
        ),
    }


def create_board(board_size):

    if board_size not in (4, 5, 6, 7, 9):

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


@lru_cache(maxsize=32768)
def _cached_generate_moves(
    board_key,
    row,
    col,
):

    board = thaw_board(board_key)

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

    if engine.is_dual_range_piece(piece):
        allowed_steps = [1, 2]
    elif engine.is_long_range_piece(piece):
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

    return tuple(moves)

def generate_moves(board, row, col):

    board_key = freeze_board(board)

    return list(
        _cached_generate_moves(
            board_key,
            row,
            col,
        )
    )


@lru_cache(maxsize=16384)
def _cached_get_all_moves(
    board_key,
    player,
):

    board = thaw_board(board_key)
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

            for next_row, next_col in (
                _cached_generate_moves(
                    board_key,
                    row,
                    col,
                )
            ):

                all_moves.append(
                    (
                        (row, col),
                        (next_row, next_col),
                    )
                )

    return tuple(all_moves)


def get_all_moves(board, player):
    board_key = freeze_board(board)

    return list(
        _cached_get_all_moves(
            board_key,
            player,
        )
    )


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

        and engine.valid_endpoints(
            start_cell,
            end_cell,
            player,
        )

        and engine.owner_of(
            middle_cell
        ) == opponent
    )


def _shape_is_win(
    board,
    player,
    shape_name,
):

    opponent = (
        2 if player == 1 else 1
    )

    matches = []

    anchors = get_shape_anchors(
        len(board)
    )

    for pattern in anchors[
        shape_name
    ]:

        first_cell = board[
            pattern[0][0]
        ][
            pattern[0][1]
        ]

        middle_cell = board[
            pattern[1][0]
        ][
            pattern[1][1]
        ]

        last_cell = board[
            pattern[2][0]
        ][
            pattern[2][1]
        ]

        if (
            not engine.valid_endpoints(
                first_cell,
                last_cell,
                player,
            )
            or engine.owner_of(
                middle_cell
            ) != opponent
        ):
            continue

        matches.append(
            [
                pattern[0],
                pattern[1],
                pattern[2],
            ]
        )

    return matches


def get_all_matching_patterns(
    board,
    player,
):

    board_key = freeze_board(board)

    cached = _cached_get_all_matching_patterns(
        board_key,
        player,
    )

    return {
        pattern_name: [
            [tuple(cell) for cell in pattern]
            for pattern in pattern_matches
        ]
        for pattern_name, pattern_matches
        in cached
    }


@lru_cache(maxsize=8192)
def _cached_get_all_matching_patterns(
    board_key,
    player,
):

    board = thaw_board(board_key)

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

    frozen_matches = []

    for pattern_name, pattern_matches in (
        matches.items()
    ):

        frozen_matches.append(
            (
                pattern_name,
                tuple(
                    tuple(
                        tuple(cell)
                        for cell in pattern
                    )
                    for pattern in pattern_matches
                ),
            )
        )

    return tuple(frozen_matches)


def wins_including_cell(
    board,
    player,
    moved_cell,
):
    canonical_cache_key = (
        canonical_state_cache_key(
            board,
            player=player,
            moved_cell=moved_cell,
        )
    )

    return dict(
        _cached_wins_including_cell(
            canonical_cache_key,
        )
    )


@lru_cache(maxsize=16384)
def _cached_wins_including_cell(
    canonical_cache_key,
):
    board_key = canonical_cache_key[1]
    player = canonical_cache_key[2]
    moved_cell = canonical_cache_key[3]

    matches = dict(
        _cached_get_all_matching_patterns(
            board_key,
            player,
        )
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

    return tuple(
        counts.items()
    )


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

    groups = (
        engine.config
        .player_pattern_groups[player]
    )

    all_matches = get_all_matching_patterns(
        board,
        player,
    )

    highlights = []

    for group in groups.values():

        for pattern, needed in (
            group["patterns"].items()
        ):

            if needed <= 0:
                continue

            matches = all_matches.get(
                pattern,
                [],
            )

            print(
                player,
                pattern,
                len(matches),
                needed,
            )

            if len(matches) >= needed:

                highlights.extend(
                    matches[:needed]
                )

    print(
        "PLAYER",
        player,
        "HIGHLIGHTS",
        highlights,
    )

    return highlights

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
    canonical_cache_key = (
        canonical_state_cache_key(
            board,
            player=mover,
            moved_cell=moved_cell,
            extra=rules_signature(),
        )
    )

    return dict(
        _cached_resolve_move_outcome(
            canonical_cache_key,
        )
    )


@lru_cache(maxsize=16384)
def _cached_resolve_move_outcome(
    canonical_cache_key,
):
    board_key = canonical_cache_key[1]
    mover = canonical_cache_key[2]
    moved_cell = canonical_cache_key[3]
    board = thaw_board(board_key)

    opponent = (
        2 if mover == 1 else 1
    )

    mover_counts = wins_including_cell(
    board,
    mover,
    None,
    )

    opponent_counts = wins_including_cell(
        board,
        opponent,
        None,
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

        return (
            ("status", "draw"),
            ("winner", 0),
            ("reason", "dual_pattern"),
        )

    if opponent_success:

        return (
            ("status", "win"),
            ("winner", opponent),
            ("reason", "self_sabotage"),
        )

    if mover_success:

        return (
            ("status", "win"),
            ("winner", mover),
            ("reason", "pattern"),
        )

    return (
        ("status", "none"),
        ("winner", None),
        ("reason", None),
    )
