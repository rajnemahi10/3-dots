import random


from modular_gui.board import (
   get_all_moves,
   resolve_move_outcome,
)




# -------------------------------------------------
# Helpers
# -------------------------------------------------




def clone_board(board):


   return [
       row[:]
       for row in board
   ]




def board_signature(board):


   return tuple(


       tuple(row)


       for row in board
   )




def print_board(board):


   print()


   for row in board:


       print(
           " ".join(row)
       )


   print()




# -------------------------------------------------
# Edge rules
# -------------------------------------------------










# -------------------------------------------------
# Safety check
# -------------------------------------------------




def is_safe_position(board):


   red = resolve_move_outcome(
       board,
       1,
       None,
   )


   green = resolve_move_outcome(
       board,
       2,
       None,
   )


   return (


       red["status"] == "none"
       and green["status"] == "none"
   )




# -------------------------------------------------
# Board quality rules
# -------------------------------------------------










# -------------------------------------------------
# Reverse move generation
# -------------------------------------------------




def generate_reverse_moves(
   board,
   player,
):


   size = len(board)


   reverse_moves = []


   directions = [


       (-1, 0),
       (1, 0),
       (0, -1),
       (0, 1),


       (-1, -1),
       (-1, 1),
       (1, -1),
       (1, 1),
   ]


   for row in range(size):


       for col in range(size):


           piece = board[row][col]


           if piece == ".":
               continue


           # player ownership


           if player == 1:


               if not (
                   piece.startswith("r")
                   or piece == "J"
               ):
                   continue


           else:


               if not (
                   piece.startswith("g")
                   or piece == "J"
               ):
                   continue


           # jokers immovable


           if piece == "J":
               continue


           # long pieces


           long_piece = piece.isupper()


           steps = [2] if long_piece else [1]


           for dr, dc in directions:


               for step in steps:


                   prev_r = row - dr * step
                   prev_c = col - dc * step


                   if not (
                       0 <= prev_r < size
                       and 0 <= prev_c < size
                   ):
                       continue


                   # cannot move into edge


                   if (
                       prev_r == 0
                       or prev_c == 0
                       or prev_r == size - 1
                       or prev_c == size - 1
                   ):


                       continue


                   if (
                       board[prev_r][prev_c]
                       != "."
                   ):
                       continue


                   if step == 2:


                       middle_r = row - dr
                       middle_c = col - dc


                       if (
                           board[middle_r][middle_c]
                           != "."
                       ):
                           continue


                   reverse_moves.append(


                       (
                           (row, col),
                           (prev_r, prev_c),
                       )
                   )


   return reverse_moves




# -------------------------------------------------
# Apply reverse move
# -------------------------------------------------




def apply_reverse_move(
   board,
   move,
):


   (src_r, src_c), (
       dst_r,
       dst_c,
   ) = move


   board[dst_r][dst_c] = (
       board[src_r][src_c]
   )


   board[src_r][src_c] = "."




# -------------------------------------------------
# Main reverse engineering
# -------------------------------------------------




def reverse_engineer_board(
   winning_board,
   winner,
   max_depth=100,
   seed=0,
):


   rng = random.Random(seed)


   current = clone_board(
       winning_board
   )


   history = []


   seen = {}


   repeated_board = None


   repeated_depth = None


   for depth in range(max_depth):


       signature = board_signature(
           current
       )


       # ---------------------------------
       # repeated state found
       # ---------------------------------


       if signature in seen:


           repeated_board = clone_board(
               current
           )


           repeated_depth = depth


           print(
               "\\nRepeated configuration found."
           )


           print(
               "First seen at depth:",
               seen[signature]
           )


           print(
               "Repeated at depth:",
               depth
           )


           break


       seen[signature] = depth


       reverse_player = (


           winner


           if depth % 2 == 0


           else (
               2 if winner == 1 else 1
           )
       )


       reverse_moves = (
           generate_reverse_moves(
               current,
               reverse_player,
           )
       )


       if not reverse_moves:


           print(
               "\\nNo reverse moves available."
           )


           break


       chosen = rng.choice(
           reverse_moves
       )


       history.append(chosen)


       apply_reverse_move(
           current,
           chosen,
       )


   return {


       "board": current,


       "history": history,


       "repeated_board": repeated_board,


       "repeated_depth": repeated_depth,
   }
# -------------------------------------------------
# Example usage
# -------------------------------------------------




if __name__ == "__main__":


   winning_board = [
    [".", ".", "J", ".", ".", "J", ".","."],
    [".", "g", ".", ".", "R", ".", ".","J"],
    ["J", ".", "r", ".", "g", ".", ".","."],
    [".", ".", ".", "J", ".", ".", ".","."],
    [".", ".", ".", "r", "G", ".", ".","J"],
    ["J", ".", ".", ".", ".", ".", ".","."],
    [".", ".", ".", ".", ".", ".", ".","."],
    [".", "J", ".", ".", "J", ".", ".","J"],
]



   result = reverse_engineer_board(


       winning_board,


       winner=1,


       max_depth=25,


       seed=42,
   )


   print(
       "\\nGenerated Starting Board:"
   )


   print_board(
       result["board"]
   )


   print(
       "Reverse move count:",
       len(result["history"])
   )


   print()


   print(
       "Move history:"
   )


   for move in result["history"]:


       print(move)
