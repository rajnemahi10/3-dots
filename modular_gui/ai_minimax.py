from functools import lru_cache

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


DEFAULT_MINIMAX_DEPTH = 3
INF = 10 ** 9

TRANSPOSITION_CACHE = {}


def copy_board(board):
    return [row[:] for row in board]


def _search_context():
    return {
        "win_cache": {},
        "outcome_cache": {},
        "eval_cache": {},
        "move_order_cache": {},
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

    player_winning_moves = sum(
        1
        for move in get_all_moves(board, player)
        if move_results_in_win(
            board,
            move,
            player,
            search_context,
        )
    )

    opponent_winning_moves = sum(
        1
        for move in get_all_moves(board, opponent)
        if move_results_in_win(
            board,
            move,
            opponent,
            search_context,
        )
    )

    player_mobility = len(get_all_moves(board, player))
    opponent_mobility = len(get_all_moves(board, opponent))

    return (
        20 * (player_winning_moves - opponent_winning_moves)
        + (player_mobility - opponent_mobility)
    )


def clear_cache():
    TRANSPOSITION_CACHE.clear()
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

    legal_moves = order_moves(
        board,
        get_all_moves(
            board,
            current_player,
        ),
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
        root_mobility = len(
            get_all_moves(
                next_board,
                root_player,
            )
        )
        opponent_mobility = len(
            get_all_moves(
                next_board,
                2 if root_player == 1 else 1,
            )
        )
        score = (
            root_mobility
            - opponent_mobility
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


def choose_move(board, player, legal_moves, rng, seen_states=None):
    if not legal_moves:
        return None

    if seen_states is None:
        seen_states = set()

    best_score = None
    best_moves = []
    opponent = 2 if player == 1 else 1
    search_context = _search_context()

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
                search_context,
            )

        if state_key(next_board, opponent) in seen_states:
            score -= 1

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return rng.choice(best_moves)
