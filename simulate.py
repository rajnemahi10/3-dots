import argparse
import random
from collections import Counter

from engine import check_win, config, create_initial_board, size


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

    for dr, dc in directions:
        nr = row + dr
        nc = col + dc

        if 0 <= nr < board_size and 0 <= nc < board_size and board[nr][nc] == 0:
            moves.append((nr, nc))

    return moves


def list_all_moves(board, player):
    all_moves = []

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] != player:
                continue

            for next_row, next_col in generate_moves(board, row, col):
                all_moves.append(((row, col), (next_row, next_col)))

    return all_moves


def apply_move(board, move, player):
    (src_row, src_col), (dst_row, dst_col) = move
    board[dst_row][dst_col] = player
    board[src_row][src_col] = 0


def copy_board(board):
    return [row[:] for row in board]


def board_key(board, player):
    return (
        player,
        tuple(tuple(row) for row in board),
    )


def has_win(board, player):
    return any(
        check_win(board, player, pattern_name)
        for pattern_name in config.player_patterns[player]
    )


def move_results_in_win(board, move, player):
    next_board = copy_board(board)
    apply_move(next_board, move, player)
    return has_win(next_board, player)


def opponent_has_immediate_win(board, player):
    opponent = 2 if player == 1 else 1

    for move in list_all_moves(board, opponent):
        if move_results_in_win(board, move, opponent):
            return True

    return False


def choose_random_move(board, player, legal_moves, rng, seen_states):
    return rng.choice(legal_moves)


def choose_heuristic_move(board, player, legal_moves, rng, seen_states):
    winning_moves = []
    blocking_moves = []
    safe_unseen_moves = []
    safe_seen_moves = []
    risky_unseen_moves = []
    risky_seen_moves = []
    opponent = 2 if player == 1 else 1

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

        if any(move_results_in_win(board, opp_move, opponent) for opp_move in list_all_moves(board, opponent)):
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


def choose_move(board, player, legal_moves, rng, seen_states, strategy):
    if strategy == "heuristic":
        return choose_heuristic_move(board, player, legal_moves, rng, seen_states)

    return choose_random_move(board, player, legal_moves, rng, seen_states)


def simulate_game(rng, max_moves, player_1_strategy, player_2_strategy, layout):
    board = create_initial_board(layout)
    current_player = 1
    moves_played = 0
    branching_sum = 0
    branching_samples = 0
    seen_states = {board_key(board, current_player)}
    repeated_state_hits = 0
    repeated_state_found = False

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
            }

        strategy = player_1_strategy if current_player == 1 else player_2_strategy
        move = choose_move(board, current_player, legal_moves, rng, seen_states, strategy)
        apply_move(board, move, current_player)
        moves_played += 1

        if has_win(board, current_player):
            return {
                "winner": current_player,
                "moves": moves_played,
                "draw": False,
                "branching_sum": branching_sum,
                "branching_samples": branching_samples,
                "repeated_state_hits": repeated_state_hits,
                "repeated_state_found": repeated_state_found,
            }

        current_player = 2 if current_player == 1 else 1
        state = board_key(board, current_player)

        if state in seen_states:
            repeated_state_hits += 1
            repeated_state_found = True
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
    }


def simulate_many(num_games, max_moves, seed, player_1_strategy, player_2_strategy, layout):
    rng = random.Random(seed)
    results = []

    for _ in range(num_games):
        results.append(simulate_game(rng, max_moves, player_1_strategy, player_2_strategy, layout))

    total_games = len(results)
    wins = Counter(result["winner"] for result in results)
    draws = sum(1 for result in results if result["draw"])
    total_moves = sum(result["moves"] for result in results)
    branching_sum = sum(result["branching_sum"] for result in results)
    branching_samples = sum(result["branching_samples"] for result in results)
    repeated_games = sum(1 for result in results if result["repeated_state_found"])
    repeated_hits = sum(result["repeated_state_hits"] for result in results)

    print(f"games: {total_games}")
    print(f"board_size: 3")
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


def main():
    parser = argparse.ArgumentParser(description="Simulate Pattern Game many times.")
    parser.add_argument("-n", "--games", type=int, default=1000)
    parser.add_argument("--max-moves", type=int, default=200)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--layout", choices=["corners", "staggered"], default="corners")
    parser.add_argument(
        "--player-1-strategy",
        choices=["random", "heuristic"],
        default="random",
    )
    parser.add_argument(
        "--player-2-strategy",
        choices=["random", "heuristic"],
        default="random",
    )
    args = parser.parse_args()

    simulate_many(
        args.games,
        args.max_moves,
        args.seed,
        args.player_1_strategy,
        args.player_2_strategy,
        args.layout,
    )


if __name__ == "__main__":
    main()
