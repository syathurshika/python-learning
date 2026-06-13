"""
Chess Game — Python Terminal Chess with AI Opponent
Features: Full chess rules, castling, en passant, promotion, AI via minimax + alpha-beta pruning
"""

import copy
import sys

# ── Piece constants ──────────────────────────────────────────────────────────
EMPTY = "."
WHITE, BLACK = "white", "black"

PIECES = {
    "K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙",
    "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟",
}

PIECE_VALUES = {"p": 100, "n": 320, "b": 330, "r": 500, "q": 900, "k": 20000}

# Piece-square tables for positional evaluation (from White's perspective)
PST = {
    "p": [
         0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
         5,  5, 10, 25, 25, 10,  5,  5,
         0,  0,  0, 20, 20,  0,  0,  0,
         5, -5,-10,  0,  0,-10, -5,  5,
         5, 10, 10,-20,-20, 10, 10,  5,
         0,  0,  0,  0,  0,  0,  0,  0,
    ],
    "n": [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50,
    ],
    "b": [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20,
    ],
    "r": [
         0,  0,  0,  0,  0,  0,  0,  0,
         5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
         0,  0,  0,  5,  5,  0,  0,  0,
    ],
    "q": [
        -20,-10,-10, -5, -5,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5,  5,  5,  5,  0,-10,
         -5,  0,  5,  5,  5,  5,  0, -5,
          0,  0,  5,  5,  5,  5,  0, -5,
        -10,  5,  5,  5,  5,  5,  0,-10,
        -10,  0,  5,  0,  0,  0,  0,-10,
        -20,-10,-10, -5, -5,-10,-10,-20,
    ],
    "k": [
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -30,-40,-40,-50,-50,-40,-40,-30,
        -20,-30,-30,-40,-40,-30,-30,-20,
        -10,-20,-20,-20,-20,-20,-20,-10,
         20, 20,  0,  0,  0,  0, 20, 20,
         20, 30, 10,  0,  0, 10, 30, 20,
    ],
}


# ── Board ────────────────────────────────────────────────────────────────────
def initial_board():
    board = [[EMPTY] * 8 for _ in range(8)]
    back = ["r", "n", "b", "q", "k", "b", "n", "r"]
    for c, p in enumerate(back):
        board[0][c] = p          # black back rank
        board[1][c] = "p"        # black pawns
        board[6][c] = "P"        # white pawns
        board[7][c] = p.upper()  # white back rank
    return board


def piece_color(piece):
    if piece == EMPTY:
        return None
    return WHITE if piece.isupper() else BLACK


def opponent(color):
    return BLACK if color == WHITE else WHITE


def in_bounds(r, c):
    return 0 <= r < 8 and 0 <= c < 8


# ── Move generation ──────────────────────────────────────────────────────────
def pawn_moves(board, r, c, color, ep_target):
    moves = []
    direction = -1 if color == WHITE else 1
    start_row = 6 if color == WHITE else 1

    # Forward
    nr = r + direction
    if in_bounds(nr, c) and board[nr][c] == EMPTY:
        moves.append((r, c, nr, c, None))
        if r == start_row:
            nr2 = r + 2 * direction
            if board[nr2][c] == EMPTY:
                moves.append((r, c, nr2, c, None))

    # Captures
    for dc in [-1, 1]:
        nr, nc = r + direction, c + dc
        if in_bounds(nr, nc):
            target = board[nr][nc]
            if target != EMPTY and piece_color(target) == opponent(color):
                moves.append((r, c, nr, nc, None))
            # En passant
            if ep_target and (nr, nc) == ep_target:
                moves.append((r, c, nr, nc, "ep"))

    # Promotion
    promo_row = 0 if color == WHITE else 7
    final = []
    for mv in moves:
        if mv[2] == promo_row:
            for promo in (["Q", "R", "B", "N"] if color == WHITE else ["q", "r", "b", "n"]):
                final.append((mv[0], mv[1], mv[2], mv[3], promo))
        else:
            final.append(mv)
    return final


def sliding_moves(board, r, c, color, directions):
    moves = []
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            target = board[nr][nc]
            if target == EMPTY:
                moves.append((r, c, nr, nc, None))
            elif piece_color(target) == opponent(color):
                moves.append((r, c, nr, nc, None))
                break
            else:
                break
            nr += dr
            nc += dc
    return moves


def knight_moves(board, r, c, color):
    moves = []
    for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
        nr, nc = r + dr, c + dc
        if in_bounds(nr, nc) and piece_color(board[nr][nc]) != color:
            moves.append((r, c, nr, nc, None))
    return moves


def king_moves(board, r, c, color):
    moves = []
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and piece_color(board[nr][nc]) != color:
                moves.append((r, c, nr, nc, None))
    return moves


def get_pseudo_moves(board, color, ep_target, castling_rights):
    moves = []
    king_r, king_c = (7, 4) if color == WHITE else (0, 4)

    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == EMPTY or piece_color(piece) != color:
                continue
            p = piece.lower()
            if p == "p":
                moves += pawn_moves(board, r, c, color, ep_target)
            elif p == "n":
                moves += knight_moves(board, r, c, color)
            elif p == "b":
                moves += sliding_moves(board, r, c, color, [(-1,-1),(-1,1),(1,-1),(1,1)])
            elif p == "r":
                moves += sliding_moves(board, r, c, color, [(-1,0),(1,0),(0,-1),(0,1)])
            elif p == "q":
                moves += sliding_moves(board, r, c, color,
                                       [(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)])
            elif p == "k":
                moves += king_moves(board, r, c, color)

    # Castling
    back_rank = 7 if color == WHITE else 0
    cr_key = color
    if castling_rights.get(cr_key, {}).get("king"):
        # King-side
        if (board[back_rank][5] == EMPTY and board[back_rank][6] == EMPTY
                and not is_square_attacked(board, back_rank, 4, color)
                and not is_square_attacked(board, back_rank, 5, color)
                and not is_square_attacked(board, back_rank, 6, color)):
            moves.append((back_rank, 4, back_rank, 6, "castle_k"))
    if castling_rights.get(cr_key, {}).get("queen"):
        # Queen-side
        if (board[back_rank][3] == EMPTY and board[back_rank][2] == EMPTY
                and board[back_rank][1] == EMPTY
                and not is_square_attacked(board, back_rank, 4, color)
                and not is_square_attacked(board, back_rank, 3, color)
                and not is_square_attacked(board, back_rank, 2, color)):
            moves.append((back_rank, 4, back_rank, 2, "castle_q"))

    return moves


def is_square_attacked(board, r, c, defending_color):
    """Return True if (r,c) is attacked by the opponent of defending_color."""
    attacker = opponent(defending_color)
    # Check all attacker pseudo-moves (without castling, no ep needed)
    for ar in range(8):
        for ac in range(8):
            piece = board[ar][ac]
            if piece == EMPTY or piece_color(piece) != attacker:
                continue
            p = piece.lower()
            if p == "p":
                d = -1 if attacker == WHITE else 1
                for dc in [-1, 1]:
                    if ar + d == r and ac + dc == c:
                        return True
            elif p == "n":
                for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                    if ar + dr == r and ac + dc == c:
                        return True
            elif p in ("b", "q"):
                for dr, dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
                    nr, nc = ar + dr, ac + dc
                    while in_bounds(nr, nc):
                        if nr == r and nc == c:
                            return True
                        if board[nr][nc] != EMPTY:
                            break
                        nr += dr; nc += dc
            if p in ("r", "q"):
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nr, nc = ar + dr, ac + dc
                    while in_bounds(nr, nc):
                        if nr == r and nc == c:
                            return True
                        if board[nr][nc] != EMPTY:
                            break
                        nr += dr; nc += dc
            elif p == "k":
                if abs(ar - r) <= 1 and abs(ac - c) <= 1:
                    return True
    return False


def find_king(board, color):
    king = "K" if color == WHITE else "k"
    for r in range(8):
        for c in range(8):
            if board[r][c] == king:
                return r, c
    return None


def apply_move(board, move, color, ep_target, castling_rights):
    """Returns (new_board, new_ep_target, new_castling_rights)."""
    r1, c1, r2, c2, flag = move
    board = copy.deepcopy(board)
    castling_rights = copy.deepcopy(castling_rights)
    piece = board[r1][c1]
    new_ep = None

    # En passant capture
    if flag == "ep":
        direction = -1 if color == WHITE else 1
        board[r2 - direction][c2] = EMPTY

    # Castling rook move
    if flag == "castle_k":
        back = r1
        board[back][5] = board[back][7]
        board[back][7] = EMPTY
    if flag == "castle_q":
        back = r1
        board[back][3] = board[back][0]
        board[back][0] = EMPTY

    # Move piece
    board[r2][c2] = piece
    board[r1][c1] = EMPTY

    # Promotion
    if flag and flag not in ("ep", "castle_k", "castle_q"):
        board[r2][c2] = flag

    # Set en passant target
    p = piece.lower()
    if p == "p" and abs(r2 - r1) == 2:
        new_ep = ((r1 + r2) // 2, c1)

    # Update castling rights
    if p == "k":
        castling_rights[color] = {"king": False, "queen": False}
    if p == "r":
        back = 7 if color == WHITE else 0
        if r1 == back and c1 == 0:
            castling_rights[color]["queen"] = False
        if r1 == back and c1 == 7:
            castling_rights[color]["king"] = False

    return board, new_ep, castling_rights


def get_legal_moves(board, color, ep_target, castling_rights):
    legal = []
    for mv in get_pseudo_moves(board, color, ep_target, castling_rights):
        new_board, _, _ = apply_move(board, mv, color, ep_target, castling_rights)
        kr, kc = find_king(new_board, color)
        if kr is not None and not is_square_attacked(new_board, kr, kc, color):
            legal.append(mv)
    return legal


def is_in_check(board, color):
    kr, kc = find_king(board, color)
    return kr is not None and is_square_attacked(board, kr, kc, color)


# ── Evaluation ───────────────────────────────────────────────────────────────
def evaluate(board):
    score = 0
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece == EMPTY:
                continue
            p = piece.lower()
            val = PIECE_VALUES.get(p, 0)
            idx = r * 8 + c if piece.islower() else (7 - r) * 8 + c
            pst_val = PST.get(p, [0]*64)[idx]
            if piece.isupper():
                score += val + pst_val
            else:
                score -= val + pst_val
    return score


# ── Minimax with Alpha-Beta ──────────────────────────────────────────────────
def minimax(board, depth, alpha, beta, maximizing, color, ep_target, castling_rights):
    legal = get_legal_moves(board, color, ep_target, castling_rights)

    if depth == 0 or not legal:
        if not legal:
            if is_in_check(board, color):
                return -99999 if maximizing else 99999
            return 0  # Stalemate
        return evaluate(board)

    if maximizing:
        best = -float("inf")
        for mv in legal:
            nb, nep, ncr = apply_move(board, mv, color, ep_target, castling_rights)
            val = minimax(nb, depth - 1, alpha, beta, False, opponent(color), nep, ncr)
            best = max(best, val)
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    else:
        best = float("inf")
        for mv in legal:
            nb, nep, ncr = apply_move(board, mv, color, ep_target, castling_rights)
            val = minimax(nb, depth - 1, alpha, beta, True, opponent(color), nep, ncr)
            best = min(best, val)
            beta = min(beta, best)
            if beta <= alpha:
                break
        return best


def best_ai_move(board, color, ep_target, castling_rights, depth=3):
    legal = get_legal_moves(board, color, ep_target, castling_rights)
    if not legal:
        return None
    maximizing = color == WHITE
    best_val = -float("inf") if maximizing else float("inf")
    best_mv = legal[0]
    for mv in legal:
        nb, nep, ncr = apply_move(board, mv, color, ep_target, castling_rights)
        val = minimax(nb, depth - 1, -float("inf"), float("inf"),
                      not maximizing, opponent(color), nep, ncr)
        if maximizing and val > best_val:
            best_val, best_mv = val, mv
        elif not maximizing and val < best_val:
            best_val, best_mv = val, mv
    return best_mv


# ── Display ──────────────────────────────────────────────────────────────────
def display(board, flipped=False, last_move=None):
    rows = range(8) if not flipped else range(7, -1, -1)
    cols = range(8) if not flipped else range(7, -1, -1)
    print()
    print("    a   b   c   d   e   f   g   h" if not flipped
          else "    h   g   f   e   d   c   b   a")
    print("  ┌───┬───┬───┬───┬───┬───┬───┬───┐")
    for ri, r in enumerate(rows):
        rank_label = 8 - r
        row_str = f"{rank_label} │"
        for c in cols:
            piece = board[r][c]
            sym = PIECES.get(piece, " ")
            # Highlight last move squares
            if last_move and (r, c) in [(last_move[0], last_move[1]), (last_move[2], last_move[3])]:
                row_str += f"\033[43m {sym} \033[0m│"
            else:
                # Checkerboard shade
                if (r + c) % 2 == 0:
                    row_str += f"\033[47m {sym} \033[0m│"
                else:
                    row_str += f" {sym} │"
        print(row_str + f" {rank_label}")
        if ri < 7:
            print("  ├───┼───┼───┼───┼───┼───┼───┼───┤")
    print("  └───┴───┴───┴───┴───┴───┴───┴───┘")
    print("    a   b   c   d   e   f   g   h" if not flipped
          else "    h   g   f   e   d   c   b   a")
    print()


def parse_move(text):
    """Parse algebraic notation like e2e4 or e2-e4."""
    text = text.strip().lower().replace("-", "").replace(" ", "")
    if len(text) < 4:
        return None
    try:
        c1 = ord(text[0]) - ord("a")
        r1 = 8 - int(text[1])
        c2 = ord(text[2]) - ord("a")
        r2 = 8 - int(text[3])
        promo = text[4].upper() if len(text) == 5 else None
        if not (in_bounds(r1, c1) and in_bounds(r2, c2)):
            return None
        return r1, c1, r2, c2, promo
    except Exception:
        return None


def move_to_notation(mv):
    r1, c1, r2, c2, flag = mv
    s = f"{chr(ord('a')+c1)}{8-r1}{chr(ord('a')+c2)}{8-r2}"
    if flag and flag not in ("ep", "castle_k", "castle_q"):
        s += flag.lower()
    return s


# ── Main Game Loop ────────────────────────────────────────────────────────────
def main():
    print("\n╔══════════════════════════════════════╗")
    print("║        ♟  PYTHON  CHESS  ♟          ║")
    print("╚══════════════════════════════════════╝")
    print("\nCommands:  <move>  e.g. e2e4  |  quit  |  help")
    print("Promotion: e7e8q  (append q/r/b/n)\n")

    mode = input("Play as [w]hite, [b]lack, or [2] player? ").strip().lower()
    if mode not in ("w", "b", "2"):
        mode = "w"

    human_color = WHITE if mode in ("w", "2") else BLACK
    two_player = mode == "2"

    board = initial_board()
    ep_target = None
    castling_rights = {
        WHITE: {"king": True, "queen": True},
        BLACK: {"king": True, "queen": True},
    }
    turn = WHITE
    last_move = None
    move_history = []

    while True:
        flipped = (turn == BLACK and not two_player)
        display(board, flipped=flipped, last_move=last_move)

        in_check = is_in_check(board, turn)
        legal = get_legal_moves(board, turn, ep_target, castling_rights)

        if not legal:
            if in_check:
                winner = opponent(turn).capitalize()
                print(f"♛  Checkmate! {winner} wins!\n")
            else:
                print("½  Stalemate! It's a draw.\n")
            break

        turn_label = "White" if turn == WHITE else "Black"
        check_str = "  ⚠  CHECK!" if in_check else ""
        print(f"  {turn_label}'s turn{check_str}")

        # AI move
        if not two_player and turn != human_color:
            print("  AI is thinking…")
            mv = best_ai_move(board, turn, ep_target, castling_rights, depth=3)
            if mv:
                board, ep_target, castling_rights = apply_move(
                    board, mv, turn, ep_target, castling_rights)
                last_move = mv
                move_history.append(move_to_notation(mv))
                print(f"  AI plays: {move_to_notation(mv)}")
            turn = opponent(turn)
            continue

        # Human move
        raw = input("  Your move: ").strip().lower()
        if raw in ("quit", "exit", "q"):
            print("  Goodbye! ♟")
            sys.exit()
        if raw == "help":
            print("  Enter moves as: e2e4  (from-square to-square)")
            print("  Promotion:       e7e8q")
            print("  Legal moves:")
            for m in legal:
                print(f"    {move_to_notation(m)}", end="")
            print()
            continue
        if raw == "moves":
            print("  Move history:", " ".join(move_history) or "(none)")
            continue

        parsed = parse_move(raw)
        if parsed is None:
            print("  ✗  Invalid format. Try: e2e4")
            continue

        r1, c1, r2, c2, promo_hint = parsed

        # Match against legal moves
        matched = None
        for lm in legal:
            lr1, lc1, lr2, lc2, lf = lm
            if lr1 == r1 and lc1 == c1 and lr2 == r2 and lc2 == c2:
                if lf in ("ep", "castle_k", "castle_q", None):
                    matched = lm
                    break
                # Promotion — match flag
                if promo_hint:
                    flag_piece = promo_hint if turn == WHITE else promo_hint.lower()
                    if lf == flag_piece:
                        matched = lm
                        break
                else:
                    matched = lm  # default: take first match (queen)
                    break

        if matched is None:
            print("  ✗  Illegal move.")
            continue

        board, ep_target, castling_rights = apply_move(
            board, matched, turn, ep_target, castling_rights)
        last_move = matched
        move_history.append(move_to_notation(matched))
        turn = opponent(turn)


if __name__ == "__main__":
    main()