def draw_grid(canvas, size, cell_size, origin_x=0, origin_y=0):
    width = size * cell_size
    height = size * cell_size

    for i in range(size + 1):
        offset = i * cell_size

        canvas.create_line(
            origin_x + offset,
            origin_y,
            origin_x + offset,
            origin_y + height,
            fill="black",
            width=2,
        )

        canvas.create_line(
            origin_x,
            origin_y + offset,
            origin_x + width,
            origin_y + offset,
            fill="black",
            width=2,
        )


def draw_edge_cells(canvas, board, cell_size, origin_x=0, origin_y=0):
    size = len(board)

    for row in range(size):
        for col in range(size):
            on_edge = row == 0 or col == 0 or row == size - 1 or col == size - 1

            if not on_edge or board[row][col] not in ("X", "J"):
                continue

            x = origin_x + col * cell_size
            y = origin_y + row * cell_size

            canvas.create_rectangle(
                x,
                y,
                x + cell_size,
                y + cell_size,
                fill="#d3d3d3",
                outline="",
            )


def draw_jokers(canvas, board, cell_size, origin_x=0, origin_y=0):
    radius = max(12, cell_size // 4)

    size = len(board)

    for row in range(size):
        for col in range(size):
            if board[row][col] != "J":
                continue

            x = origin_x + (col + 0.5) * cell_size
            y = origin_y + (row + 0.5) * cell_size

            canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill="royal blue",
                outline="black",
                width=2,
            )

            inner = max(5, radius // 4)

            canvas.create_oval(
                x - inner,
                y - inner,
                x + inner,
                y + inner,
                fill="white",
                outline="black",
                width=1,
            )


def draw_pieces(canvas, board, cell_size, origin_x=0, origin_y=0):
    size = len(board)
    radius = max(12, cell_size // 4)

    for row in range(size):
        for col in range(size):
            x = origin_x + col * cell_size + cell_size // 2
            y = origin_y + row * cell_size + cell_size // 2

            if board[row][col] in ("r", "R"):
                color = "red"
            elif board[row][col] in ("g", "G"):
                color = "green"
            else:
                continue

            canvas.create_oval(
                x - radius,
                y - radius,
                x + radius,
                y + radius,
                fill=color,
                outline="black",
                width=2,
            )

            if board[row][col] in ("R", "G"):
                inner = max(6, radius // 3)

                canvas.create_oval(
                    x - inner,
                    y - inner,
                    x + inner,
                    y + inner,
                    fill="gold",
                    outline="black",
                    width=1,
                )


def draw_selected(canvas, selected, cell_size, origin_x=0, origin_y=0):
    if selected is None:
        return

    row, col = selected

    x = origin_x + col * cell_size + cell_size // 2
    y = origin_y + row * cell_size + cell_size // 2

    radius = max(16, cell_size // 3)

    canvas.create_oval(
        x - radius,
        y - radius,
        x + radius,
        y + radius,
        outline="blue",
        width=3,
    )


def draw_legal_moves(canvas, legal_moves, cell_size, origin_x=0, origin_y=0):
    for row, col in legal_moves:
        x = origin_x + col * cell_size
        y = origin_y + row * cell_size

        canvas.create_rectangle(
            x,
            y,
            x + cell_size,
            y + cell_size,
            fill="#c8c8ff",
            outline="",
        )


def draw_game(canvas, board, selected, legal_moves, cell_size, origin_x=0, origin_y=0):
    canvas.delete("all")

    size = len(board)

    draw_edge_cells(canvas, board, cell_size, origin_x, origin_y)
    draw_legal_moves(canvas, legal_moves, cell_size, origin_x, origin_y)
    draw_grid(canvas, size, cell_size, origin_x, origin_y)
    draw_pieces(canvas, board, cell_size, origin_x, origin_y)
    draw_selected(canvas, selected, cell_size, origin_x, origin_y)
    draw_jokers(canvas, board, cell_size, origin_x, origin_y)
