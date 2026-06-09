# =====================================================
# BOARD (same format as engine.py)
# =====================================================

BOARD = [

    "X . . . . . X",

    ". J g . Sg J .",

    ". . . . . . .",

    ". g . X . r .",

    ". . . . . . .",

    ". J Sr . r J .",

    "X . . . . . X",

]


# =====================================================
# PATTERNS
# =====================================================

SHAPES = {

    "horizontal": [
        (0,0),
        (0,1),
        (0,2),
    ],

    "vertical": [
        (0,0),
        (1,0),
        (2,0),
    ],

    "diag_left": [
        (0,2),
        (1,1),
        (2,0),
    ],

    "diag_right": [
        (0,0),
        (1,1),
        (2,2),
    ],

    "triangle_up": [
        (1,0),
        (0,1),
        (1,2),
    ],

    "triangle_down": [
        (0,0),
        (1,1),
        (0,2),
    ],

    "triangle_left": [
        (0,0),
        (1,1),
        (2,0),
    ],

    "triangle_right": [
        (0,1),
        (1,0),
        (2,1),
    ],

    "corner_ul": [
        (0,0),
        (0,1),
        (1,0),
    ],

    "corner_ur": [
        (0,0),
        (0,1),
        (1,1),
    ],

    "corner_dl": [
        (0,0),
        (1,0),
        (1,1),
    ],

    "corner_dr": [
        (0,1),
        (1,0),
        (1,1),
    ],

    "octagon_ul": [
        (0,0),
        (0,1),
        (1,2),
    ],

    "octagon_ur": [
        (0,2),
        (0,1),
        (1,0),
    ],

    "octagon_dl": [
        (0,2),
        (1,1),
        (1,0),
    ],

    "octagon_dr": [
        (0,0),
        (1,1),
        (1,2),
    ],

    "octagon_vul": [
        (0,0),
        (1,0),
        (2,1),
    ],

    "octagon_vur": [
        (0,1),
        (1,1),
        (2,0),
    ],

    "octagon_vdl": [
        (0,1),
        (1,0),
        (2,0),
    ],

    "octagon_vdr": [
        (0,0),
        (1,1),
        (2,1),
    ],
}


# =====================================================
# PARSE BOARD
# =====================================================

def board_cells(rows):

    cells = set()

    for r, row in enumerate(rows):

        tokens = row.split()

        for c, token in enumerate(tokens):

            if token != "X":
                cells.add((r, c))

    return cells


# =====================================================
# COUNT PATTERN
# =====================================================

def count_pattern(board, pattern):

    count = 0

    max_r = max(r for r, c in pattern)
    max_c = max(c for r, c in pattern)

    rows = max(r for r, c in board) + 1
    cols = max(c for r, c in board) + 1

    for base_r in range(rows):

        for base_c in range(cols):

            valid = True

            for dr, dc in pattern:

                if (
                    base_r + dr,
                    base_c + dc
                ) not in board:

                    valid = False
                    break

            if valid:
                count += 1

    return count


# =====================================================
# MAIN
# =====================================================

def main():

    board = board_cells(BOARD)

    print()
    print("=" * 50)
    print("PATTERN CENSUS")
    print("=" * 50)

    total = 0

    for name in sorted(SHAPES):

        count = count_pattern(
            board,
            SHAPES[name]
        )

        total += count

        print(
            f"{name:<20} {count}"
        )

    print("=" * 50)
    print(
        f"{'TOTAL':<20} {total}"
    )
    print("=" * 50)


if __name__ == "__main__":
    main()