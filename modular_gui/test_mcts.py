move = ai_mcts.choose_move(
    board,
    1,
    get_all_moves(board,1),
    random.Random(0),
)