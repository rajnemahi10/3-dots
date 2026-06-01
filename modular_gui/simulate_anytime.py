import random
import time
from statistics import mean

from modular_gui.game import play_game

from modular_gui.players.anytime_ai import (
    SEARCH_STATS,
)

GAMES = 1000


def run_simulation():

    wins_p1 = 0
    wins_p2 = 0
    draws = 0

    move_counts = []
    move_times = []

    depths = []

    total_nodes = 0

    start = time.perf_counter()

    for game_idx in range(GAMES):

        result = play_game(
            player1="anytime",
            player2="anytime",
            seed=random.randint(
                0,
                1_000_000
            ),
        )

        winner = result["winner"]

        if winner == 1:
            wins_p1 += 1

        elif winner == 2:
            wins_p2 += 1

        else:
            draws += 1

        move_counts.append(
            result["moves"]
        )

        total_nodes += SEARCH_STATS[
            "nodes"
        ]

        depths.append(
            SEARCH_STATS[
                "depth_reached"
            ]
        )

        if (
            "avg_move_time"
            in result
        ):
            move_times.append(
                result["avg_move_time"]
            )

    elapsed = (
        time.perf_counter()
        - start
    )

    print()
    print("=" * 60)
    print("ANYTIME AI SIMULATION")
    print("=" * 60)

    print(
        f"Games Played: {GAMES}"
    )

    print(
        f"P1 Wins: {wins_p1}"
    )

    print(
        f"P2 Wins: {wins_p2}"
    )

    print(
        f"Draws: {draws}"
    )

    print()

    print(
        f"P1 Win Rate: "
        f"{100*wins_p1/GAMES:.2f}%"
    )

    print(
        f"P2 Win Rate: "
        f"{100*wins_p2/GAMES:.2f}%"
    )

    print(
        f"Draw Rate: "
        f"{100*draws/GAMES:.2f}%"
    )

    print()

    print(
        f"Average Moves: "
        f"{mean(move_counts):.2f}"
    )

    print(
        f"Min Moves: "
        f"{min(move_counts)}"
    )

    print(
        f"Max Moves: "
        f"{max(move_counts)}"
    )

    print()

    print(
        f"Average Depth Reached: "
        f"{mean(depths):.2f}"
    )

    print(
        f"Max Depth Reached: "
        f"{max(depths)}"
    )

    print()

    print(
        f"Total Nodes Expanded: "
        f"{total_nodes:,}"
    )

    if move_times:
        print(
            f"Average Move Time: "
            f"{1000*mean(move_times):.2f} ms"
        )

    print()

    print(
        f"Total Runtime: "
        f"{elapsed:.2f} sec"
    )

    print("=" * 60)


if __name__ == "__main__":
    run_simulation()