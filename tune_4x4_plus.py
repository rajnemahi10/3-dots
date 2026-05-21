import argparse

from simulate_4x4 import simulate_game


SIZE = 4


def create_base_board(layout):
    board = [[0] * SIZE for _ in range(SIZE)]

    if layout == "corners":
        board[0][0] = 1
        board[0][3] = 1
        board[3][0] = 2
        board[3][3] = 2
    elif layout == "middle":
        board[1][1] = 1
        board[2][2] = 1
        board[1][2] = 2
        board[2][1] = 2
    else:
        raise ValueError(f"Unknown base layout: {layout}")

    return board


def board_with_specials(layout, red_pos, green_pos):
    board = create_base_board(layout)
    red_row, red_col = red_pos
    green_row, green_col = green_pos

    if board[red_row][red_col] != 0 or board[green_row][green_col] != 0:
        raise ValueError("Special piece overlaps an existing piece")

    board[red_row][red_col] = 3
    board[green_row][green_col] = 4
    return board


def board_to_layout_string(board):
    rows = []

    for row in board:
        rows.append(" ".join(str(cell) for cell in row))

    return " / ".join(rows)


def candidate_pairs(layout):
    base = create_base_board(layout)
    pairs = []

    for row in range(SIZE):
        for col in range(SIZE):
            mirror = (SIZE - 1 - row, SIZE - 1 - col)

            if (row, col) > mirror:
                continue

            if base[row][col] != 0 or base[mirror[0]][mirror[1]] != 0:
                continue

            pairs.append(((row, col), mirror))

    return pairs


def simulate_from_board(board, games, max_moves, seed, player_1_strategy, player_2_strategy):
    import random

    rng = random.Random(seed)
    results = []

    for _ in range(games):
        results.append(
            simulate_game(
                rng,
                max_moves,
                player_1_strategy,
                player_2_strategy,
                layout=None,
                initial_board=board,
            )
        )

    total_games = len(results)
    player_1_wins = sum(1 for result in results if result["winner"] == 1)
    player_2_wins = sum(1 for result in results if result["winner"] == 2)
    draws = sum(1 for result in results if result["draw"])
    avg_moves = sum(result["moves"] for result in results) / total_games
    avg_branching = sum(result["branching_sum"] for result in results) / sum(
        result["branching_samples"] for result in results
    )
    repeated_games = sum(1 for result in results if result["repeated_state_found"]) / total_games

    return {
        "p1_win_rate": player_1_wins / total_games,
        "p2_win_rate": player_2_wins / total_games,
        "draw_rate": draws / total_games,
        "avg_moves": avg_moves,
        "avg_branching": avg_branching,
        "repeated_games": repeated_games,
    }


def balance_score(heuristic_metrics):
    return (
        abs(heuristic_metrics["p1_win_rate"] - heuristic_metrics["p2_win_rate"]),
        heuristic_metrics["draw_rate"],
        heuristic_metrics["repeated_games"],
    )


def main():
    parser = argparse.ArgumentParser(description="Rank symmetric 4x4 plus-piece placements.")
    parser.add_argument("--layout", choices=["corners", "middle"], required=True)
    parser.add_argument("--rr-games", type=int, default=200)
    parser.add_argument("--hh-games", type=int, default=80)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--max-moves", type=int, default=300)
    args = parser.parse_args()

    rows = []

    for red_pos, green_pos in candidate_pairs(args.layout):
        board = board_with_specials(args.layout, red_pos, green_pos)
        rr = simulate_from_board(
            board,
            args.rr_games,
            args.max_moves,
            args.seed,
            "random",
            "random",
        )
        hh = simulate_from_board(
            board,
            args.hh_games,
            args.max_moves,
            args.seed,
            "heuristic",
            "heuristic",
        )

        rows.append(
            {
                "red_special": red_pos,
                "green_special": green_pos,
                "board": board_to_layout_string(board),
                "rr": rr,
                "hh": hh,
            }
        )

    rows.sort(key=lambda row: balance_score(row["hh"]))

    print(f"layout: {args.layout}")
    print(f"candidates_tested: {len(rows)}")

    for index, row in enumerate(rows, start=1):
        print(f"rank: {index}")
        print(f"red_special: {row['red_special']}")
        print(f"green_special: {row['green_special']}")
        print(f"board: {row['board']}")
        print(
            "heuristic_vs_heuristic: "
            f"p1={row['hh']['p1_win_rate']:.4f} "
            f"p2={row['hh']['p2_win_rate']:.4f} "
            f"draw={row['hh']['draw_rate']:.4f} "
            f"avg_moves={row['hh']['avg_moves']:.4f} "
            f"avg_branching={row['hh']['avg_branching']:.4f} "
            f"repeated_games={row['hh']['repeated_games']:.4f}"
        )
        print(
            "random_vs_random: "
            f"p1={row['rr']['p1_win_rate']:.4f} "
            f"p2={row['rr']['p2_win_rate']:.4f} "
            f"draw={row['rr']['draw_rate']:.4f} "
            f"avg_moves={row['rr']['avg_moves']:.4f} "
            f"avg_branching={row['rr']['avg_branching']:.4f} "
            f"repeated_games={row['rr']['repeated_games']:.4f}"
        )


if __name__ == "__main__":
    main()
