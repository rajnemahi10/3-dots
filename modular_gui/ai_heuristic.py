from modular_gui.board import apply_move, get_all_moves, resolve_move_outcome


def copy_board(board):
    return [row[:] for row in board]


def board_key(board, player):
    return (
        player,
        tuple(tuple(row) for row in board),
    )


def move_results_in_win(board, move, player):
    next_board = copy_board(board)
    apply_move(next_board, move)
    outcome = resolve_move_outcome(next_board, player, move[1])
    return outcome["status"] == "win" and outcome["winner"] == player


def opponent_has_immediate_win(board, player):
    opponent = 2 if player == 1 else 1
    return any(
        move_results_in_win(board, move, opponent)
        for move in get_all_moves(board, opponent)
    )


def choose_move(board, player, legal_moves, rng, seen_states=None):
    if not legal_moves:
        return None

    if seen_states is None:
        seen_states = set()

    winning_moves = []
    drawing_moves = []
    blocking_moves = []
    safe_unseen_moves = []
    safe_seen_moves = []
    risky_unseen_moves = []
    risky_seen_moves = []

    opponent = 2 if player == 1 else 1
    opponent_winning_now = any(
        move_results_in_win(board, opp_move, opponent)
        for opp_move in get_all_moves(board, opponent)
    )

    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move)
        next_state = board_key(next_board, opponent)
        is_seen = next_state in seen_states

        outcome = resolve_move_outcome(next_board, player, move[1])

        if outcome["status"] == "win":
            if outcome["winner"] == player:
                winning_moves.append(move)
            elif is_seen:
                risky_seen_moves.append(move)
            else:
                risky_unseen_moves.append(move)

            continue

        if outcome["status"] == "draw":
            drawing_moves.append(move)
            continue

        if opponent_has_immediate_win(next_board, player):
            if is_seen:
                risky_seen_moves.append(move)
            else:
                risky_unseen_moves.append(move)
            continue

        if opponent_winning_now:
            blocking_moves.append(move)

        if is_seen:
            safe_seen_moves.append(move)
        else:
            safe_unseen_moves.append(move)

    if winning_moves:
        return rng.choice(winning_moves)

    if drawing_moves:
        return rng.choice(drawing_moves)

    if blocking_moves:
        return rng.choice(blocking_moves)

    if safe_unseen_moves:
        return rng.choice(safe_unseen_moves)

    if safe_seen_moves:
        return rng.choice(safe_seen_moves)

    if risky_unseen_moves:
        return rng.choice(risky_unseen_moves)

    return rng.choice(risky_seen_moves)
