from modular_gui.board import (
    apply_move,
    canonical_board_cache_key,
    get_all_moves,
    resolve_move_outcome,
    wins_including_cell,
)
import modular_gui.engine as engine

# ----------------------------------------
# CACHES
# ----------------------------------------

MOVE_WIN_CACHE = {}
IMMEDIATE_WIN_CACHE = {}
POSITION_CACHE = {}


def clear_cache():

    MOVE_WIN_CACHE.clear()
    IMMEDIATE_WIN_CACHE.clear()
    POSITION_CACHE.clear()


# ----------------------------------------
# HELPERS
# ----------------------------------------

def copy_board(board):
    return [row[:] for row in board]


def board_signature(board):

    return tuple(
        tuple(row)
        for row in board
    )


def board_key(board, player):

    return (
        player,
        tuple(
            tuple(row)
            for row in board
        ),
    )


def evaluate_position(
    board,
    player,
):

    key = (
        player,
        canonical_board_cache_key(
            board
        ),
    )

    cached = POSITION_CACHE.get(
        key
    )

    if cached is not None:
        return cached

    opponent = (
        2 if player == 1 else 1
    )

    player_counts = wins_including_cell(
        board,
        player,
        None,
    )
    opponent_counts = wins_including_cell(
        board,
        opponent,
        None,
    )

    def progress_score(target_player, counts):
        total = 0.0
        best = 0.0
        completed = 0
        groups = (
            engine.config
            .player_pattern_groups[target_player]
        )

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
                total += progress
                best = max(
                    best,
                    progress,
                )

                if actual >= needed:
                    completed += 1

        return total, best, completed

    (
        player_progress,
        player_best,
        player_completed,
    ) = progress_score(
        player,
        player_counts,
    )

    (
        opponent_progress,
        opponent_best,
        opponent_completed,
    ) = progress_score(
        opponent,
        opponent_counts,
    )

    player_moves = get_all_moves(
        board,
        player,
    )
    opponent_moves = get_all_moves(
        board,
        opponent,
    )

    player_wins = sum(
        1
        for move in player_moves
        if move_results_in_win(
            board,
            move,
            player,
        )
    )
    opponent_wins = sum(
        1
        for move in opponent_moves
        if move_results_in_win(
            board,
            move,
            opponent,
        )
    )

    score = int(
        200
        * (
            player_wins
            - opponent_wins
        )
        + 70
        * (
            player_progress
            - opponent_progress
        )
        + 120
        * (
            player_best
            - opponent_best
        )
        + 180
        * (
            player_completed
            - opponent_completed
        )
        + 10
        * (
            len(player_moves)
            - len(opponent_moves)
        )
    )

    POSITION_CACHE[key] = score
    return score


# ----------------------------------------
# WIN CHECK CACHE
# ----------------------------------------

def move_results_in_win(
    board,
    move,
    player,
):

    key = (
        player,
        move,
        board_signature(board),
    )

    cached = MOVE_WIN_CACHE.get(
        key
    )

    if cached is not None:
        return cached

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

    result = (
        outcome["status"] == "win"
        and outcome["winner"] == player
    )

    MOVE_WIN_CACHE[key] = result

    return result


def opponent_has_immediate_win(
    board,
    player,
):

    key = (
        player,
        board_signature(board),
    )

    cached = IMMEDIATE_WIN_CACHE.get(
        key
    )

    if cached is not None:
        return cached

    opponent = (
        2 if player == 1 else 1
    )

    result = any(
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

    IMMEDIATE_WIN_CACHE[key] = result

    return result


# ----------------------------------------
# MAIN HEURISTIC
# ----------------------------------------

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

    winning_moves = []
    drawing_moves = []
    move_buckets = {
        "blocking": [],
        "safe_unseen": [],
        "safe_seen": [],
        "risky_unseen": [],
        "risky_seen": [],
    }

    opponent = (
        2 if player == 1 else 1
    )

    opponent_winning_now = any(
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

    for move in legal_moves:

        next_board = copy_board(
            board
        )

        apply_move(
            next_board,
            move,
        )

        next_state = board_key(
            next_board,
            opponent,
        )

        is_seen = (
            next_state in seen_states
        )

        outcome = resolve_move_outcome(
            next_board,
            player,
            move[1],
        )

        if outcome["status"] == "win":

            if (
                outcome["winner"]
                == player
            ):
                winning_moves.append((
                    move,
                    evaluate_position(
                        next_board,
                        player,
                    ),
                ))

            elif is_seen:
                move_buckets[
                    "risky_seen"
                ].append((
                    move,
                    evaluate_position(
                        next_board,
                        player,
                    ),
                ))

            else:
                move_buckets[
                    "risky_unseen"
                ].append((
                    move,
                    evaluate_position(
                        next_board,
                        player,
                    ),
                ))

            continue

        if outcome["status"] == "draw":

            drawing_moves.append((
                move,
                evaluate_position(
                    next_board,
                    player,
                ),
            ))

            continue

        if opponent_has_immediate_win(
            next_board,
            player,
        ):

            if is_seen:
                move_buckets[
                    "risky_seen"
                ].append((
                    move,
                    evaluate_position(
                        next_board,
                        player,
                    ),
                ))

            else:
                move_buckets[
                    "risky_unseen"
                ].append((
                    move,
                    evaluate_position(
                        next_board,
                        player,
                    ),
                ))

            continue

        score = evaluate_position(
            next_board,
            player,
        )

        if opponent_winning_now:
            move_buckets[
                "blocking"
            ].append((
                move,
                score,
            ))

        if is_seen:
            move_buckets[
                "safe_seen"
            ].append((
                move,
                score,
            ))

        else:
            move_buckets[
                "safe_unseen"
            ].append((
                move,
                score,
            ))

    def best_scored_move(scored_moves):
        best_score = max(
            score
            for _move, score in scored_moves
        )
        best_moves = [
            move
            for move, score in scored_moves
            if score == best_score
        ]
        return rng.choice(best_moves)

    if winning_moves:
        return best_scored_move(
            winning_moves
        )

    if drawing_moves:
        return best_scored_move(
            drawing_moves
        )

    if move_buckets["blocking"]:
        return best_scored_move(
            move_buckets["blocking"]
        )

    if move_buckets["safe_unseen"]:
        return best_scored_move(
            move_buckets["safe_unseen"]
        )

    if move_buckets["safe_seen"]:
        return best_scored_move(
            move_buckets["safe_seen"]
        )

    if move_buckets["risky_unseen"]:
        return best_scored_move(
            move_buckets["risky_unseen"]
        )

    return best_scored_move(
        move_buckets["risky_seen"]
    )
