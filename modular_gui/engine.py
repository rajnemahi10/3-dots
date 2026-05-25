from typing import Literal, TypeAlias

Cell: TypeAlias = Literal[
    ".",
    "r",
    "g",
    "R",
    "G",
    "J",
    "X",
]

EMPTY: Cell = "."
RED_SINGLE: Cell = "r"
GREEN_SINGLE: Cell = "g"
RED_LONG: Cell = "R"
GREEN_LONG: Cell = "G"
JOKER: Cell = "J"
BLOCKED: Cell = "X"


PATTERNS = {
    "horizontal": [],
    "vertical": [],
    "diag_left": [],
    "diag_right": [],
}


SHAPE_PATTERNS = {

    "triangle_up": [
        [(1,0), (0,1), (1,2)],
    ],

    "triangle_down": [
        [(0,0), (1,1), (0,2)],
    ],

    "triangle_left": [
        [(0,0), (1,1), (2,0)],
    ],

    "triangle_right": [
        [(0,1), (1,0), (2,1)],
    ],

    "corner_ul": [
        [(0,1), (0,0), (1,0)],
    ],

    "corner_ur": [
        [(0,0), (0,1), (1,1)],
    ],

    "corner_dl": [
        [(0,0), (1,0), (1,1)],
    ],

    "corner_dr": [
        [(0,1), (1,1), (1,0)],
    ],
}


CURRENT_PATTERN_SIZE = None


STARTING_NOTATION_BY_SIZE = {

    4: [

        "X X X X X X",

        "X r r . . X",

        "X . . . . X",

        "X . . . . X",

        "X . . g g X",

        "X X X X X X",
    ],

    5: [

        "X X J X J X X",

        "J . R . G . X",

        "X . r . g . J",

        "J . J . . . X",

        "X . g . r . J",

        "J . G . R . X",

        "X X J X J X X",
    ],

    6: [

        "X X J X X J X X",

        "J . . R . . . X",

        "X . r . . g . J",

        "X . . J . . . X",

        "J . . . . . . X",

        "X . g . . r . J",

        "X . . . G . . X",

        "X X J X X J X X",
    ],

    7: [

        "X X J X X X J X X",

        "X . . R . G . . X",

        "J . r . . . g . X",

        "X . . J . . . . J",

        "X . . . . . . . X",

        "X . g . . . r . J",

        "J . . . . . . . X",

        "X . . G . R . . J",

        "X X J X X X J X X",
    ],
}


class GameConfig:

    def __init__(self):

        self.player_pattern_groups = {

            1: {

                "lines": {

                    "mode": "or",

                    "patterns": {

                        "horizontal": 1,
                        "vertical": 1,
                        "diag_left": 1,
                        "diag_right": 1,
                    },
                },

                "triangles": {

                    "mode": "or",

                    "patterns": {

                        "triangle_up": 0,
                        "triangle_down": 0,
                        "triangle_left": 0,
                        "triangle_right": 0,
                    },
                },

                "corners": {

                    "mode": "or",

                    "patterns": {

                        "corner_ul": 0,
                        "corner_ur": 0,
                        "corner_dl": 0,
                        "corner_dr": 0,
                    },
                },
            },

            2: {

                "lines": {

                    "mode": "or",

                    "patterns": {

                        "horizontal": 1,
                        "vertical": 1,
                        "diag_left": 1,
                        "diag_right": 1,
                    },
                },

                "triangles": {

                    "mode": "or",

                    "patterns": {

                        "triangle_up": 0,
                        "triangle_down": 0,
                        "triangle_left": 0,
                        "triangle_right": 0,
                    },
                },

                "corners": {

                    "mode": "or",

                    "patterns": {

                        "corner_ul": 0,
                        "corner_ur": 0,
                        "corner_dl": 0,
                        "corner_dr": 0,
                    },
                },
            },
        }


config = GameConfig()


def parse_compact_notation_rows(rows):

    board = []

    valid_tokens = {

        EMPTY,
        RED_SINGLE,
        GREEN_SINGLE,
        RED_LONG,
        GREEN_LONG,
        JOKER,
        BLOCKED,
    }

    edge_tokens = {
        BLOCKED,
        JOKER,
    }

    interior_tokens = valid_tokens

    for raw_row in rows:

        tokens = raw_row.split()

        row = []

        for token in tokens:

            if token not in valid_tokens:

                raise ValueError(
                    f"Unknown token: {token}"
                )

            row.append(token)

        board.append(row)

    if not board:
        raise ValueError("Empty board")

    width = len(board[0])

    if any(len(row) != width for row in board):

        raise ValueError(
            "Rows must have equal width"
        )

    size = len(board)

    if width != size:

        raise ValueError(
            "Board must be square"
        )

    for row in range(size):

        for col in range(size):

            cell = board[row][col]

            on_edge = (

                row == 0
                or col == 0
                or row == size - 1
                or col == size - 1
            )

            if on_edge:

                if cell not in edge_tokens:

                    raise ValueError(
                        "Edges must contain X or J"
                    )

            else:

                if cell not in interior_tokens:

                    raise ValueError(
                        "Invalid interior token"
                    )

    return board


def owner_of(cell):

    if cell in (
        RED_SINGLE,
        RED_LONG,
    ):
        return 1

    if cell in (
        GREEN_SINGLE,
        GREEN_LONG,
    ):
        return 2

    return 0


def is_player_piece(cell, player):

    return owner_of(cell) == player


def is_long_range_piece(cell):

    return cell in (
        RED_LONG,
        GREEN_LONG,
    )


def is_joker(cell):

    return cell == JOKER


def endpoint_matches_player(
    cell,
    player,
):

    return (

        owner_of(cell) == player
        or is_joker(cell)
    )

def valid_endpoints(
    first_cell,
    last_cell,
    player,
):

    first_matches = endpoint_matches_player(
        first_cell,
        player,
    )

    last_matches = endpoint_matches_player(
        last_cell,
        player,
    )

    if not (
        first_matches
        and last_matches
    ):
        return False

    # prevent Joker + Joker

    if (
        is_joker(first_cell)
        and is_joker(last_cell)
    ):

        return False

    return True


def pattern_enabled(
    player,
    pattern_name,
):

    groups = (
        config.player_pattern_groups[player]
    )

    for group in groups.values():

        patterns = group["patterns"]

        if (
            pattern_name in patterns
            and patterns[pattern_name] > 0
        ):

            return True

    return False


def generate_patterns(size):

    global PATTERNS
    global CURRENT_PATTERN_SIZE

    PATTERNS = {

        "horizontal": [],
        "vertical": [],
        "diag_left": [],
        "diag_right": [],
    }

    for row in range(size):

        for col in range(size - 2):

            PATTERNS["horizontal"].append(

                [
                    (row, col),
                    (row, col + 1),
                    (row, col + 2),
                ]
            )

    for row in range(size - 2):

        for col in range(size):

            PATTERNS["vertical"].append(

                [
                    (row, col),
                    (row + 1, col),
                    (row + 2, col),
                ]
            )

    for row in range(size - 2):

        for col in range(size - 2):

            PATTERNS["diag_right"].append(

                [
                    (row, col),
                    (row + 1, col + 1),
                    (row + 2, col + 2),
                ]
            )

            PATTERNS["diag_left"].append(

                [
                    (row, col + 2),
                    (row + 1, col + 1),
                    (row + 2, col),
                ]
            )

    CURRENT_PATTERN_SIZE = size


def ensure_patterns_for_board(board):

    size = len(board)

    if CURRENT_PATTERN_SIZE != size:
        generate_patterns(size)


def get_cell(board, row, col):

    if (
        0 <= row < len(board)
        and 0 <= col < len(board[row])
    ):

        return board[row][col]

    return None


def check_shape_win(
    board,
    player,
    shape_offsets,
):

    size = len(board)

    opponent = (
        2 if player == 1 else 1
    )

    max_r = max(
        dr for dr, dc in shape_offsets
    )

    max_c = max(
        dc for dr, dc in shape_offsets
    )

    for row in range(size - max_r):

        for col in range(size - max_c):

            player_count = 0
            opponent_count = 0

            for dr, dc in shape_offsets:

                r = row + dr
                c = col + dc

                cell = board[r][c]

                if endpoint_matches_player(
                    cell,
                    player,
                ):
                    player_count += 1

                elif owner_of(cell) == opponent:
                    opponent_count += 1

            if (
                player_count >= 2
                and opponent_count >= 1
            ):

                return True

    return False


def has_any_win(board, player):

    ensure_patterns_for_board(board)

    groups = (
        config.player_pattern_groups[player]
    )

    for group_name, group in groups.items():

        mode = group["mode"]

        patterns = group["patterns"]

        enabled_results = []

        for pattern_name, needed in patterns.items():

            if needed <= 0:
                continue

            count = 0

            if pattern_name in PATTERNS:

                pattern_list = PATTERNS[
                    pattern_name
                ]

                opponent = (
                    2 if player == 1 else 1
                )

                for pattern in pattern_list:

                    start_row, start_col = pattern[0]
                    middle_row, middle_col = pattern[1]
                    end_row, end_col = pattern[2]

                    start_cell = get_cell(
                        board,
                        start_row,
                        start_col,
                    )

                    middle_cell = get_cell(
                        board,
                        middle_row,
                        middle_col,
                    )

                    end_cell = get_cell(
                        board,
                        end_row,
                        end_col,
                    )

                    if (
                        start_cell is not None
                        and middle_cell is not None
                        and end_cell is not None

                        and endpoint_matches_player(
                            start_cell,
                            player,
                        )

                        and owner_of(
                            middle_cell
                        ) == opponent

                        and endpoint_matches_player(
                            end_cell,
                            player,
                        )
                    ):

                        count += 1

            else:

                for offsets in SHAPE_PATTERNS[
                    pattern_name
                ]:

                    if check_shape_win(
                        board,
                        player,
                        offsets,
                    ):

                        count += 1

            enabled_results.append(
                count >= needed
            )

        if not enabled_results:
            continue

        if mode == "and":

            if not all(enabled_results):
                return False

        else:

            if not any(enabled_results):
                return False

    return True


def create_initial_board(board_size=4):

    if board_size not in STARTING_NOTATION_BY_SIZE:

        raise ValueError(
            f"Unsupported size: {board_size}"
        )

    board = parse_compact_notation_rows(

        STARTING_NOTATION_BY_SIZE[
            board_size
        ]
    )

    generate_patterns(len(board))

    return board