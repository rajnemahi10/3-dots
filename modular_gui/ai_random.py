def choose_move(board, player, legal_moves, rng, seen_states=None):
    del board
    del player
    del seen_states

    if not legal_moves:
        return None

    return rng.choice(legal_moves)
