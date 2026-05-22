import random
import tkinter as tk
from tkinter import ttk, messagebox

from modular_gui import engine
from modular_gui.visuals import draw_game

from modular_gui import (
    ai_random,
    ai_heuristic,
    ai_minimax,
    ai_monte_carlo,
)

from modular_gui.board import (
    apply_move,
    create_board,
    generate_moves,
    get_all_moves,
    resolve_move_outcome,
)

BOARD_PIXELS = 420
MARGIN = 10
BOARD_EDGE_PADDING = 10

BOARD_SIZES = [4, 5, 6, 7]

CONTROLLERS = [
    "human",
    "random",
    "heuristic",
    "minimax",
    "monte_carlo",
]

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

GROUPS = {

    "lines": [
        "horizontal",
        "vertical",
        "diag_left",
        "diag_right",
    ],

    "triangles": [
        "triangle_up",
        "triangle_down",
        "triangle_left",
        "triangle_right",
    ],

    "corners": [
        "corner_ul",
        "corner_ur",
        "corner_dl",
        "corner_dr",
    ],
}


class PatternGameApp:

    def __init__(self, root):

        self.root = root

        self.root.title("Pattern Game")

        self.root.geometry("1450x900")

        self.root.resizable(True, True)

        self.rng = random.Random()

        self.player_1_var = tk.StringVar(value="human")
        self.player_2_var = tk.StringVar(value="monte_carlo")

        self.board_size_var = tk.StringVar(value="5")

        self.board = []

        self.selected = None
        self.legal_moves = []

        self.current_player = 1

        self.game_over = False
        self.game_started = False

        self.pattern_controls = {}

        self.group_modes = {}

        self.main_container = ttk.Frame(
            self.root
        )

        self.main_container.pack(
            fill="both",
            expand=True,
        )

        self.left_panel = ttk.Frame(
            self.main_container
        )

        self.left_panel.pack(
            side="left",
            fill="y",
            padx=8,
            pady=8,
        )

        self.right_panel = ttk.Frame(
            self.main_container
        )

        self.right_panel.pack(
            side="right",
            fill="both",
            expand=True,
            padx=8,
            pady=8,
        )

        self._build_controls()

        canvas_size = (
            BOARD_PIXELS
            + 2 * (
                MARGIN
                + BOARD_EDGE_PADDING
            )
        )

        self.canvas = tk.Canvas(
            self.right_panel,
            width=canvas_size,
            height=canvas_size,
            bg="white",
            highlightthickness=0,
        )

        self.canvas.pack(
            expand=True,
        )

        self.canvas.bind(
            "<Button-1>",
            self._handle_click,
        )

        self.new_game()

    def _build_controls(self):

        controls = ttk.Frame(
            self.left_panel
        )

        controls.pack(
            fill="x",
            pady=5,
        )

        ttk.Label(
            controls,
            text="P1",
        ).grid(
            row=0,
            column=0,
            padx=5,
            pady=5,
        )

        ttk.Combobox(
            controls,
            textvariable=self.player_1_var,
            values=CONTROLLERS,
            width=15,
            state="readonly",
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=5,
        )

        ttk.Label(
            controls,
            text="P2",
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=5,
        )

        ttk.Combobox(
            controls,
            textvariable=self.player_2_var,
            values=CONTROLLERS,
            width=15,
            state="readonly",
        ).grid(
            row=0,
            column=3,
            padx=5,
            pady=5,
        )

        ttk.Label(
            controls,
            text="Board",
        ).grid(
            row=0,
            column=4,
            padx=5,
            pady=5,
        )

        ttk.Combobox(
            controls,
            textvariable=self.board_size_var,
            values=[
                str(size)
                for size in BOARD_SIZES
            ],
            width=8,
            state="readonly",
        ).grid(
            row=0,
            column=5,
            padx=5,
            pady=5,
        )

        ttk.Button(
            controls,
            text="Start Game",
            command=self.start_game,
        ).grid(
            row=0,
            column=6,
            padx=5,
            pady=5,
        )

        ttk.Button(
            controls,
            text="New Game",
            command=self.new_game,
        ).grid(
            row=0,
            column=7,
            padx=5,
            pady=5,
        )

        self._build_pattern_controls()

    def _build_pattern_controls(self):

        container = ttk.Frame(
            self.left_panel
        )

        container.pack(
            fill="x",
            pady=10,
        )

        player_1_frame = ttk.LabelFrame(
            container,
            text="Player 1",
        )

        player_1_frame.pack(
            side="left",
            fill="y",
            padx=5,
        )

        player_2_frame = ttk.LabelFrame(
            container,
            text="Player 2",
        )

        player_2_frame.pack(
            side="left",
            fill="y",
            padx=5,
        )

        self._build_player_groups(
            player_1_frame,
            1,
        )

        self._build_player_groups(
            player_2_frame,
            2,
        )

    def _build_player_groups(
        self,
        parent,
        player,
    ):

        for group_name, patterns in GROUPS.items():

            group_frame = ttk.LabelFrame(
                parent,
                text=group_name.capitalize(),
            )

            group_frame.pack(
                fill="x",
                pady=5,
                padx=5,
            )

            mode_var = tk.StringVar(
                value="or"
            )

            self.group_modes[
                (player, group_name)
            ] = mode_var

            mode_row = ttk.Frame(
                group_frame
            )

            mode_row.pack(
                anchor="w",
                pady=2,
            )

            ttk.Label(
                mode_row,
                text="Mode",
                width=10,
            ).pack(side="left")

            ttk.Combobox(
                mode_row,
                textvariable=mode_var,
                values=["and", "or"],
                width=6,
                state="readonly",
            ).pack(side="left")

            for pattern in patterns:

                row = ttk.Frame(
                    group_frame
                )

                row.pack(
                    anchor="w",
                    pady=1,
                )

                ttk.Label(
                    row,
                    text=pattern,
                    width=16,
                    anchor="w",
                ).pack(side="left")

                default = 0

                if group_name == "lines":
                    default = 1

                var = tk.IntVar(
                    value=default
                )

                spin = tk.Spinbox(
                    row,
                    from_=0,
                    to=10,
                    width=5,
                    textvariable=var,
                )

                spin.pack(
                    side="left",
                    padx=3,
                )

                self.pattern_controls[
                    (
                        player,
                        group_name,
                        pattern,
                    )
                ] = var

    def _apply_pattern_settings(self):

        for player in (1, 2):

            for group_name, patterns in GROUPS.items():

                group = engine.config.player_pattern_groups[
                    player
                ][group_name]

                group["mode"] = self.group_modes[
                    (player, group_name)
                ].get()

                for pattern in patterns:

                    count = self.pattern_controls[
                        (
                            player,
                            group_name,
                            pattern,
                        )
                    ].get()

                    group["patterns"][
                        pattern
                    ] = count

    def start_game(self):

        self.game_started = True

        self._schedule_ai_turn()

    def new_game(self):

        self._apply_pattern_settings()

        board_size = int(
            self.board_size_var.get()
        )

        self.board = create_board(
            board_size
        )

        self.cell_size = (
            BOARD_PIXELS
            // len(self.board)
        )

        self.board_origin = (
            MARGIN
            + BOARD_EDGE_PADDING
        )

        self.selected = None
        self.legal_moves = []

        self.current_player = 1

        self.game_over = False
        self.game_started = False

        self._redraw()

    def _redraw(self):

        draw_game(
            self.canvas,
            self.board,
            self.selected,
            self.legal_moves,
            self.cell_size,
            origin_x=self.board_origin,
            origin_y=self.board_origin,
        )

    def _advance_turn(self):

        self.current_player = (
            2
            if self.current_player == 1
            else 1
        )

    def _controller_for_current_player(
        self
    ):

        if self.current_player == 1:
            return self.player_1_var.get()

        return self.player_2_var.get()

    def _apply_move_outcome(
        self,
        moved_to,
    ):

        outcome = resolve_move_outcome(
            self.board,
            self.current_player,
            moved_to,
        )

        if outcome["status"] == "draw":

            self.game_over = True

            messagebox.showinfo(
                "Pattern Game",
                "Draw!",
            )

            return True

        if outcome["status"] == "win":

            self.game_over = True

            winner = outcome["winner"]

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

        strategy = (
            self._controller_for_current_player()
        )

        if strategy == "human":
            return

        self.root.after(
            250,
            self._ai_step,
        )

    def _ai_step(self):

        if self.game_over:
            return

        strategy = (
            self._controller_for_current_player()
        )

        legal_moves = get_all_moves(
            self.board,
            self.current_player,
        )

        if not legal_moves:

            self.game_over = True

            messagebox.showinfo(
                "Pattern Game",
                "Draw: no legal moves.",
            )

            return

        chooser = AI_HANDLERS.get(
            strategy,
            ai_random.choose_move,
        )

        move = chooser(
            self.board,
            self.current_player,
            legal_moves,
            self.rng,
            set(),
        )

        if move is None:

            self.game_over = True

            messagebox.showinfo(
                "Pattern Game",
                "Draw: no legal moves.",
            )

            return

        apply_move(
            self.board,
            move,
        )

        self.selected = None
        self.legal_moves = []

        self._redraw()

        if self._apply_move_outcome(
            move[1]
        ):
            return

        self._advance_turn()

        self._schedule_ai_turn()

    def _handle_click(self, event):

        if self.game_over:
            return

        if not self.game_started:
            return

        if (
            self._controller_for_current_player()
            != "human"
        ):
            return

        row = (
            event.y
            - self.board_origin
        ) // self.cell_size

        col = (
            event.x
            - self.board_origin
        ) // self.cell_size

        size = len(self.board)

        if not (
            0 <= row < size
            and 0 <= col < size
        ):
            return

        if self.selected is None:

            if engine.is_player_piece(
                self.board[row][col],
                self.current_player,
            ):

                if not engine.is_joker(
                    self.board[row][col]
                ):

                    self.selected = (
                        row,
                        col,
                    )

                    self.legal_moves = (
                        generate_moves(
                            self.board,
                            row,
                            col,
                        )
                    )

        else:

            if (
                row,
                col,
            ) in self.legal_moves:

                apply_move(
                    self.board,
                    (
                        self.selected,
                        (
                            row,
                            col,
                        ),
                    ),
                )

                self.selected = None
                self.legal_moves = []

                self._redraw()

                if self._apply_move_outcome(
                    (
                        row,
                        col,
                    )
                ):
                    return

                self._advance_turn()

            else:

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