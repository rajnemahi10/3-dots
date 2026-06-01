import time



from modular_gui.ai_minimax import (
    minimax_score,
    copy_board,
    apply_move,
    _search_context,
    SEARCH_STATS,
)
INF = 10**9
TIME_LIMIT = 0.001


def reset_stats():

    SEARCH_STATS["nodes"] = 0
    SEARCH_STATS["states"] = 0
    SEARCH_STATS["legal_moves"] = 0


LAST_MOVE_STATS = {
    "nodes": 0,
    "depth": 0,
    "branching_factor": 0,
    "time_ms": 0,
}


def choose_move(
    board,
    player,
    legal_moves,
    rng,
    seen_states=None,
):
    if not legal_moves:
        return None

    reset_stats()

    opponent = (
        2 if player == 1 else 1
    )

    start_time = time.perf_counter()

    best_move = legal_moves[0]

    completed_depth = 0

    depth = 1

    while True:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        if elapsed >= TIME_LIMIT:
            break

        ctx = _search_context()

        current_best_score = -INF
        current_best_move = None

        for move in legal_moves:

            if (
                time.perf_counter()
                - start_time
                >= TIME_LIMIT
            ):
                break

            next_board = copy_board(board)

            apply_move(
                next_board,
                move,
            )

            score = minimax_score(
                next_board,
                player,
                opponent,
                depth,
                -INF,
                INF,
                player,
                move[1],
                ctx,
            )

            if score > current_best_score:

                current_best_score = score
                current_best_move = move

        if current_best_move is not None:

            best_move = current_best_move
            completed_depth = depth

        depth += 1

    elapsed_ms = (
        time.perf_counter()
        - start_time
    ) * 1000

    if SEARCH_STATS["states"] > 0:

        branching_factor = (
            SEARCH_STATS["legal_moves"]
            /
            SEARCH_STATS["states"]
        )

    else:

        branching_factor = 0

    LAST_MOVE_STATS["nodes"] = (
        SEARCH_STATS["nodes"]
    )

    LAST_MOVE_STATS["depth"] = (
        completed_depth
    )

    LAST_MOVE_STATS[
        "branching_factor"
    ] = branching_factor

    LAST_MOVE_STATS[
        "time_ms"
    ] = elapsed_ms

    return best_move