PATTERNS = {
    "horizontal": [],
    "vertical": [],
    "diagonal": [],
}

SHAPE_PATTERNS = {

    "triangle_up": [
        [(0,1),(1,0),(1,2)],
    ],

    "triangle_down": [
        [(0,0),(0,2),(1,1)],
    ],

    "triangle_left": [
        [(0,0),(1,1),(2,0)],
    ],

    "triangle_right": [
        [(0,1),(1,0),(2,1)],
    ],

    "corner_ul": [
        [(0,0),(0,1),(1,0)],
    ],

    "corner_ur": [
        [(0,0),(0,1),(1,1)],
    ],

    "corner_dl": [
        [(0,0),(1,0),(1,1)],
    ],

    "corner_dr": [
        [(0,1),(1,0),(1,1)],
    ],
}


JOKER = 9
ACTIVE_JOKER_POSITIONS = set()


def owner_of(cell):

    if cell in (1, 3):
        return 1

    if cell in (2, 4):
        return 2

    return 0


def is_player_piece(cell, player):
    return owner_of(cell) == player


def is_long_range_piece(cell):
    return cell in (3, 4)


def is_joker(cell):
    return cell == JOKER


def endpoint_matches_player(cell, player):
    return owner_of(cell) == player or is_joker(cell)


def generate_patterns(size):

    global PATTERNS

    PATTERNS = {
        "horizontal": [],
        "vertical": [],
        "diagonal": [],
    }

    for row in range(size):

        for col in range(size - 2):

            PATTERNS["horizontal"].append(
                [(row, col), (row, col + 1), (row, col + 2)]
            )

    for row in range(size - 2):

        for col in range(size):

            PATTERNS["vertical"].append(
                [(row, col), (row + 1, col), (row + 2, col)]
            )

    for row in range(size - 2):

        for col in range(size - 2):

            PATTERNS["diagonal"].append(
                [(row, col), (row + 1, col + 1), (row + 2, col + 2)]
            )

            PATTERNS["diagonal"].append(
                [(row, col + 2), (row + 1, col + 1), (row + 2, col)]
            )

    # OUTSIDE JOKER PATTERNS

    if size == 4:

        for col in (1, 3):
            PATTERNS["vertical"].append(
                [(-1, col), (0, col), (1, col)]
            )

        for col in (0, 2):
            PATTERNS["vertical"].append(
                [(2, col), (3, col), (4, col)]
            )

        for row in (0, 2):
            PATTERNS["horizontal"].append(
                [(row, -1), (row, 0), (row, 1)]
            )

        for row in (1, 3):
            PATTERNS["horizontal"].append(
                [(row, 2), (row, 3), (row, 4)]
            )

    if size == 5:

        for col in (1, 3):
            PATTERNS["vertical"].append(
                [(-1, col), (0, col), (1, col)]
            )

        for col in (1, 3):
            PATTERNS["vertical"].append(
                [(3, col), (4, col), (5, col)]
            )

        for row in (1, 3):
            PATTERNS["horizontal"].append(
                [(row, -1), (row, 0), (row, 1)]
            )

        for row in (1, 3):
            PATTERNS["horizontal"].append(
                [(row, 3), (row, 4), (row, 5)]
            )

    if size == 6:

        for col in (1, 4):
            PATTERNS["vertical"].append(
                [(-1, col), (0, col), (1, col)]
            )

        for col in (1, 4):
            PATTERNS["vertical"].append(
                [(4, col), (5, col), (6, col)]
            )

        for row in (1, 4):
            PATTERNS["horizontal"].append(
                [(row, -1), (row, 0), (row, 1)]
            )

        for row in (1, 4):
            PATTERNS["horizontal"].append(
                [(row, 4), (row, 5), (row, 6)]
            )


def get_outside_joker_positions(size):

    if size == 4:

        return {
            (-1,1), (-1,3),
            (0,-1), (2,-1),
            (1,4), (3,4),
            (4,0), (4,2),
        }

    if size == 5:

        return {
            (-1,1), (-1,3),
            (1,-1), (3,-1),
            (1,5), (3,5),
            (5,1), (5,3),
        }

    if size == 6:

        return {
            (-1,1), (-1,4),
            (1,-1), (4,-1),
            (1,6), (4,6),
            (6,1), (6,4),
        }

    return set()


def set_active_joker_positions(size):

    global ACTIVE_JOKER_POSITIONS

    ACTIVE_JOKER_POSITIONS = get_outside_joker_positions(size)


def get_active_joker_positions():
    return set(ACTIVE_JOKER_POSITIONS)


def get_cell(board, row, col):

    if 0 <= row < len(board) and 0 <= col < len(board[row]):
        return board[row][col]

    if (row, col) in ACTIVE_JOKER_POSITIONS:
        return JOKER

    return None


def check_win(board, player, pattern_name):

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
            1: [
                "horizontal",
                "vertical",
                "diagonal",
            ],
            2: [
                "horizontal",
                "vertical",
                "diagonal",
            ],
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

    for pattern_name in config.player_patterns[player]:

        if check_win(board, player, pattern_name):
            return True

    for shape_name in config.extra_shapes:

        for offsets in SHAPE_PATTERNS[shape_name]:

            if check_shape_win(board, player, offsets):
                return True

    return False

def create_initial_board(layout="crossfire_4x4"):

    if layout in ("crossfire_4x4", "rotational_4x4"):
        size = 4

    elif layout in ("center_warfare_5x5", "dual_pressure_5x5"):
        size = 5

    elif layout == "competitive_6x6":
        size = 6

    else:
        size = 4

    generate_patterns(size)
    set_active_joker_positions(size)

    board = [[0] * size for _ in range(size)]

    # ---------------------------------------------------
    # 4x4 CROSS FIRE
    # ---------------------------------------------------

    if layout == "crossfire_4x4":

        board = [
            [0, 3, 0, 0],
            [1, 0, 2, 0],
            [0, 1, 0, 2],
            [0, 0, 4, 0],
        ]

    # ---------------------------------------------------
    # 4x4 ROTATIONAL
    # ---------------------------------------------------

    elif layout == "rotational_4x4":

        board = [
            [1, 0, 0, 3],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [4, 0, 0, 2],
        ]

    # ---------------------------------------------------
    # NEW FIXED 5x5 CENTER WARFARE
    # ---------------------------------------------------

    elif layout == "center_warfare_5x5":

        board = [
            [0, 0, 3, 0, 0],
            [1, 0, 0, 2, 0],
            [0, 0, 0, 0, 0],
            [0, 1, 0, 0, 2],
            [0, 0, 4, 0, 0],
        ]

    # ---------------------------------------------------
    # 5x5 DUAL PRESSURE
    # ---------------------------------------------------

    elif layout == "dual_pressure_5x5":

        board = [
            [1, 0, 0, 0, 3],
            [0, 0, 2, 0, 0],
            [0, 1, 0, 2, 0],
            [0, 0, 1, 0, 0],
            [4, 0, 0, 0, 2],
        ]

    # ---------------------------------------------------
    # 6x6 COMPETITIVE
    # ---------------------------------------------------

    elif layout == "competitive_6x6":

        board = [
            [0, 0, 3, 0, 0, 0],
            [0, 1, 0, 0, 2, 0],
            [0, 0, 1, 2, 0, 0],
            [0, 0, 2, 1, 0, 0],
            [0, 2, 0, 0, 1, 0],
            [0, 0, 0, 4, 0, 0],
        ]

    return board
    