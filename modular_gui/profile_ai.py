import argparse
import cProfile
import io
import pstats
import random
import time
from modular_gui import anytime_ai
from modular_gui import fun_ai
from modular_gui import ai_mcts

from modular_gui import (
    ai_heuristic,
    ai_minimax,
    ai_mcts,
    ai_random,
)
from modular_gui.board import (
    apply_move,
    cache_report as board_cache_report,
    clear_caches as clear_board_caches,
    create_board,
    get_all_moves,
    resolve_move_outcome,
)


AI_HANDLERS = {
    "random": ai_random.choose_move,
    "heuristic": ai_heuristic.choose_move,
    "minimax": ai_minimax.choose_move,
    
    "anytime": anytime_ai.choose_move,
    "fun": fun_ai.choose_move,
    "mcts":ai_mcts.choose_move
}


def clone_board(board):

    return [
        row[:]
        for row in board
    ]


def clear_all_caches():

    clear_board_caches()
    ai_minimax.clear_cache()
    ai_mcts.clear_cache()


def print_cache_stats():

    print(
        "board_cache:",
        board_cache_report(),
    )

    print(
        "minimax_cache:",
        ai_minimax.cache_report(),
    )

    print(
        "mcts_cache:",
        ai_mcts.cache_report(),
    )


def run_profile_session(args):

    wins_p1 = 0
    wins_p2 = 0
    draws = 0

    game_lengths = []

    base_board = create_board(
        args.board_size
    )

    rng = random.Random(
        args.seed
    )

    total_moves = 0
    completed_games = 0

    start = time.perf_counter()

    for _ in range(args.games):

        moves_this_game = 0

        board = clone_board(base_board)
        current_player = 1
        seen_states = set()

        for _turn in range(args.max_turns):

            legal_moves = get_all_moves(
                board,
                current_player,
            )

            if not legal_moves:
                break

            strategy = (
                args.player_1
                if current_player == 1
                else args.player_2
            )

            chooser = AI_HANDLERS[
                strategy
            ]

            move = chooser(
                board,
                current_player,
                legal_moves,
                rng,
                seen_states,
            )

            if move is None:
                break

            apply_move(
                board,
                move,
            )

            moves_this_game += 1

            total_moves += 1

            outcome = (
                resolve_move_outcome(
                    board,
                    current_player,
                    move[1],
                )
            )

            if outcome["status"] == "win":

                if outcome["winner"] == 1:
                    wins_p1 += 1
                else:
                    wins_p2 += 1

                

                break

            elif outcome["status"] == "draw":

                draws += 1

                

                break

            current_player = (
                2
                if current_player == 1
                else 1
            )


        if moves_this_game > 0:
            game_lengths.append(
                moves_this_game
            )

        completed_games += 1

        

    elapsed = (
        time.perf_counter()
        - start
    )

    print(
        f"games={completed_games}"
    )
    print()

    print(
        f"P1 wins={wins_p1}"
    )

    print(
        f"P2 wins={wins_p2}"
    )

    print(
        f"draws={draws}"
    )

    print()

    print(
        f"P1 win %="
        f"{100*wins_p1/completed_games:.2f}"
    )

    print(
        f"P2 win %="
        f"{100*wins_p2/completed_games:.2f}"
    )

    print(
        f"draw %="
        f"{100*draws/completed_games:.2f}"
    )

    print()

    print(
        f"avg_moves_per_game="
        f"{sum(game_lengths)/len(game_lengths):.2f}"
    )

    print(
        f"min_moves="
        f"{min(game_lengths)}"
    )

    print(
        f"max_moves="
        f"{max(game_lengths)}"
    )

    print()
    print(
        f"total_moves={total_moves}"
    )
    print(
        f"elapsed_seconds={elapsed:.6f}"
    )

    if completed_games:
        print(
            "avg_seconds_per_game="
            f"{elapsed / completed_games:.6f}"
        )

    if total_moves:
        print(
            "avg_seconds_per_move="
            f"{elapsed / total_moves:.6f}"
        )

    print_cache_stats()


def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Profile modular_gui AI"
            " without opening Tkinter."
        )
    )

    parser.add_argument(
        "--board-size",
        type=int,
        default=9,
        choices=[4, 5, 6, 7, 9],
    )

    parser.add_argument(
        "--games",
        type=int,
        default=20,
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=30,
    )

    parser.add_argument(
        "--player-1",
        choices=list(AI_HANDLERS),
        default="minimax",
    )

    parser.add_argument(
        "--player-2",
        choices=list(AI_HANDLERS),
        default="heuristic",
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=0,
    )

    parser.add_argument(
        "--profile-top",
        type=int,
        default=25,
    )

    parser.add_argument(
        "--profile-sort",
        default="cumtime",
    )

    return parser.parse_args()


def main():

    args = parse_args()
    clear_all_caches()

    profiler = cProfile.Profile()
    profiler.enable()
    run_profile_session(args)
    profiler.disable()

    stream = io.StringIO()
    stats = pstats.Stats(
        profiler,
        stream=stream,
    )
    stats.sort_stats(
        args.profile_sort
    ).print_stats(
        args.profile_top
    )

    print()
    print(stream.getvalue())


if __name__ == "__main__":
    main()
