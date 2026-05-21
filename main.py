import argparse

from main_4x4 import run_game


def main():
    parser = argparse.ArgumentParser(description="Play the default 4x4 Pattern Game.")
    parser.add_argument(
        "--layout",
        choices=[
            "corners",
            "corners_jokers",
            "corners_plus",
            "middle",
            "middle_jokers",
            "middle_plus",
        ],
        default="corners_jokers",
    )
    args = parser.parse_args()
    run_game(args.layout)


if __name__ == "__main__":
    main()
