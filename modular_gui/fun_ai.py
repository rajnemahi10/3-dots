from modular_gui.board import (
    apply_move,
    get_all_moves,
    resolve_move_outcome,
    wins_including_cell,
)

import modular_gui.engine as engine


def copy_board(board):
    return [row[:] for row in board]


def board_key(board, player):
    return (
        player,
        tuple(tuple(row) for row in board),
    )


def move_results_in_win(board, move, player):

    next_board = copy_board(board)

    apply_move(
        next_board,
        move,
    )

    outcome = resolve_move_outcome(
        next_board,
        player,
        move[1],
    )

    return (
        outcome["status"] == "win"
        and outcome["winner"] == player
    )


def opponent_has_immediate_win(
    board,
    player,
):

    opponent = (
        2 if player == 1 else 1
    )

    return any(
        move_results_in_win(
            board,
            move,
            opponent,
        )
        for move in get_all_moves(
            board,
            opponent,
        )
    )


def progress_score(
    board,
    player,
):

    counts = wins_including_cell(
        board,
        player,
        None,
    )

    groups = (
        engine.config
        .player_pattern_groups[player]
    )

    total_progress = 0.0
    best_progress = 0.0
    improved_patterns = 0

    for group in groups.values():

        for pattern_name, needed in (
            group["patterns"].items()
        ):

            if needed <= 0:
                continue

            actual = counts.get(
                pattern_name,
                0,
            )

            progress = min(
                actual / needed,
                1.0,
            )

            total_progress += progress

            best_progress = max(
                best_progress,
                progress,
            )

            if actual > 0:
                improved_patterns += 1

    return (
        total_progress,
        best_progress,
        improved_patterns,
    )


def count_winning_moves(
    board,
    player,
):

    wins = 0

    for move in get_all_moves(
        board,
        player,
    ):

        if move_results_in_win(
            board,
            move,
            player,
        ):
            wins += 1

    return wins


def evaluate_position(
    board,
    player,
):

    score = 0

    (
        total_progress,
        best_progress,
        improved_patterns,
    ) = progress_score(
        board,
        player,
    )

    score += (
        total_progress * 100
    )

    score += (
        best_progress * 500
    )

    score += (
        improved_patterns * 50
    )

    winning_moves = count_winning_moves(
        board,
        player,
    )

    score += (
        winning_moves * 1000
    )

    if winning_moves >= 2:
        score += 10000

    return score


def choose_move(
    board,
    player,
    legal_moves,
    rng,
    seen_states=None,
):

    if not legal_moves:
        return None

    if seen_states is None:
        seen_states = set()

    opponent = (
        2 if player == 1 else 1
    )

    winning_moves = []
    blocking_moves = []

    opponent_winning_now = any(
        move_results_in_win(
            board,
            opp_move,
            opponent,
        )
        for opp_move in get_all_moves(
            board,
            opponent,
        )
    )

    scored_moves = []

    for move in legal_moves:

        next_board = copy_board(
            board
        )

        apply_move(
            next_board,
            move,
        )

        outcome = resolve_move_outcome(
            next_board,
            player,
            move[1],
        )

        # ALWAYS TAKE WIN

        if (
            outcome["status"] == "win"
            and outcome["winner"] == player
        ):
            winning_moves.append(
                move
            )
            continue

        # NEVER ACCEPT DRAW

        if outcome["status"] == "draw":
            continue

        # NEVER SELF SABOTAGE

        if (
            outcome["status"] == "win"
            and outcome["winner"] != player
        ):
            continue

        # BLOCK IMMEDIATE LOSS

        blocks_loss = (
            not opponent_has_immediate_win(
                next_board,
                player,
            )
        )

        if (
            opponent_winning_now
            and blocks_loss
        ):
            blocking_moves.append(
                move
            )

        score = evaluate_position(
            next_board,
            player,
        )

        next_state = board_key(
            next_board,
            opponent,
        )

        if next_state in seen_states:
            score -= 100

        scored_moves.append(
            (
                move,
                score,
            )
        )

    # WIN NOW

    if winning_moves:
        return winning_moves[0]

    # MUST BLOCK

    if (
        opponent_winning_now
        and blocking_moves
    ):
        return blocking_moves[0]

    if not scored_moves:
        return rng.choice(legal_moves)

    scored_moves.sort(
        key=lambda x: x[1],
        reverse=True,
    )

    # ALWAYS PLAY BEST MOVE

    return scored_moves[0][0]