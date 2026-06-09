from functools import lru_cache

import modular_gui.engine as engine

from modular_gui.board import (
    apply_move,
    canonical_board_cache_key,
    canonical_state_cache_key,
    freeze_board,
    get_all_moves,
    resolve_move_outcome,
    rules_signature,
    thaw_board,
)

SEARCH_STATS = {
    "nodes": 0,
    "states": 0,
    "legal_moves": 0,
}

DEFAULT_MINIMAX_DEPTH = 3
INF = 10 ** 9

TRANSPOSITION_CACHE = {}
ROOT_MOVE_CACHE = {}


def copy_board(board):
    return [row[:] for row in board]


def _search_context():
    return {
        "win_cache": {},
        "outcome_cache": {},
        "eval_cache": {},
        "move_order_cache": {},
        "counts_cache": {},
    }


def cached_outcome(
    board,
    player,
    moved_to,
    search_context=None,
):
    if search_context is None:
        return resolve_move_outcome(
            board,
            player,
            moved_to,
        )

    key = (
        canonical_state_cache_key(
            board,
            player=player,
            moved_cell=moved_to,
        )
    )

    cached = search_context[
        "outcome_cache"
    ].get(key)

    if cached is not None:
        return cached

    outcome = resolve_move_outcome(
        board,
        player,
        moved_to,
    )

    search_context[
        "outcome_cache"
    ][key] = outcome

    return outcome


def move_results_in_win(
    board,
    move,
    player,
    search_context=None,
):
    board_key = freeze_board(board)
    cache_key = canonical_state_cache_key(
        board,
        player=player,
        move=move,
    )

    if (
        search_context is not None
        and cache_key
        in search_context["win_cache"]
    ):
        return search_context[
            "win_cache"
        ][cache_key]

    next_board = copy_board(board)
    apply_move(next_board, move)
    outcome = cached_outcome(
        next_board,
        player,
        move[1],
        search_context,
    )
    result = (
        outcome["status"] == "win"
        and outcome["winner"] == player
    )

    if search_context is not None:
        search_context[
            "win_cache"
        ][cache_key] = result

    return result


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


def _counts_for_player(
    board,
    player,
    search_context,
):
    key = (
        canonical_board_cache_key(
            board
        ),
        player,
    )

    cached = search_context[
        "counts_cache"
    ].get(key)

    if cached is not None:
        return cached

    from modular_gui.board import (
        wins_including_cell,
    )

    counts = wins_including_cell(
        board,
        player,
        None,
    )
    search_context[
        "counts_cache"
    ][key] = counts
    return counts


def _pattern_progress_score(
    board,
    player,
    search_context,
):
    counts = _counts_for_player(
        board,
        player,
        search_context,
    )

    groups = (
        engine
        .config
        .player_pattern_groups[player]
    )

    total_progress = 0.0
    best_progress = 0.0
    completed_targets = 0
    active_targets = 0

    for group in groups.values():

        for pattern_name, needed in (
            group["patterns"].items()
        ):

            if needed <= 0:
                continue

            active_targets += 1
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

            if actual >= needed:
                completed_targets += 1

    return (
        total_progress,
        best_progress,
        completed_targets,
        active_targets,
    )


def evaluate_board(
    board,
    player,
    search_context=None,
):
    if search_context is not None:
        key = (
            canonical_board_cache_key(
                board
            ),
            player,
        )

        cached = search_context[
            "eval_cache"
        ].get(key)

        if cached is not None:
            return cached

        score = _evaluate_board_core(
            board,
            player,
            search_context,
        )

        search_context[
            "eval_cache"
        ][key] = score

        return score

    return _cached_evaluate_board(
        canonical_board_cache_key(board),
        player,
        rules_signature(),
    )


@lru_cache(maxsize=8192)
def _cached_evaluate_board(
    canonical_board_key,
    player,
    config_key,
):
    del config_key

    board = thaw_board(
        canonical_board_key[1]
    )
    return _evaluate_board_core(
        board,
        player,
        None,
    )


def _evaluate_board_core(
    board,
    player,
    search_context,
):
    opponent = 2 if player == 1 else 1

    player_moves = get_all_moves(
        board,
        player,
    )

    opponent_moves = get_all_moves(
        board,
        opponent,
    )

    player_winning_moves = sum(
        1
        for move in player_moves
        if move_results_in_win(
            board,
            move,
            player,
            search_context,
        )
    )

    opponent_winning_moves = sum(
        1
        for move in opponent_moves
        if move_results_in_win(
            board,
            move,
            opponent,
            search_context,
        )
    )

    (
        player_progress,
        player_best,
        player_completed,
        player_targets,
    ) = _pattern_progress_score(
        board,
        player,
        search_context,
    )

    (
        opponent_progress,
        opponent_best,
        opponent_completed,
        opponent_targets,
    ) = _pattern_progress_score(
        board,
        opponent,
        search_context,
    )

    return int(
        180
        * (
            player_winning_moves
            - opponent_winning_moves
        )
        + 12
        * (
            len(player_moves)
            - len(opponent_moves)
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
        + 200
        * (
            player_completed
            - opponent_completed
        )
        + 25
        * (
            player_targets
            - opponent_targets
        )
    )

def clear_cache():
    TRANSPOSITION_CACHE.clear()
    ROOT_MOVE_CACHE.clear()
    _cached_evaluate_board.cache_clear()


def cache_report():
    return {
        "transposition_entries": len(
            TRANSPOSITION_CACHE
        ),
        "evaluate_board": (
            _cached_evaluate_board
            .cache_info()
        ),
    }


def minimax_score(
    board,
    root_player,
    current_player,
    depth,
    alpha,
    beta,
    last_mover,
    last_move_to,
    search_context,
):

    SEARCH_STATS["nodes"] += 1
    cache_key = canonical_state_cache_key(
        board,
        moved_cell=last_move_to,
        extra=(
            root_player,
            current_player,
            depth,
            last_mover,
            rules_signature(),
        ),
    )

    cached_score = (
        TRANSPOSITION_CACHE.get(
            cache_key
        )
    )

    if cached_score is not None:
        return cached_score

    opponent = 2 if current_player == 1 else 1
    outcome = cached_outcome(
        board,
        last_mover,
        last_move_to,
        search_context,
    )
    terminal_score = score_outcome(outcome, root_player, depth)

    if terminal_score is not None:
        TRANSPOSITION_CACHE[
            cache_key
        ] = terminal_score
        return terminal_score

    if depth == 0:
        score = evaluate_board(
            board,
            root_player,
            search_context,
        )
        TRANSPOSITION_CACHE[
            cache_key
        ] = score
        return score

    raw_moves = get_all_moves(
        board,
        current_player,
    )

    SEARCH_STATS["states"] += 1
    SEARCH_STATS["legal_moves"] += len(raw_moves)

    legal_moves = order_moves(
        board,
        raw_moves,
        current_player,
        root_player,
        search_context,
    )

    if not legal_moves:
        TRANSPOSITION_CACHE[
            cache_key
        ] = 0
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
                search_context,
            )

            value = max(value, score)
            alpha = max(alpha, value)

            if beta <= alpha:
                break

        TRANSPOSITION_CACHE[
            cache_key
        ] = value
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
            search_context,
        )

        value = min(value, score)
        beta = min(beta, value)

        if beta <= alpha:
            break

    TRANSPOSITION_CACHE[
        cache_key
    ] = value

    return value


def _move_order_score(
    board,
    move,
    current_player,
    root_player,
    search_context,
):
    cache_key = canonical_state_cache_key(
        board,
        move=move,
        extra=(
            current_player,
            root_player,
        ),
    )

    cached = search_context[
        "move_order_cache"
    ].get(cache_key)

    if cached is not None:
        return cached

    next_board = copy_board(board)
    apply_move(next_board, move)

    outcome = cached_outcome(
        next_board,
        current_player,
        move[1],
        search_context,
    )

    outcome_score = score_outcome(
        outcome,
        root_player,
        DEFAULT_MINIMAX_DEPTH,
    )

    if outcome_score is not None:
        score = outcome_score
    else:
        score = evaluate_board(
            next_board,
            root_player,
            search_context,
        )

    search_context[
        "move_order_cache"
    ][cache_key] = score

    return score


def order_moves(
    board,
    legal_moves,
    current_player,
    root_player,
    search_context,
):
    reverse = (
        current_player == root_player
    )

    return sorted(
        legal_moves,
        key=lambda move: _move_order_score(
            board,
            move,
            current_player,
            root_player,
            search_context,
        ),
        reverse=reverse,
    )


def search_depth_for_position(
    legal_moves,
):
    move_count = len(legal_moves)

    if move_count <= 8:
        return 5

    if move_count <= 14:
        return 4

    return DEFAULT_MINIMAX_DEPTH


def choose_move(board, player, legal_moves, rng, seen_states=None):
    if not legal_moves:
        return None

    if seen_states is None:
        seen_states = set()

    best_score = None
    best_moves = []
    opponent = 2 if player == 1 else 1
    search_context = _search_context()
    depth = search_depth_for_position(
        legal_moves
    )

    ordered_moves = order_moves(
        board,
        legal_moves,
        player,
        player,
        search_context,
    )

    for move in ordered_moves:
        next_board = copy_board(board)
        apply_move(next_board, move)

        outcome = cached_outcome(
            next_board,
            player,
            move[1],
            search_context,
        )
        score = score_outcome(
            outcome,
            player,
            depth,
        )

        if score is None:
            root_cache_key = (
                player,
                move,
                depth,
                canonical_board_cache_key(
                    board
                ),
                rules_signature(),
            )

            cached_score = ROOT_MOVE_CACHE.get(
                root_cache_key
            )

            if cached_score is not None:

                score = cached_score

            else:

                score = minimax_score(
                    next_board,
                    player,
                    opponent,
                    depth - 1,
                    -INF,
                    INF,
                    player,
                    move[1],
                    search_context,
                )

                ROOT_MOVE_CACHE[
                    root_cache_key
                ] = score

        if state_key(next_board, opponent) in seen_states:
            score -= 20

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return rng.choice(best_moves)
