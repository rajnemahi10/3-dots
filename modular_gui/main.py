import random
import tkinter as tk
from tkinter import messagebox, ttk

from modular_gui.engine import is_joker, is_player_piece
from modular_gui.visuals import draw_game

from modular_gui import ai_heuristic, ai_minimax, ai_monte_carlo, ai_random
from modular_gui.board import (
    apply_move,
    create_board,
    generate_moves,
    get_all_moves,
    resolve_move_outcome,
)


BOARD_PIXELS = 600
MARGIN = 80
BOARD_EDGE_PADDING = 50

CONTROLLERS = ["human", "random", "heuristic", "minimax", "monte_carlo"]
BOARD_SIZES = [4, 5, 6]

PLAYER_COLORS = {
    1: "Red",
    2: "Green",
}

AI_HANDLERS = {
    "random": ai_random.choose_move,
    "heuristic": ai_heuristic.choose_move,
    "minimax": ai_minimax.choose_move,
    "monte_carlo": ai_monte_carlo.choose_move,
}


class PatternGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pattern Game Modular GUI")
        self.root.resizable(False, False)

        self.rng = random.Random()

        self.player_1_var = tk.StringVar(value="human")
        self.player_2_var = tk.StringVar(value="monte_carlo")
        self.board_size_var = tk.StringVar(value="4")

        self.board = []
        self.cell_size = 0
        self.board_origin = MARGIN + BOARD_EDGE_PADDING
        self.selected = None
        self.legal_moves = []
        self.current_player = 1
        self.game_over = False
        self.game_started = False
        self.move_history = []
        self.history_index = 0

        self._build_controls()

        canvas_size = BOARD_PIXELS + 2 * self.board_origin
        self.canvas = tk.Canvas(
            self.root,
            width=canvas_size,
            height=canvas_size,
            bg="white",
            highlightthickness=0,
        )
        self.canvas.pack(padx=8, pady=8)
        self.canvas.bind("<Button-1>", self._handle_click)

        self.new_game()

    def _build_controls(self):
        controls = ttk.Frame(self.root)
        controls.pack(fill="x", padx=8, pady=(8, 4))

        ttk.Label(controls, text="P1").pack(side="left")
        ttk.Combobox(
            controls,
            textvariable=self.player_1_var,
            values=CONTROLLERS,
            state="readonly",
            width=12,
        ).pack(side="left", padx=(6, 12))

        ttk.Label(controls, text="P2").pack(side="left")
        ttk.Combobox(
            controls,
            textvariable=self.player_2_var,
            values=CONTROLLERS,
            state="readonly",
            width=12,
        ).pack(side="left", padx=(6, 12))

        ttk.Label(controls, text="Board").pack(side="left")
        ttk.Combobox(
            controls,
            textvariable=self.board_size_var,
            values=[str(size) for size in BOARD_SIZES],
            state="readonly",
            width=6,
        ).pack(side="left", padx=(6, 12))

        ttk.Button(controls, text="Start Game", command=self.start_game).pack(side="left")
        ttk.Button(controls, text="New Game", command=self.new_game).pack(side="left", padx=(8, 0))
        ttk.Button(controls, text="Previous Move", command=self._show_previous_move).pack(side="left", padx=(8, 4))
        ttk.Button(controls, text="Next Move", command=self._show_next_move).pack(side="left")

        self.history_label = ttk.Label(controls, text="Move 0/0")
        self.history_label.pack(side="left", padx=(12, 0))

    def start_game(self):
        if not self.board:
            self.new_game()

        self.game_started = True

        if self.move_history:
            self.history_index = len(self.move_history) - 1
            self.selected = None
            self.legal_moves = []
            self._update_history_label()
            self._redraw()

        self._schedule_ai_turn()

    def new_game(self):
        board_size = int(self.board_size_var.get())

        self.board = create_board(board_size)
        self.cell_size = BOARD_PIXELS // len(self.board)
        self.selected = None
        self.legal_moves = []
        self.current_player = 1
        self.game_over = False
        self.game_started = False

        self.move_history = [self._copy_board(self.board)]
        self.history_index = 0
        self._update_history_label()

        self._redraw()

    def _copy_board(self, board):
        return [row[:] for row in board]

    def _is_viewing_latest_move(self):
        return self.history_index == len(self.move_history) - 1

    def _record_current_position(self):
        self.move_history = self.move_history[: self.history_index + 1]
        self.move_history.append(self._copy_board(self.board))
        self.history_index = len(self.move_history) - 1
        self._update_history_label()

    def _update_history_label(self):
        if not self.move_history:
            self.history_label.config(text="Move 0/0")
            return

        self.history_label.config(
            text=f"Move {self.history_index}/{len(self.move_history) - 1}"
        )

    def _show_previous_move(self):
        if not self.move_history:
            return

        if self.history_index == 0:
            return

        self.history_index -= 1
        self.selected = None
        self.legal_moves = []
        self._update_history_label()
        self._redraw()

    def _show_next_move(self):
        if not self.move_history:
            return

        if self.history_index >= len(self.move_history) - 1:
            return

        self.history_index += 1
        self.selected = None
        self.legal_moves = []
        self._update_history_label()
        self._redraw()

        if self._is_viewing_latest_move():
            self._schedule_ai_turn()

    def _redraw(self):
        if self.move_history:
            board_to_draw = self.move_history[self.history_index]
        else:
            board_to_draw = self.board

        draw_game(
            self.canvas,
            board_to_draw,
            self.selected,
            self.legal_moves,
            self.cell_size,
            origin_x=self.board_origin,
            origin_y=self.board_origin,
        )

    def _advance_turn(self):
        self.current_player = 2 if self.current_player == 1 else 1

    def _controller_for_current_player(self):
        if self.current_player == 1:
            return self.player_1_var.get()

        return self.player_2_var.get()

    def _apply_move_outcome(self, moved_to):
        outcome = resolve_move_outcome(
            self.board,
            self.current_player,
            moved_to,
        )

        if outcome["status"] == "draw":
            self.game_over = True
            messagebox.showinfo(
                "Pattern Game",
                "Draw: both players formed a pattern through the moved piece.",
            )
            return True

        if outcome["status"] == "win":
            self.game_over = True
            winner = outcome["winner"]

            if winner != self.current_player and outcome["reason"] == "self_sabotage":
                messagebox.showinfo(
                    "Pattern Game",
                    f"{PLAYER_COLORS[self.current_player]} self-sabotaged. "
                    f"{PLAYER_COLORS[winner]} wins!",
                )
            else:
                messagebox.showinfo(
                    "Pattern Game",
                    f"{PLAYER_COLORS[winner]} wins!",
                )

            return True

        return False

    def _schedule_ai_turn(self):
        if self.game_over:
            return

        if not self.game_started:
            return

        if not self._is_viewing_latest_move():
            return

        if self._controller_for_current_player() == "human":
            return

        self.root.after(250, self._ai_step)

    def _ai_step(self):
        if self.game_over:
            return

        if not self.game_started:
            return

        if not self._is_viewing_latest_move():
            return

        strategy = self._controller_for_current_player()

        if strategy == "human":
            return

        legal_moves = get_all_moves(self.board, self.current_player)

        if not legal_moves:
            self.game_over = True
            messagebox.showinfo("Pattern Game", "Draw: no legal moves.")
            return

        chooser = AI_HANDLERS.get(strategy, ai_random.choose_move)
        move = chooser(
            self.board,
            self.current_player,
            legal_moves,
            self.rng,
            set(),
        )

        if move is None:
            self.game_over = True
            messagebox.showinfo("Pattern Game", "Draw: no legal moves.")
            return

        apply_move(self.board, move)
        self._record_current_position()
        self.selected = None
        self.legal_moves = []
        self._redraw()

        if self._apply_move_outcome(move[1]):
            return

        self._advance_turn()
        self._schedule_ai_turn()

    def _handle_click(self, event):
        if self.game_over:
            return

        if not self.game_started:
            return

        if not self._is_viewing_latest_move():
            return

        if self._controller_for_current_player() != "human":
            return

        row = (event.y - self.board_origin) // self.cell_size
        col = (event.x - self.board_origin) // self.cell_size

        size = len(self.board)

        if not (0 <= row < size and 0 <= col < size):
            return

        if self.selected is None:
            if is_player_piece(self.board[row][col], self.current_player):
                if not is_joker(self.board[row][col]):
                    self.selected = (row, col)
                    self.legal_moves = generate_moves(self.board, row, col)
        else:
            if (row, col) in self.legal_moves:
                apply_move(self.board, (self.selected, (row, col)))
                self._record_current_position()
                self.selected = None
                self.legal_moves = []
                self._redraw()

                if self._apply_move_outcome((row, col)):
                    return

                self._advance_turn()

            if self.selected is not None:
                self.selected = None
                self.legal_moves = []

        self._redraw()
        self._schedule_ai_turn()


def main():
    root = tk.Tk()
    PatternGameApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
