import tkinter as tk

from modular_gui import engine


CELL_COLORS = {

    engine.EMPTY: "#f2f2f2",

    engine.RED_SINGLE: "#d84c4c",
    engine.RED_LONG: "#8b0000",

    engine.GREEN_SINGLE: "#49b649",
    engine.GREEN_LONG: "#006400",

    engine.JOKER: "#3b82f6",

    engine.BLOCKED: "#222222",
}


TEXT_COLORS = {

    engine.EMPTY: "#666666",

    engine.RED_SINGLE: "white",
    engine.RED_LONG: "white",

    engine.GREEN_SINGLE: "white",
    engine.GREEN_LONG: "white",

    engine.JOKER: "white",

    engine.BLOCKED: "white",
}


CELL_LABELS = {

    engine.EMPTY: "",

    engine.RED_SINGLE: "r",
    engine.RED_LONG: "R",

    engine.GREEN_SINGLE: "g",
    engine.GREEN_LONG: "G",

    engine.JOKER: "J",

    engine.BLOCKED: "X",
}


def draw_game(
    canvas,
    board,
    selected,
    legal_moves,
    cell_size,
    origin_x=0,
    origin_y=0,
    red_patterns=None,
    green_patterns=None,
):

    if red_patterns is None:
        red_patterns = []

    if green_patterns is None:
        green_patterns = []

    canvas.delete("all")

    size = len(board)

    # -----------------------------
    # DRAW BOARD
    # -----------------------------

    for row in range(size):

        for col in range(size):

            x1 = (
                origin_x
                + col * cell_size
            )

            y1 = (
                origin_y
                + row * cell_size
            )

            x2 = x1 + cell_size
            y2 = y1 + cell_size

            cell = board[row][col]

            fill = CELL_COLORS.get(
                cell,
                "#cccccc",
            )

            outline = "#555555"
            width = 2

            if (
                selected
                and selected == (row, col)
            ):

                outline = "#ffcc00"
                width = 5

            elif (
                row,
                col,
            ) in legal_moves:

                outline = "#00aaff"
                width = 4

            canvas.create_rectangle(

                x1,
                y1,
                x2,
                y2,

                fill=fill,

                outline=outline,

                width=width,
            )

            label = CELL_LABELS.get(
                cell,
                "?",
            )

            canvas.create_text(

                (x1 + x2) / 2,
                (y1 + y2) / 2,

                text=label,

                fill=TEXT_COLORS.get(
                    cell,
                    "black",
                ),

                font=(
                    "Arial",
                    int(cell_size * 0.25),
                    "bold",
                ),
            )

    # -----------------------------
    # DRAW GRID
    # -----------------------------

    draw_grid_lines(
        canvas,
        size,
        cell_size,
        origin_x,
        origin_y,
    )

    # -----------------------------
    # DRAW HIGHLIGHTS ON TOP
    # -----------------------------

    draw_pattern_overlays(
        canvas,
        red_patterns,
        green_patterns,
        cell_size,
        origin_x,
        origin_y,
    )


def draw_grid_lines(
    canvas,
    size,
    cell_size,
    origin_x,
    origin_y,
):

    total = size * cell_size

    for i in range(size + 1):

        x = origin_x + i * cell_size

        canvas.create_line(

            x,
            origin_y,

            x,
            origin_y + total,

            fill="#444444",
            width=2,
        )

    for i in range(size + 1):

        y = origin_y + i * cell_size

        canvas.create_line(

            origin_x,
            y,

            origin_x + total,
            y,

            fill="#444444",
            width=2,
        )


def draw_pattern_overlays(
    canvas,
    red_patterns,
    green_patterns,
    cell_size,
    origin_x,
    origin_y,
):

    for pattern in red_patterns:

        draw_single_pattern(

            canvas,
            pattern,

            "#ff6666",

            cell_size,
            origin_x,
            origin_y,
        )

    for pattern in green_patterns:

        draw_single_pattern(

            canvas,
            pattern,

            "#66ff66",

            cell_size,
            origin_x,
            origin_y,
        )


def draw_single_pattern(
    canvas,
    pattern,
    color,
    cell_size,
    origin_x,
    origin_y,
):

    if len(pattern) != 3:
        return

    centers = []

    for row, col in pattern:

        x = (
            origin_x
            + col * cell_size
            + cell_size / 2
        )

        y = (
            origin_y
            + row * cell_size
            + cell_size / 2
        )

        centers.append((x, y))

    x1, y1 = centers[0]
    x2, y2 = centers[1]
    x3, y3 = centers[2]

    # glow cells

    for row, col in pattern:

        gx1 = (
            origin_x
            + col * cell_size
            + 6
        )

        gy1 = (
            origin_y
            + row * cell_size
            + 6
        )

        gx2 = gx1 + cell_size - 12
        gy2 = gy1 + cell_size - 12

        canvas.create_rectangle(

            gx1,
            gy1,
            gx2,
            gy2,

            outline=color,
            width=5,
        )

    # connect pattern

    canvas.create_line(

        x1,
        y1,

        x2,
        y2,

        fill=color,
        width=7,
        smooth=True,
    )

    canvas.create_line(

        x2,
        y2,

        x3,
        y3,

        fill=color,
        width=7,
        smooth=True,
    )

    # dots

    radius = 8

    for x, y in centers:

        canvas.create_oval(

            x - radius,
            y - radius,

            x + radius,
            y + radius,

            fill=color,
            outline="",
        )