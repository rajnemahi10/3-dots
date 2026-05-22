from modular_gui.board import apply_move, get_all_moves, resolve_move_outcome


DEFAULT_MINIMAX_DEPTH = 3
INF = 10 ** 9


def copy_board(board):
    return [row[:] for row in board]


def move_results_in_win(board, move, player):
    next_board = copy_board(board)
    apply_move(next_board, move)
    outcome = resolve_move_outcome(next_board, player, move[1])
    return outcome["status"] == "win" and outcome["winner"] == player


def state_key(board, player):
    return (
        player,
        tuple(tuple(row) for row in board),
    )


def score_outcome(outcome, root_player, depth):
    if outcome["status"] == "draw":
        return 0

    if outcome["status"] == "win":
        if outcome["winner"] == root_player:
            return 1000 + depth

        return -1000 - depth

    return None


def evaluate_board(board, player):
    opponent = 2 if player == 1 else 1

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


def minimax_score(
    board,
    root_player,
    current_player,
    depth,
    alpha,
    beta,
    last_mover,
    last_move_to,
):
    opponent = 2 if current_player == 1 else 1
    outcome = resolve_move_outcome(board, last_mover, last_move_to)
    terminal_score = score_outcome(outcome, root_player, depth)

    if terminal_score is not None:
        return terminal_score

    if depth == 0:
        return evaluate_board(board, root_player)

    legal_moves = get_all_moves(board, current_player)

    if not legal_moves:
        return 0

    if current_player == root_player:
        value = -INF

        for move in legal_moves:
            next_board = copy_board(board)
            apply_move(next_board, move)

            score = minimax_score(
                next_board,
                root_player,
                opponent,
                depth - 1,
                alpha,
                beta,
                current_player,
                move[1],
            )

            value = max(value, score)
            alpha = max(alpha, value)

            if beta <= alpha:
                break

        return value

    value = INF

    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move)

        score = minimax_score(
            next_board,
            root_player,
            opponent,
            depth - 1,
            alpha,
            beta,
            current_player,
            move[1],
        )

        value = min(value, score)
        beta = min(beta, value)

        if beta <= alpha:
            break

    return value


def choose_move(board, player, legal_moves, rng, seen_states=None):
    if not legal_moves:
        return None

    if seen_states is None:
        seen_states = set()

    best_score = None
    best_moves = []
    opponent = 2 if player == 1 else 1

    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move)

        outcome = resolve_move_outcome(next_board, player, move[1])
        score = score_outcome(outcome, player, DEFAULT_MINIMAX_DEPTH)

        if score is None:
            score = minimax_score(
                next_board,
                player,
                opponent,
                DEFAULT_MINIMAX_DEPTH - 1,
                -INF,
                INF,
                player,
                move[1],
            )

        if state_key(next_board, opponent) in seen_states:
            score -= 1

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return rng.choice(best_moves)
