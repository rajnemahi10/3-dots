import unittest

from modular_gui.engine import parse_compact_notation_rows
from modular_gui.board import (
    apply_move,
    create_board,
    generate_moves,
    resolve_move_outcome,
    wins_including_cell,
)


class TestRulesAndNotation(unittest.TestCase):
    def setUp(self):
        # Ensure engine patterns and active joker positions are initialized.
        create_board(4)

    def test_parse_compact_requires_edge_tokens(self):
        with self.assertRaises(ValueError):
            parse_compact_notation_rows(
                [
                    ". . .",
                    ". r .",
                    ". . .",
                ]
            )

    def test_generate_moves_single_vs_long_range(self):
        board = parse_compact_notation_rows(
            [
                "X J X J X X X",
                "X . . . . . J",
                "J . . . . . X",
                "X . . r . . J",
                "J . . . . . X",
                "X . . . . . J",
                "X X X J X J X",
            ]
        )

        single_moves = set(generate_moves(board, 3, 3))
        self.assertEqual(len(single_moves), 8)
        self.assertNotIn((1, 3), single_moves)

        board[3][3] = "R"
        long_moves = set(generate_moves(board, 3, 3))
        self.assertEqual(len(long_moves), 16)
        self.assertIn((1, 3), long_moves)
        self.assertIn((3, 1), long_moves)
        self.assertIn((5, 5), long_moves)

    def test_outcome_only_counts_patterns_through_moved_cell(self):
        board = parse_compact_notation_rows(
            [
                "X J X J X X",
                "X r g r . J",
                "J . . . . X",
                "X . . . . J",
                "J . . . . X",
                "X X J X J X",
            ]
        )

        outcome = resolve_move_outcome(board, 1, (4, 4))

        self.assertEqual(
            outcome,
            {
                "status": "none",
                "winner": None,
                "reason": None,
            },
        )

    def test_red_wins_with_joker_after_given_move(self):
        board = parse_compact_notation_rows(
            [
                "X J X J X X",
                "X . R . . J",
                "J r . g . X",
                "X . r . g J",
                "J . . G . X",
                "X X J X J X",
            ]
        )

        move = ((1, 2), (1, 4))
        apply_move(board, move)

        red_wins = wins_including_cell(board, 1, (1, 4))
        green_wins = wins_including_cell(board, 2, (1, 4))

        self.assertTrue(red_wins)
        self.assertFalse(green_wins)

        outcome = resolve_move_outcome(board, 1, (1, 4))

        self.assertEqual(
            outcome,
            {
                "status": "win",
                "winner": 1,
                "reason": "pattern",
            },
        )

    def test_green_wins_with_joker_symmetry(self):
        board = parse_compact_notation_rows(
            [
                "X J X J X X",
                "X . G . . J",
                "J g . r . X",
                "X . g . r J",
                "J . . R . X",
                "X X J X J X",
            ]
        )

        move = ((1, 2), (1, 4))
        apply_move(board, move)

        outcome = resolve_move_outcome(board, 2, (1, 4))

        self.assertEqual(
            outcome,
            {
                "status": "win",
                "winner": 2,
                "reason": "pattern",
            },
        )

    def test_self_sabotage_is_opponent_win(self):
        board = parse_compact_notation_rows(
            [
                "X J X J X X X",
                "X . . . . . J",
                "J . . . . . X",
                "X . g r g . J",
                "J . . . . . X",
                "X . . . . . J",
                "X X X J X J X",
            ]
        )

        outcome = resolve_move_outcome(board, 1, (3, 3))

        self.assertEqual(
            outcome,
            {
                "status": "win",
                "winner": 2,
                "reason": "self_sabotage",
            },
        )

    def test_dual_pattern_through_moved_piece_is_draw(self):
        board = parse_compact_notation_rows(
            [
                "X J X J X X",
                "X . g . . J",
                "J . r g r X",
                "X . g . . J",
                "J . . . . X",
                "X X J X J X",
            ]
        )

        outcome = resolve_move_outcome(board, 1, (2, 2))

        self.assertEqual(
            outcome,
            {
                "status": "draw",
                "winner": 0,
                "reason": "dual_pattern",
            },
        )

    def test_wins_including_cell_matches_outcome_reasoning(self):
        board = parse_compact_notation_rows(
            [
                "X J X J X X",
                "X . R . . J",
                "J r . g . X",
                "X . r . g J",
                "J . . G . X",
                "X X J X J X",
            ]
        )

        move = ((1, 2), (1, 4))
        apply_move(board, move)

        self.assertTrue(wins_including_cell(board, 1, (1, 4)))
        self.assertFalse(wins_including_cell(board, 2, (1, 4)))


if __name__ == "__main__":
    unittest.main()
