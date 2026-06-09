from math import sqrt, log

import modular_gui.engine as engine

from modular_gui.board import (
    apply_move,
    get_all_moves,
    resolve_move_outcome,
)

# ----------------------------------------
# TUNING
# ----------------------------------------

SIMULATIONS = 100
ROLLOUT_DEPTH = 15
UCT_C = 1.414

# ----------------------------------------
# NODE CACHE
# ----------------------------------------

NODE_CACHE = {}

# ----------------------------------------
# FAST LOCAL WIN CHECK (O(1), no board copy)
# ----------------------------------------

_LINE_DIRS = ((0,1),(1,0),(1,1),(1,-1))

def _build_triples():
    t = []
    for dr, dc in _LINE_DIRS:
        t.append((0,0, dr,dc, 2*dr,2*dc))
        t.append((-dr,-dc, 0,0, dr,dc))
        t.append((-2*dr,-2*dc, -dr,-dc, 0,0))
    return tuple(t)

_TRIPLES = _build_triples()


def _check_win_at(board, row, col, player):
    size = len(board)
    opponent = 2 if player == 1 else 1
    is_joker = engine.is_joker
    owner    = engine.owner_of

    for dr1,dc1, drm,dcm, dr2,dc2 in _TRIPLES:
        r1,c1 = row+dr1, col+dc1
        rm,cm = row+drm, col+dcm
        r2,c2 = row+dr2, col+dc2
        if not (0<=r1<size and 0<=c1<size
                and 0<=rm<size and 0<=cm<size
                and 0<=r2<size and 0<=c2<size):
            continue
        mid = board[rm][cm]
        if owner(mid) != opponent:
            continue
        ep1 = board[r1][c1]
        ep2 = board[r2][c2]
        o1 = owner(ep1); j1 = is_joker(ep1)
        o2 = owner(ep2); j2 = is_joker(ep2)
        if (o1==player or j1) and (o2==player or j2) and not (j1 and j2):
            return True
    return False


# ----------------------------------------
# HELPERS
# ----------------------------------------

def copy_board(board):
    return [row[:] for row in board]

def fast_board_key(board, player):
    return (player, tuple(tuple(r) for r in board))


# ----------------------------------------
# NODE
# ----------------------------------------

class Node:
    __slots__ = ("board","player","parent","move",
                 "children","visits","value","untried_moves")

    def __init__(self, board, player, parent=None, move=None):
        self.board = board
        self.player = player
        self.parent = parent
        self.move = move
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_moves = get_all_moves(board, player)


# ----------------------------------------
# UCT / SELECT / EXPAND
# ----------------------------------------

def uct_score(pv, child):
    if child.visits == 0:
        return float("inf")
    return child.value/child.visits + UCT_C*sqrt(log(pv)/child.visits)

def select(node):
    while not node.untried_moves and node.children:
        pv = node.visits
        node = max(node.children, key=lambda c: uct_score(pv, c))
    return node

def expand(node):
    if not node.untried_moves:
        return node
    move = node.untried_moves.pop()
    nb = copy_board(node.board)
    apply_move(nb, move)
    np_ = 2 if node.player == 1 else 1
    key = fast_board_key(nb, np_)
    if key in NODE_CACHE:
        child = NODE_CACHE[key]
    else:
        child = Node(nb, np_, parent=node, move=move)
        NODE_CACHE[key] = child
    child.parent = node
    child.move = move
    node.children.append(child)
    return child


# ----------------------------------------
# ROLLOUT — pure random, single post-move terminal check
# ----------------------------------------

def rollout(node, root_player, rng):
    board = copy_board(node.board)
    cp = node.player

    for _ in range(ROLLOUT_DEPTH):
        moves = get_all_moves(board, cp)
        if not moves:
            return 0.0

        move = rng.choice(moves)
        (sr,sc),(dr,dc) = move
        piece = board[sr][sc]
        board[dr][dc] = piece
        board[sr][sc] = engine.EMPTY

        # O(1) terminal check — no function call overhead
        opponent = 2 if cp == 1 else 1
        mw = _check_win_at(board, dr, dc, cp)
        ow = _check_win_at(board, dr, dc, opponent)

        if mw or ow:
            if mw and ow:   return 0.0
            if mw:          return 1.0 if cp == root_player else -1.0
            return          -1.0 if cp == root_player else 1.0

        cp = opponent

    return 0.0


# ----------------------------------------
# BACKPROP / SIMULATE
# ----------------------------------------

def backpropagate(node, result):
    while node:
        node.visits += 1
        node.value  += result
        result = -result
        node = node.parent

def simulate(root, root_player, rng):
    node = select(root)
    node = expand(node)
    backpropagate(node, rollout(node, root_player, rng))


# ----------------------------------------
# PUBLIC INTERFACE
# ----------------------------------------

def choose_move(board, player, legal_moves, rng, seen_states=None):
    if not legal_moves:
        return None

    # Grab free win with in-place check (no copy)
    for move in legal_moves:
        (sr,sc),(dr,dc) = move
        piece = board[sr][sc]
        board[dr][dc] = piece
        board[sr][sc] = engine.EMPTY
        won = _check_win_at(board, dr, dc, player)
        board[sr][sc] = piece
        board[dr][dc] = engine.EMPTY
        if won:
            return move

    NODE_CACHE.clear()
    root = Node(board, player)

    for _ in range(SIMULATIONS):
        simulate(root, player, rng)

    if not root.children:
        return rng.choice(legal_moves)

    return max(root.children, key=lambda c: c.visits).move


def clear_cache():
    NODE_CACHE.clear()

def cache_report():
    return {"nodes": len(NODE_CACHE)}