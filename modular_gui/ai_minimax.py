from modular_gui.board import apply_move, get_all_moves
from modular_gui.engine import has_any_win


DEFAULT_MINIMAX_DEPTH = 3


def copy_board(board):
    return [row[:] for row in board]


def has_win(board, player):
    return has_any_win(board, player)


def move_results_in_win(board, move, player):
    next_board = copy_board(board)
    apply_move(next_board, move)
    return has_win(next_board, player)


def evaluate_board(board, player):
    opponent = 2 if player == 1 else 1

    if has_win(board, player):
        return 1000

    if has_win(board, opponent):
        return -1000

    player_winning_moves = sum(
        1
        for move in get_all_moves(board, player)
        if move_results_in_win(board, move, player)
    )

    opponent_winning_moves = sum(
        1
        for move in get_all_moves(board, opponent)
        if move_results_in_win(board, move, opponent)
    )

    player_mobility = len(get_all_moves(board, player))
    opponent_mobility = len(get_all_moves(board, opponent))

    return (
        20 * (player_winning_moves - opponent_winning_moves)
        + (player_mobility - opponent_mobility)
    )


def minimax_score(board, root_player, current_player, depth, alpha, beta):
    opponent = 2 if current_player == 1 else 1

    if has_win(board, root_player):
        return 1000 + depth

    if has_win(board, 2 if root_player == 1 else 1):
        return -1000 - depth

    if depth == 0:
        return evaluate_board(board, root_player)

    legal_moves = get_all_moves(board, current_player)

    if not legal_moves:
        return 0

    if current_player == root_player:
        value = -(10 ** 9)

        for move in legal_moves:
            next_board = copy_board(board)
            apply_move(next_board, move)

            if has_win(next_board, current_player):
                score = 1000 + depth
            else:
                score = minimax_score(
                    next_board,
                    root_player,
                    opponent,
                    depth - 1,
                    alpha,
                    beta,
                )

            value = max(value, score)
            alpha = max(alpha, value)

            if beta <= alpha:
                break

        return value

    value = 10 ** 9

    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move)

        if has_win(next_board, current_player):
            score = -1000 - depth
        else:
            score = minimax_score(
                next_board,
                root_player,
                opponent,
                depth - 1,
                alpha,
                beta,
            )

        value = min(value, score)
        beta = min(beta, value)

        if beta <= alpha:
            break

    return value


def choose_move(board, player, legal_moves, rng, seen_states=None):
    del seen_states

    if not legal_moves:
        return None

    best_score = None
    best_moves = []
    opponent = 2 if player == 1 else 1

    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move)

        if has_win(next_board, player):
            score = 1000 + DEFAULT_MINIMAX_DEPTH
        else:
            score = minimax_score(
                next_board,
                player,
                opponent,
                DEFAULT_MINIMAX_DEPTH - 1,
                -(10 ** 9),
                10 ** 9,
            )

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return rng.choice(best_moves)
