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
    wins_including_cell,
    get_required_highlight_patterns,
)

BOARD_PIXELS = 360
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

        self.root.geometry("1500x1050")

        self.rng = random.Random()

        self.player_1_var = tk.StringVar(value="human")
        self.player_2_var = tk.StringVar(value="monte_carlo")

        self.board_size_var = tk.StringVar(value="6")

        self.board = []

        self.selected = None
        self.legal_moves = []

        self.current_player = 1

        self.game_over = False
        self.game_started = False

        self.move_history = []

        self.red_highlights = []
        self.green_highlights = []

        self.status_text = tk.StringVar(
            value="Ready"
        )

        self.pattern_controls = {}

        self.report_labels = {}

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
            padx=10,
            pady=10,
        )

        self.center_panel = ttk.Frame(
            self.main_container
        )

        self.center_panel.pack(
            side="left",
            expand=True,
            pady=10,
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
            self.center_panel,
            width=canvas_size,
            height=canvas_size,
            bg="white",
            highlightthickness=0,
        )

        self.canvas.pack(
            pady=10,
        )

        self.status_label = ttk.Label(
            self.center_panel,
            textvariable=self.status_text,
            font=("Arial", 16, "bold"),
        )

        self.status_label.pack(
            pady=5,
        )

        legend_frame = ttk.LabelFrame(
            self.center_panel,
            text="Legend",
        )

        legend_frame.pack(
            pady=8,
            fill="x",
        )

        ttk.Label(
            legend_frame,
            text="Light Red = Red winning patterns",
            font=("Arial", 11),
        ).pack(anchor="w", padx=10)

        ttk.Label(
            legend_frame,
            text="Light Green = Green winning patterns",
            font=("Arial", 11),
        ).pack(anchor="w", padx=10)

        ttk.Label(
            legend_frame,
            text="Blue = Joker",
            font=("Arial", 11),
        ).pack(anchor="w", padx=10)

        self.canvas.bind(
            "<Button-1>",
            self._handle_click,
        )

        self._build_reports()

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

        ttk.Button(
            controls,
            text="Previous Move",
            command=self.previous_move,
        ).grid(
            row=0,
            column=8,
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

            for pattern in patterns:

                row = ttk.Frame(
                    group_frame
                )

                row.pack(
                    anchor="w",
                    pady=2,
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

    def _build_reports(self):

        reports_frame = ttk.LabelFrame(
            self.center_panel,
            text="Winning Statistics",
        )

        reports_frame.pack(
            pady=10,
            fill="x",
        )

        players_container = ttk.Frame(
            reports_frame
        )

        players_container.pack(
            padx=10,
        )

        for player in (1, 2):

            outer = ttk.LabelFrame(
                players_container,
                text=f"{PLAYER_COLORS[player]}",
            )

            outer.pack(
                side="left",
                padx=8,
                pady=5,
                anchor="n",
            )
            

            left_col = ttk.Frame(outer)
            left_col.pack(
                side="left",
                padx=4,
                anchor="n",
            )

            right_col = ttk.Frame(outer)
            right_col.pack(
                side="left",
                padx=4,
                anchor="n",
            )

            # ------------------------
            # LEFT COLUMN
            # Lines + Triangles
            # ------------------------

            for section_name in (
                "lines",
                "triangles",
            ):

                title = ttk.Label(
                    left_col,
                    text=section_name.upper(),
                    font=(
                        "Arial",
                        10,
                        "bold",
                    ),
                )

                title.pack(
                    anchor="w",
                    pady=(6, 2),
                )

                for pattern in GROUPS[
                    section_name
                ]:

                    label = ttk.Label(

                        left_col,

                        text=(
                            f"{pattern:<12}"
                            f"0/0 •"
                        ),

                        font=(
                            "Consolas",
                            10,
                        ),
                    )

                    label.pack(
                        anchor="w",
                        padx=4,
                        pady=1,
                    )

                    self.report_labels[
                        (player, pattern)
                    ] = label

            # ------------------------
            # RIGHT COLUMN
            # Corners
            # ------------------------

            title = ttk.Label(
                right_col,
                text="CORNERS",
                font=(
                    "Arial",
                    10,
                    "bold",
                ),
            )

            title.pack(
                anchor="w",
                pady=(6, 2),
            )

            for pattern in GROUPS[
                "corners"
            ]:

                label = ttk.Label(

                    right_col,

                    text=(
                        f"{pattern:<15}"
                        f"0/0 •"
                    ),

                    font=(
                        "Consolas",
                        10,
                    ),
                )

                label.pack(
                    anchor="w",
                    padx=4,
                    pady=1,
                )

                self.report_labels[
                    (player, pattern)
                ] = label

    def _apply_pattern_settings(self):

        for player in (1, 2):

            for group_name, patterns in GROUPS.items():

                group = engine.config.player_pattern_groups[
                    player
                ][group_name]

                group["mode"] = "or"

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

    def _update_reports(self):

        red_counts = wins_including_cell(
            self.board,
            1,
            None,
        )

        green_counts = wins_including_cell(
            self.board,
            2,
            None,
        )

        for player, counts in (

            (1, red_counts),
            (2, green_counts),

        ):

            groups = (
                engine.config
                .player_pattern_groups[player]
            )

            for group in groups.values():

                for pattern, needed in (
                    group["patterns"].items()
                ):

                    actual = counts.get(
                        pattern,
                        0,
                    )

                    success = (
                        needed > 0
                        and actual >= needed
                    )

                    symbol = "✓" if success else "•"

                    self.report_labels[
                        (player, pattern)
                    ].config(

                        text=(
                            f"{pattern:<12}"
                            f"{actual}/{needed} "
                            f"{symbol}"
                        )
                    )

        self.red_highlights = (
            get_required_highlight_patterns(
                self.board,
                1,
            )
        )

        self.green_highlights = (
            get_required_highlight_patterns(
                self.board,
                2,
            )
        )

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

        self.move_history = []

        self.status_text.set(
            "Ready"
        )

        self._update_reports()

        self._redraw()

    def previous_move(self):

        if not self.move_history:
            return

        board, player = self.move_history.pop()

        self.board = [
            row[:]
            for row in board
        ]

        self.current_player = player

        self.selected = None
        self.legal_moves = []

        self.game_over = False

        self._update_reports()

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
            red_patterns=self.red_highlights,
            green_patterns=self.green_highlights,
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

        self._update_reports()

        outcome = resolve_move_outcome(
            self.board,
            self.current_player,
            moved_to,
        )

        if outcome["status"] == "draw":

            self.game_over = True

            self._update_reports()
            self._redraw()
            self.status_text.set(
                "Draw! Both players satisfied conditions."
            )

            return True

        if outcome["status"] == "win":

            self.game_over = True

            winner = outcome["winner"]

            self._update_reports()
            self._redraw()
            self.status_text.set(
                f"{PLAYER_COLORS[winner]} wins!"
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
            return

        self.move_history.append(

            (
                [row[:] for row in self.board],
                self.current_player,
            )
        )

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

                self.move_history.append(

                    (
                        [row[:] for row in self.board],
                        self.current_player,
                    )
                )

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