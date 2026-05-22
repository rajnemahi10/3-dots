from typing import Literal, TypeAlias

Cell: TypeAlias = Literal[".", "r", "g", "R", "G", "J", "X"]

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
    "diagonal": [],
}

SHAPE_PATTERNS = {
    "triangle_up": [
        [(0, 1), (1, 0), (1, 2)],
    ],
    "triangle_down": [
        [(0, 0), (0, 2), (1, 1)],
    ],
    "triangle_left": [
        [(0, 0), (1, 1), (2, 0)],
    ],
    "triangle_right": [
        [(0, 1), (1, 0), (2, 1)],
    ],
    "corner_ul": [
        [(0, 0), (0, 1), (1, 0)],
    ],
    "corner_ur": [
        [(0, 0), (0, 1), (1, 1)],
    ],
    "corner_dl": [
        [(0, 0), (1, 0), (1, 1)],
    ],
    "corner_dr": [
        [(0, 1), (1, 0), (1, 1)],
    ],
}

CURRENT_PATTERN_SIZE: int | None = None

STARTING_NOTATION_BY_SIZE = {
    4: [
        "X J X J X X",
        "X . R . . J",
        "J r . g . X",
        "X . r . g J",
        "J . . G . X",
        "X X J X J X",
    ],
    5: [
        "X J X J X X X",
        "X . . R . . J",
        "X r . . g . X",
        "J . . . . . J",
        "X . r . . g X",
        "J . . G . . X",
        "X X X J X J X",
    ],
    6: [
        "X J X X J X X X",
        "X . . R . . . J",
        "X . r . . g . X",
        "J . . r g . . X",
        "X . . g r . . J",
        "X . g . . r . X",
        "J . . . G . . X",
        "X X X J X X J X",
    ],
}


def parse_compact_notation_rows(rows: list[str]) -> list[list[Cell]]:
    board: list[list[Cell]] = []

    valid_tokens = {
        EMPTY,
        RED_SINGLE,
        GREEN_SINGLE,
        RED_LONG,
        GREEN_LONG,
        JOKER,
        BLOCKED,
    }
    edge_tokens = {BLOCKED, JOKER}
    interior_tokens = {EMPTY, RED_SINGLE, GREEN_SINGLE, RED_LONG, GREEN_LONG}

    for raw_row in rows:
        text = raw_row.strip()

        if text.startswith("[") and text.endswith("]"):
            text = text[1:-1].strip()

        tokens = [token for token in text.replace(",", " ").split() if token]

        if not tokens:
            continue

        row: list[Cell] = []

        for token in tokens:
            if token not in valid_tokens:
                raise ValueError(f"Unknown notation token: {token}")

            row.append(token)

        board.append(row)

    if not board:
        raise ValueError("Notation rows cannot be empty")

    width = len(board[0])

    if any(len(row) != width for row in board):
        raise ValueError("All notation rows must have equal width")

    size = len(board)

    if size < 3 or width != size:
        raise ValueError("Notation must be square and at least 3x3")

    for row_index, row in enumerate(board):
        for col_index, cell in enumerate(row):
            on_edge = (
                row_index == 0
                or col_index == 0
                or row_index == size - 1
                or col_index == size - 1
            )

            if on_edge and cell not in edge_tokens:
                raise ValueError("Board edge must contain only X or J")

            if not on_edge and cell not in interior_tokens:
                raise ValueError("Board interior must contain only ., r, g, R, G")

    return board


def owner_of(cell: Cell) -> int:
    if cell in (RED_SINGLE, RED_LONG):
        return 1

    if cell in (GREEN_SINGLE, GREEN_LONG):
        return 2

    return 0


def is_player_piece(cell: Cell, player: int) -> bool:
    return owner_of(cell) == player


def is_long_range_piece(cell: Cell) -> bool:
    return cell in (RED_LONG, GREEN_LONG)


def is_joker(cell: Cell) -> bool:
    return cell == JOKER


def endpoint_matches_player(cell: Cell, player: int) -> bool:
    return owner_of(cell) == player or is_joker(cell)


def generate_patterns(size):
    global PATTERNS
    global CURRENT_PATTERN_SIZE

    PATTERNS = {
        "horizontal": [],
        "vertical": [],
        "diagonal": [],
    }

    for row in range(size):
        for col in range(size - 2):
            PATTERNS["horizontal"].append([(row, col), (row, col + 1), (row, col + 2)])

    for row in range(size - 2):
        for col in range(size):
            PATTERNS["vertical"].append([(row, col), (row + 1, col), (row + 2, col)])

    for row in range(size - 2):
        for col in range(size - 2):
            PATTERNS["diagonal"].append(
                [(row, col), (row + 1, col + 1), (row + 2, col + 2)]
            )

            PATTERNS["diagonal"].append(
                [(row, col + 2), (row + 1, col + 1), (row + 2, col)]
            )

    CURRENT_PATTERN_SIZE = size


def ensure_patterns_for_board(board: list[list[Cell]]) -> None:
    size = len(board)

    if CURRENT_PATTERN_SIZE != size:
        generate_patterns(size)


def get_cell(board: list[list[Cell]], row: int, col: int) -> Cell | None:
    if 0 <= row < len(board) and 0 <= col < len(board[row]):
        return board[row][col]

    return None


def check_win(board, player, pattern_name):
    ensure_patterns_for_board(board)

    opponent = 2 if player == 1 else 1

    for pattern in PATTERNS[pattern_name]:
        start_row, start_col = pattern[0]
        middle_row, middle_col = pattern[1]
        end_row, end_col = pattern[2]

        start_cell = get_cell(board, start_row, start_col)
        middle_cell = get_cell(board, middle_row, middle_col)
        end_cell = get_cell(board, end_row, end_col)

        if (
            start_cell is not None
            and middle_cell is not None
            and end_cell is not None
            and endpoint_matches_player(start_cell, player)
            and owner_of(middle_cell) == opponent
            and endpoint_matches_player(end_cell, player)
        ):
            return True

    return False


def check_shape_win(board, player, shape_offsets):
    size = len(board)
    opponent = 2 if player == 1 else 1

    max_r = max(dr for dr, dc in shape_offsets)
    max_c = max(dc for dr, dc in shape_offsets)

    for row in range(size - max_r):
        for col in range(size - max_c):
            player_count = 0
            opponent_count = 0

            for dr, dc in shape_offsets:
                r = row + dr
                c = col + dc
                cell = board[r][c]

                if endpoint_matches_player(cell, player):
                    player_count += 1
                elif owner_of(cell) == opponent:
                    opponent_count += 1

            if player_count >= 2 and opponent_count >= 1:
                return True

    return False


class GameConfig:
    def __init__(self):
        self.player_patterns = {
            1: ["horizontal", "vertical", "diagonal"],
            2: ["horizontal", "vertical", "diagonal"],
        }

        self.extra_shapes = [
            "triangle_up",
            "triangle_down",
            "triangle_left",
            "triangle_right",
            "corner_ul",
            "corner_ur",
            "corner_dl",
            "corner_dr",
        ]


config = GameConfig()


def has_any_win(board, player):
    ensure_patterns_for_board(board)

    for pattern_name in config.player_patterns[player]:
        if check_win(board, player, pattern_name):
            return True

    for shape_name in config.extra_shapes:
        for offsets in SHAPE_PATTERNS[shape_name]:
            if check_shape_win(board, player, offsets):
                return True

    return False


def create_initial_board(board_size: int = 4):
    if board_size not in STARTING_NOTATION_BY_SIZE:
        raise ValueError(f"Unsupported board size: {board_size}")

    board = parse_compact_notation_rows(STARTING_NOTATION_BY_SIZE[board_size])

    generate_patterns(len(board))

    return board
