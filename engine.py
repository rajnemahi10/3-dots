PATTERNS = {
    "horizontal": [
        [(0, 0), (0, 1), (0, 2)],
        [(1, 0), (1, 1), (1, 2)],
        [(2, 0), (2, 1), (2, 2)],
    ],
    "vertical": [
        [(0, 0), (1, 0), (2, 0)],
        [(0, 1), (1, 1), (2, 1)],
        [(0, 2), (1, 2), (2, 2)],
    ],
    "diagonal": [
        [(0, 0), (1, 1), (2, 2)],
        [(0, 2), (1, 1), (2, 0)],
    ],
}

def check_pattern(board,row,col,pattern,player):
    size = len(board)

    for dr,dc in pattern:

        nr = row + dr
        nc = col + dc

        # outside board?
        if not (0 <= nr < size and
                0 <= nc < size):

            return False

        # wrong piece?
        if board[nr][nc] != player:

            return False

    return True

def check_win(board,
              player,
              pattern_name):
    for pattern in PATTERNS[pattern_name]:
        start_row, start_col = pattern[0]
        middle_row, middle_col = pattern[1]
        end_row, end_col = pattern[2]
        opponent = 2 if player == 1 else 1

        if (
            board[start_row][start_col] == player
            and board[middle_row][middle_col] == opponent
            and board[end_row][end_col] == player
        ):
            return True

    return False
class GameConfig:

    def __init__(self):

        self.board_size = 3

        self.player_patterns = {
            1: ["horizontal", "vertical", "diagonal"],
            2: ["horizontal", "vertical", "diagonal"]
        }

        self.piece_counts = {
            1: 2,
            2: 2
        }
        

config=GameConfig()
size = config.board_size


def create_initial_board(layout="corners"):
    board = []

    for i in range(size):

        row = [0] * size

        board.append(row)

    if layout == "corners":
        board[0][0] = 1
        board[0][2] = 1

        board[2][0] = 2
        board[2][2] = 2
    elif layout == "staggered":
        board[0][0] = 1
        board[0][1] = 1

        board[2][1] = 2
        board[2][2] = 2
    else:
        raise ValueError(f"Unknown layout: {layout}")

    return board


board = create_initial_board()
