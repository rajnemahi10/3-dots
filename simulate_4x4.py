import argparse
import random
from collections import Counter
from engine_4x4 import has_any_win

from engine_4x4 import (
    check_win,
    config,
    create_initial_board,
    get_active_joker_positions,
    is_joker,
    is_long_range_piece,
    is_player_piece,
)


def generate_moves(board, row, col):
    moves = []
    directions = [
        (-1, 0),
        (1, 0),
        (0, -1),
        (0, 1),
        (-1, -1),
        (-1, 1),
        (1, -1),
        (1, 1),
    ]

    board_size = len(board)
    max_step = 2 if is_long_range_piece(board[row][col]) else 1

    for dr, dc in directions:
        for step in range(1, max_step + 1):
            nr = row + dr * step
            nc = col + dc * step

            if 0 <= nr < board_size and 0 <= nc < board_size and board[nr][nc] == 0:
                moves.append((nr, nc))

    return moves


def list_all_moves(board, player):
    all_moves = []

    for row in range(len(board)):
        for col in range(len(board[row])):
            if not is_player_piece(board[row][col], player) or is_joker(board[row][col]):
                continue

            for next_row, next_col in generate_moves(board, row, col):
                all_moves.append(((row, col), (next_row, next_col)))

    return all_moves


def apply_move(board, move, player):
    (src_row, src_col), (dst_row, dst_col) = move
    board[dst_row][dst_col] = board[src_row][src_col]
    board[src_row][src_col] = 0


def copy_board(board):
    return [row[:] for row in board]


def format_cell(cell):
    symbols = {
        0: ".",
        1: "R",
        2: "G",
        3: "R2",
        4: "G2",
        9: "J",
    }
    return symbols.get(cell, str(cell))


def format_board(board):
    rows = []

    for row in board:
        rows.append(" ".join(f"{format_cell(cell):>2}" for cell in row))

    return "\n".join(rows)


def format_board_with_outside_jokers(board):
    joker_positions = get_active_joker_positions()
    rows = []

    for row in range(-1, len(board) + 1):
        cells = []

        for col in range(-1, len(board[0]) + 1):
            if 0 <= row < len(board) and 0 <= col < len(board[0]):
                cell = format_cell(board[row][col])
            elif (row, col) in joker_positions:
                cell = "J"
            else:
                cell = " "

            cells.append(f"{cell:>2}")

        rows.append(" ".join(cells))

    return "\n".join(rows)


def board_key(board, player):
    return (
        player,
        tuple(tuple(row) for row in board),
    )


def has_win(board, player):
    return has_any_win(board, player)


def move_results_in_win(board, move, player):
    next_board = copy_board(board)
    apply_move(next_board, move, player)
    return has_win(next_board, player)


def opponent_has_immediate_win(board, player):

    opponent = 2 if player == 1 else 1

    return has_win(board, opponent)


def choose_random_move(board, legal_moves, rng):
    return rng.choice(legal_moves)


def choose_heuristic_move(board, player, legal_moves, rng, seen_states):
    winning_moves = []
    blocking_moves = []
    safe_unseen_moves = []
    safe_seen_moves = []
    risky_unseen_moves = []
    risky_seen_moves = []
    opponent = 2 if player == 1 else 1
    opponent_winning_now = any(
        move_results_in_win(board, opp_move, opponent)
        for opp_move in list_all_moves(board, opponent)
    )

    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move, player)
        next_state = board_key(next_board, opponent)
        is_seen = next_state in seen_states

        if has_win(next_board, player):
            winning_moves.append(move)
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

    if blocking_moves:
        non_losing_blocks = []

        for move in blocking_moves:
            next_board = copy_board(board)
            apply_move(next_board, move, player)
            if not opponent_has_immediate_win(next_board, player):
                non_losing_blocks.append(move)

        if non_losing_blocks:
            return rng.choice(non_losing_blocks)
        return rng.choice(blocking_moves)

    if safe_unseen_moves:
        return rng.choice(safe_unseen_moves)

    if safe_seen_moves:
        return rng.choice(safe_seen_moves)

    if risky_unseen_moves:
        return rng.choice(risky_unseen_moves)

    return rng.choice(risky_seen_moves)


def evaluate_board(board, player):
    opponent = 2 if player == 1 else 1

    if has_win(board, player):
        return 1000
    if has_win(board, opponent):
        return -1000

    player_winning_moves = sum(
        1 for move in list_all_moves(board, player) if move_results_in_win(board, move, player)
    )
    opponent_winning_moves = sum(
        1 for move in list_all_moves(board, opponent) if move_results_in_win(board, move, opponent)
    )
    player_mobility = len(list_all_moves(board, player))
    opponent_mobility = len(list_all_moves(board, opponent))

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

    legal_moves = list_all_moves(board, current_player)
    if not legal_moves:
        return 0

    if current_player == root_player:
        value = -10**9
        for move in legal_moves:
            next_board = copy_board(board)
            apply_move(next_board, move, current_player)
            if has_win(next_board, current_player):
                score = 1000 + depth
            else:
                score = minimax_score(next_board, root_player, opponent, depth - 1, alpha, beta)
            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value

    value = 10**9
    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move, current_player)
        if has_win(next_board, current_player):
            score = -1000 - depth
        else:
            score = minimax_score(next_board, root_player, opponent, depth - 1, alpha, beta)
        value = min(value, score)
        beta = min(beta, value)
        if beta <= alpha:
            break
    return value


def choose_minimax_move(board, player, legal_moves, rng, depth):
    best_score = None
    best_moves = []
    opponent = 2 if player == 1 else 1

    for move in legal_moves:
        next_board = copy_board(board)
        apply_move(next_board, move, player)
        if has_win(next_board, player):
            score = 1000 + depth
        else:
            score = minimax_score(next_board, player, opponent, depth - 1, -10**9, 10**9)

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return rng.choice(best_moves)


def rollout_result(board, next_player, root_player, rng, rollout_depth):
    current_player = next_player
    depth_left = rollout_depth

    while depth_left > 0:
        legal_moves = list_all_moves(board, current_player)
        if not legal_moves:
            return 0.0

        move = choose_heuristic_move(board, current_player, legal_moves, rng, set())
        apply_move(board, move, current_player)

        if has_win(board, current_player):
            return 1.0 if current_player == root_player else -1.0

        current_player = 2 if current_player == 1 else 1
        depth_left -= 1

    score = evaluate_board(board, root_player)
    if score > 0:
        return 0.25
    if score < 0:
        return -0.25
    return 0.0


def choose_monte_carlo_move(board, player, legal_moves, rng, rollouts, rollout_depth):
    best_score = None
    best_moves = []
    opponent = 2 if player == 1 else 1

    for move in legal_moves:
        total = 0.0

        for _ in range(rollouts):
            next_board = copy_board(board)
            apply_move(next_board, move, player)

            if has_win(next_board, player):
                total += 1.0
            else:
                total += rollout_result(next_board, opponent, player, rng, rollout_depth)

        score = total / rollouts

        if best_score is None or score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)

    return rng.choice(best_moves)


def choose_move(board, player, legal_moves, rng, seen_states, strategy, minimax_depth, monte_carlo_rollouts):
    if strategy == "heuristic":
        return choose_heuristic_move(board, player, legal_moves, rng, seen_states)
    if strategy == "minimax":
        return choose_minimax_move(board, player, legal_moves, rng, minimax_depth)
    if strategy == "monte_carlo":
        return choose_monte_carlo_move(
            board,
            player,
            legal_moves,
            rng,
            monte_carlo_rollouts,
            rollout_depth=max(4, minimax_depth * 2),
        )

    return choose_random_move(board, legal_moves, rng)


def simulate_game(
    rng,
    max_moves,
    player_1_strategy,
    player_2_strategy,
    layout,
    initial_board=None,
    trace=False,
    minimax_depth=3,
    monte_carlo_rollouts=24,
):
    if initial_board is None:
        board = create_initial_board(layout)
    else:
        board = copy_board(initial_board)
    current_player = 1
    moves_played = 0
    branching_sum = 0
    branching_samples = 0
    seen_states = {board_key(board, current_player)}
    repeated_state_hits = 0
    repeated_state_found = False
    history = []

    if trace:
        history.append(
            {
                "move_number": 0,
                "player": current_player,
                "move": None,
                "board": copy_board(board),
            }
        )

    while moves_played < max_moves:
        legal_moves = list_all_moves(board, current_player)
        branching_sum += len(legal_moves)
        branching_samples += 1

        if not legal_moves:
            return {
                "winner": 0,
                "moves": moves_played,
                "draw": True,
                "branching_sum": branching_sum,
                "branching_samples": branching_samples,
                "repeated_state_hits": repeated_state_hits,
                "repeated_state_found": repeated_state_found,
                "history": history,
            }

        strategy = player_1_strategy if current_player == 1 else player_2_strategy
        move = choose_move(
            board,
            current_player,
            legal_moves,
            rng,
            seen_states,
            strategy,
            minimax_depth,
            monte_carlo_rollouts,
        )
        apply_move(board, move, current_player)
        moves_played += 1

        if trace:
            history.append(
                {
                    "move_number": moves_played,
                    "player": current_player,
                    "move": move,
                    "board": copy_board(board),
                }
            )

        if has_win(board, current_player):
            return {
                "winner": current_player,
                "moves": moves_played,
                "draw": False,
                "branching_sum": branching_sum,
                "branching_samples": branching_samples,
                "repeated_state_hits": repeated_state_hits,
                "repeated_state_found": repeated_state_found,
                "history": history,
            }

        current_player = 2 if current_player == 1 else 1
        state = board_key(board, current_player)

        if state in seen_states:

            repeated_state_hits += 1
            repeated_state_found = True

            if repeated_state_hits >= 8:
                return {
                    "winner": 0,
                    "moves": moves_played,
                    "draw": True,
                    "branching_sum": branching_sum,
                    "branching_samples": branching_samples,
                    "repeated_state_hits": repeated_state_hits,
                    "repeated_state_found": True,
                    "history": history,
                }

        else:
            seen_states.add(state)
    

    return {
        "winner": 0,
        "moves": moves_played,
        "draw": True,
        "branching_sum": branching_sum,
        "branching_samples": branching_samples,
        "repeated_state_hits": repeated_state_hits,
        "repeated_state_found": repeated_state_found,
        "history": history,
    }


def simulate_many(
    num_games,
    max_moves,
    seed,
    player_1_strategy,
    player_2_strategy,
    layout,
    minimax_depth,
    monte_carlo_rollouts,
):
    rng = random.Random(seed)
    results = []

    for _ in range(num_games):
        results.append(
            simulate_game(
                rng,
                max_moves,
                player_1_strategy,
                player_2_strategy,
                layout,
                minimax_depth=minimax_depth,
                monte_carlo_rollouts=monte_carlo_rollouts,
            )
        )

    return results


def print_simulation_report(results, max_moves, seed, player_1_strategy, player_2_strategy, layout):
    total_games = len(results)
    wins = Counter(result["winner"] for result in results)
    draws = sum(1 for result in results if result["draw"])
    total_moves = sum(result["moves"] for result in results)
    branching_sum = sum(result["branching_sum"] for result in results)
    branching_samples = sum(result["branching_samples"] for result in results)
    repeated_games = sum(1 for result in results if result["repeated_state_found"])
    repeated_hits = sum(result["repeated_state_hits"] for result in results)

    print(f"games: {total_games}")
    sample_board = create_initial_board(layout)
    print(f"board_size: {len(sample_board)}")
    print(f"layout: {layout}")
    print(f"max_moves_per_game: {max_moves}")
    print(f"seed: {seed}")
    print(f"player_1_strategy: {player_1_strategy}")
    print(f"player_2_strategy: {player_2_strategy}")
    print(f"player_1_win_rate: {wins[1] / total_games:.4f}")
    print(f"player_2_win_rate: {wins[2] / total_games:.4f}")
    print(f"draw_rate: {draws / total_games:.4f}")
    print(f"average_moves: {total_moves / total_games:.4f}")
    print(f"average_branching_factor: {branching_sum / branching_samples:.4f}")
    print(f"games_with_repeated_states: {repeated_games / total_games:.4f}")
    print(f"average_repeated_state_hits: {repeated_hits / total_games:.4f}")


def print_game_outcomes(results):
    for index, result in enumerate(results, start=1):
        if result["draw"]:
            outcome = "draw"
        else:
            outcome = f"player_{result['winner']}_win"

        print(
            f"game_{index}: "
            f"outcome={outcome} "
            f"moves={result['moves']} "
            f"repeated_state_found={result['repeated_state_found']} "
            f"repeated_state_hits={result['repeated_state_hits']}"
        )


def print_traced_game(result):
    print("board_legend: .=empty R=red G=green R2=red_2step G2=green_2step J=joker")

    for state in result["history"]:
        if state["move"] is None:
            print("\ninitial_board:")
        else:
            (src_row, src_col), (dst_row, dst_col) = state["move"]
            print(
                f"\nmove_{state['move_number']}: "
                f"player_{state['player']} "
                f"({src_row},{src_col})->({dst_row},{dst_col})"
            )

        print(format_board_with_outside_jokers(state["board"]))

    if result["draw"]:
        print(f"\nresult: draw after {result['moves']} moves")
    else:
        print(f"\nresult: player_{result['winner']}_win after {result['moves']} moves")

# =========================================================
# ADVANCED BOARD SEARCHER
# =========================================================

import itertools


SEARCH_SHAPES = [

    [],

    [
        "triangle_up",
        "triangle_down",
    ],

    [
        "corner_ul",
        "corner_ur",
        "corner_dl",
        "corner_dr",
    ],

    [
        "triangle_up",
        "triangle_down",
        "triangle_left",
        "triangle_right",
    ],

    [
        "triangle_up",
        "triangle_down",
        "triangle_left",
        "triangle_right",
        "corner_ul",
        "corner_ur",
        "corner_dl",
        "corner_dr",
    ],
]


def random_start_board(
    size,
    normal_count,
    long_count,
    rng,
):

    board = [[0] * size for _ in range(size)]

    cells = [(r, c) for r in range(size) for c in range(size)]

    rng.shuffle(cells)

    for _ in range(normal_count):

        r, c = cells.pop()
        board[r][c] = 1

    for _ in range(normal_count):

        r, c = cells.pop()
        board[r][c] = 2

    for _ in range(long_count):

        r, c = cells.pop()
        board[r][c] = 3

    for _ in range(long_count):

        r, c = cells.pop()
        board[r][c] = 4

    return board


def board_has_immediate_win(board):

    return has_win(board, 1) or has_win(board, 2)


def evaluate_board_config(
    board,
    games,
    rng,
):

    results = []

    for _ in range(games):

        result = simulate_game(
            rng,
            max_moves=120,
            player_1_strategy="heuristic",
            player_2_strategy="heuristic",
            layout=None,
            initial_board=board,
        )

        results.append(result)

    total = len(results)

    p1 = sum(1 for r in results if r["winner"] == 1)
    p2 = sum(1 for r in results if r["winner"] == 2)
    draws = sum(1 for r in results if r["draw"])

    avg_moves = sum(r["moves"] for r in results) / total

    fairness = abs(p1 - p2) / total

    draw_rate = draws / total

    score = (
        fairness * 0.60
        + draw_rate * 0.30
        + (1 / max(avg_moves, 1)) * 0.10
    )

    return {
        "score": score,
        "p1_rate": p1 / total,
        "p2_rate": p2 / total,
        "draw_rate": draw_rate,
        "avg_moves": avg_moves,
    }


def search_best_boards():

    rng = random.Random(0)

    best_configs = []

    for size in range(4, 7):

        print()
        print("=" * 70)
        print(f"SEARCHING {size}x{size}")
        print("=" * 70)

        for normal_count in range(1, 5):

            for long_count in range(1, 4):

                for shape_set in SEARCH_SHAPES:

                    config.extra_shapes = shape_set

                    local_best = []

                    tested = 0

                    while tested < 8:

                        board = random_start_board(
                            size=size,
                            normal_count=normal_count,
                            long_count=long_count,
                            rng=rng,
                        )

                        if board_has_immediate_win(board):
                            continue

                        tested += 1

                        metrics = evaluate_board_config(
                            board,
                            games=6,
                            rng=rng,
                        )

                        local_best.append(
                            (
                                metrics["score"],
                                board,
                                metrics,
                                shape_set,
                                normal_count,
                                long_count,
                            )
                        )

                        local_best.sort(key=lambda x: x[0])

                        local_best = local_best[:3]

                    best_configs.extend(local_best)

        print()
        print(f"DONE SEARCHING {size}x{size}")

    best_configs.sort(key=lambda x: x[0])

    print()
    print("=" * 70)
    print("GLOBAL BEST CONFIGURATIONS")
    print("=" * 70)

    for rank, (
        score,
        board,
        metrics,
        shape_set,
        normal_count,
        long_count,
    ) in enumerate(best_configs[:20], start=1):

        print()
        print("-" * 50)
        print(f"GLOBAL RANK {rank}")
        print("-" * 50)

        print(f"normal_pieces={normal_count}")
        print(f"long_pieces={long_count}")
        print(f"shapes={shape_set}")

        print()

        for row in board:
            print(row)

        print()

        print(
            f"P1={metrics['p1_rate']:.3f} "
            f"P2={metrics['p2_rate']:.3f} "
            f"DRAW={metrics['draw_rate']:.3f} "
            f"AVG_MOVES={metrics['avg_moves']:.2f}"
        )

def main():

    parser = argparse.ArgumentParser(
        description="Simulate Pattern Game many times."
    )

    parser.add_argument(
        "-n",
        "--games",
        type=int,
        default=1000
    )

    parser.add_argument(
        "--max-moves",
        type=int,
        default=300
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=0
    )

    parser.add_argument(
        "--layout",
        choices=[
            "crossfire_4x4",
            "rotational_4x4",
            "center_warfare_5x5",
            "dual_pressure_5x5",
            "competitive_6x6",
        ],
        default="crossfire_4x4",
    )

    parser.add_argument(
        "--player-1-strategy",
        choices=[
            "random",
            "heuristic",
            "minimax",
            "monte_carlo",
        ],
        default="random",
    )

    parser.add_argument(
        "--player-2-strategy",
        choices=[
            "random",
            "heuristic",
            "minimax",
            "monte_carlo",
        ],
        default="random",
    )

    parser.add_argument(
        "--minimax-depth",
        type=int,
        default=3
    )

    parser.add_argument(
        "--monte-carlo-rollouts",
        type=int,
        default=24
    )

    parser.add_argument(
        "--show-games",
        action="store_true",
    )

    parser.add_argument(
        "--trace-game",
        action="store_true",
    )

    parser.add_argument(
        "--search-best-boards",
        action="store_true",
    )

    args = parser.parse_args()

    if args.search_best_boards:
        search_best_boards()
        return

    if args.trace_game:

        rng = random.Random(args.seed)

        result = simulate_game(
            rng,
            args.max_moves,
            args.player_1_strategy,
            args.player_2_strategy,
            args.layout,
            trace=True,
            minimax_depth=args.minimax_depth,
            monte_carlo_rollouts=args.monte_carlo_rollouts,
        )

        print_traced_game(result)

        return

    results = simulate_many(
        args.games,
        args.max_moves,
        args.seed,
        args.player_1_strategy,
        args.player_2_strategy,
        args.layout,
        args.minimax_depth,
        args.monte_carlo_rollouts,
    )

    print_simulation_report(
        results,
        args.max_moves,
        args.seed,
        args.player_1_strategy,
        args.player_2_strategy,
        args.layout,
    )

    if args.show_games:
        print_game_outcomes(results)


if __name__ == "__main__":
    main()