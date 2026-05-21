from modular_gui.board import apply_move, get_all_moves, resolve_move_outcome


DEFAULT_ROLLOUTS = 24
DEFAULT_ROLLOUT_DEPTH = 8


def copy_board(board):
    return [row[:] for row in board]


def score_outcome(outcome, root_player):
    if outcome["status"] == "draw":
        return 0.0

    if outcome["status"] == "win":
        if outcome["winner"] == root_player:
            return 1.0

        return -1.0

    return None


def move_results_in_win(board, move, player):
    next_board = copy_board(board)
    apply_move(next_board, move)
    outcome = resolve_move_outcome(next_board, player, move[1])
    return outcome["status"] == "win" and outcome["winner"] == player


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


def rollout_result(board, next_player, root_player, rng, rollout_depth):
    current_player = next_player
    depth_left = rollout_depth

    while depth_left > 0:
        legal_moves = get_all_moves(board, current_player)

        if not legal_moves:
            return 0.0

        move = rng.choice(legal_moves)

        apply_move(board, move)

        outcome = resolve_move_outcome(board, current_player, move[1])
        outcome_score = score_outcome(outcome, root_player)

        if outcome_score is not None:
            return outcome_score

        current_player = 2 if current_player == 1 else 1
        depth_left -= 1

    score = evaluate_board(board, root_player)

    if score > 0:
        return 0.25

    if score < 0:
        return -0.25

    return 0.0


def choose_move(board, player, legal_moves, rng, seen_states=None):
    del seen_states

    if not legal_moves:
        return None

    best_score = None
    best_moves = []
    opponent = 2 if player == 1 else 1

    for move in legal_moves:
        total = 0.0

        for _ in range(DEFAULT_ROLLOUTS):
            next_board = copy_board(board)
            apply_move(next_board, move)

            outcome = resolve_move_outcome(next_board, player, move[1])
            outcome_score = score_outcome(outcome, player)

            if outcome_score is None:
                total += rollout_result(
                    next_board,
                    opponent,
                    player,
                    rng,
                    DEFAULT_ROLLOUT_DEPTH,
                )
            else:
                total += outcome_score

        score = total / DEFAULT_ROLLOUTS

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return rng.choice(best_moves)
