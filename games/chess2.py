import tkinter as tk
from tkinter import messagebox
import copy

# ── Piece Unicode symbols ──────────────────────────────────────────────────────
PIECES = {
    'wK': '♔', 'wQ': '♕', 'wR': '♖', 'wB': '♗', 'wN': '♘', 'wP': '♙',
    'bK': '♚', 'bQ': '♛', 'bR': '♜', 'bB': '♝', 'bN': '♞', 'bP': '♟',
}

# ── Initial board layout ───────────────────────────────────────────────────────
INITIAL_BOARD = [
    ['bR','bN','bB','bQ','bK','bB','bN','bR'],
    ['bP','bP','bP','bP','bP','bP','bP','bP'],
    [None]*8,
    [None]*8,
    [None]*8,
    [None]*8,
    ['wP','wP','wP','wP','wP','wP','wP','wP'],
    ['wR','wN','wB','wQ','wK','wB','wN','wR'],
]

LIGHT  = '#F0D9B5'
DARK   = '#B58863'
SEL    = '#7FC97F'
MOVE   = '#CDD16E'
CHECK  = '#E84040'
BG     = '#2C2C2C'
PANEL  = '#1A1A2E'
ACCENT = '#E2B96F'
TEXT   = '#F0EAD6'


class ChessGame:
    def __init__(self, root):
        self.root = root
        self.root.title('Chess')
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        self.board      = copy.deepcopy(INITIAL_BOARD)
        self.turn       = 'w'
        self.selected   = None
        self.valid_moves= []
        self.move_log   = []
        self.en_passant = None   # target square for en-passant capture
        self.castling   = {'w': {'K': True, 'Q': True}, 'b': {'K': True, 'Q': True}}
        self.in_check   = False
        self.game_over  = False

        self._build_ui()
        self._draw_board()
        self._update_status()

    # ── UI Construction ─────────────────────────────────────────────────────────
    def _build_ui(self):
        # Left panel: board
        board_frame = tk.Frame(self.root, bg=BG, padx=16, pady=16)
        board_frame.pack(side=tk.LEFT)

        # Rank labels (left)
        for r in range(8):
            lbl = tk.Label(board_frame, text=str(8 - r), fg=ACCENT, bg=BG,
                           font=('Georgia', 12, 'bold'), width=1)
            lbl.grid(row=r, column=0, padx=(0, 4))

        # Canvas squares
        self.sq_size = 72
        self.buttons = {}
        for r in range(8):
            for c in range(8):
                btn = tk.Label(board_frame, width=2, height=1,
                               font=('Segoe UI Symbol', 36),
                               cursor='hand2', relief='flat', bd=0)
                btn.grid(row=r, column=c + 1)
                btn.bind('<Button-1>', lambda e, row=r, col=c: self._on_click(row, col))
                self.buttons[(r, c)] = btn

        # File labels (bottom)
        for c, letter in enumerate('abcdefgh'):
            lbl = tk.Label(board_frame, text=letter, fg=ACCENT, bg=BG,
                           font=('Georgia', 12, 'bold'))
            lbl.grid(row=8, column=c + 1)

        # Right panel: info
        right = tk.Frame(self.root, bg=PANEL, width=210, padx=16, pady=20)
        right.pack(side=tk.RIGHT, fill=tk.BOTH)
        right.pack_propagate(False)

        tk.Label(right, text='♟  CHESS', font=('Georgia', 18, 'bold'),
                 fg=ACCENT, bg=PANEL).pack(pady=(0, 12))

        self.status_var = tk.StringVar()
        self.status_lbl = tk.Label(right, textvariable=self.status_var,
                                   font=('Georgia', 11, 'bold'), fg='#7FE07F',
                                   bg=PANEL, wraplength=180, justify='center')
        self.status_lbl.pack(pady=(0, 10))

        self.check_var = tk.StringVar()
        self.check_lbl = tk.Label(right, textvariable=self.check_var,
                                  font=('Georgia', 10, 'bold'), fg=CHECK,
                                  bg=PANEL)
        self.check_lbl.pack()

        tk.Frame(right, bg=ACCENT, height=1).pack(fill=tk.X, pady=12)

        tk.Label(right, text='Move History', font=('Georgia', 11, 'bold'),
                 fg=TEXT, bg=PANEL).pack()

        log_frame = tk.Frame(right, bg=PANEL)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=6)
        scrollbar = tk.Scrollbar(log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_box = tk.Listbox(log_frame, yscrollcommand=scrollbar.set,
                                  bg='#0D0D1A', fg=TEXT, selectbackground=ACCENT,
                                  font=('Courier', 10), relief='flat', bd=0,
                                  activestyle='none', height=16)
        self.log_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_box.yview)

        tk.Frame(right, bg=ACCENT, height=1).pack(fill=tk.X, pady=10)

        btn_frame = tk.Frame(right, bg=PANEL)
        btn_frame.pack()
        tk.Button(btn_frame, text='New Game', command=self._new_game,
                  font=('Georgia', 10, 'bold'), bg=ACCENT, fg='#1A1A2E',
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side=tk.LEFT, padx=4)
        tk.Button(btn_frame, text='Resign', command=self._resign,
                  font=('Georgia', 10, 'bold'), bg='#8B3030', fg=TEXT,
                  relief='flat', padx=12, pady=5, cursor='hand2').pack(side=tk.LEFT, padx=4)

    # ── Board Rendering ─────────────────────────────────────────────────────────
    def _draw_board(self):
        valid_set = set(self.valid_moves)
        king_pos  = self._find_king(self.turn) if self.in_check else None

        for r in range(8):
            for c in range(8):
                btn  = self.buttons[(r, c)]
                base = LIGHT if (r + c) % 2 == 0 else DARK

                if (r, c) == self.selected:
                    bg = SEL
                elif (r, c) in valid_set:
                    bg = MOVE
                elif (r, c) == king_pos:
                    bg = CHECK
                else:
                    bg = base

                piece = self.board[r][c]
                symbol = PIECES.get(piece, '') if piece else ''

                # Choose foreground based on piece color for contrast
                if piece and piece[0] == 'w':
                    fg = '#FFFFFF'
                elif piece and piece[0] == 'b':
                    fg = '#1A1A1A'
                else:
                    fg = base   # empty square

                btn.configure(bg=bg, activebackground=bg, text=symbol,
                               fg=fg, activeforeground=fg,
                               font=('Segoe UI Symbol', 34))

    def _update_status(self):
        color = 'White' if self.turn == 'w' else 'Black'
        if self.game_over:
            return
        self.status_var.set(f"{'⬜' if self.turn=='w' else '⬛'}  {color}'s turn")
        if self.in_check:
            self.check_var.set('⚠ CHECK!')
            self.check_lbl.configure(fg=CHECK)
        else:
            self.check_var.set('')

    # ── Click Handler ───────────────────────────────────────────────────────────
    def _on_click(self, row, col):
        if self.game_over:
            return

        piece = self.board[row][col]

        if self.selected is None:
            # Select a piece that belongs to current player
            if piece and piece[0] == self.turn:
                self.selected   = (row, col)
                self.valid_moves = self._get_legal_moves(row, col)
        else:
            if (row, col) == self.selected:
                # Deselect
                self.selected    = None
                self.valid_moves = []
            elif (row, col) in self.valid_moves:
                self._make_move(self.selected, (row, col))
                self.selected    = None
                self.valid_moves = []
            elif piece and piece[0] == self.turn:
                # Switch selection
                self.selected    = (row, col)
                self.valid_moves = self._get_legal_moves(row, col)
            else:
                self.selected    = None
                self.valid_moves = []

        self._draw_board()

    # ── Move Execution ──────────────────────────────────────────────────────────
    def _make_move(self, src, dst):
        sr, sc = src
        dr, dc = dst
        piece  = self.board[sr][sc]
        target = self.board[dr][dc]
        kind   = piece[1]

        # Algebraic notation
        files = 'abcdefgh'
        note  = ''

        # En-passant capture
        ep_capture = False
        if kind == 'P' and self.en_passant == (dr, dc):
            # Remove the captured pawn
            cap_row = sr   # same rank as moving pawn
            self.board[cap_row][dc] = None
            ep_capture = True
            note = f'{files[sc]}x{files[dc]}{8-dr} e.p.'

        # Set new en-passant target
        self.en_passant = None
        if kind == 'P' and abs(dr - sr) == 2:
            self.en_passant = ((sr + dr) // 2, dc)

        # Castling
        castled = False
        if kind == 'K' and abs(dc - sc) == 2:
            castled = True
            if dc > sc:   # kingside
                self.board[dr][dc-1] = self.board[dr][7]
                self.board[dr][7]    = None
                note = 'O-O'
            else:          # queenside
                self.board[dr][dc+1] = self.board[dr][0]
                self.board[dr][0]    = None
                note = 'O-O-O'

        # Update castling rights
        if kind == 'K':
            self.castling[self.turn]['K'] = False
            self.castling[self.turn]['Q'] = False
        if kind == 'R':
            if sc == 7: self.castling[self.turn]['K'] = False
            if sc == 0: self.castling[self.turn]['Q'] = False

        # Execute move
        self.board[dr][dc] = piece
        self.board[sr][sc] = None

        # Pawn promotion (auto-queen)
        if kind == 'P' and (dr == 0 or dr == 7):
            new_piece = self.turn + 'Q'
            self.board[dr][dc] = new_piece
            note = note or f'{files[sc]}{8-sr}={PIECES[new_piece]}'

        if not note:
            cap = 'x' if target else ''
            note = f'{files[sc]}{8-sr}{cap}→{files[dc]}{8-dr}'

        # Switch turns
        self.turn = 'b' if self.turn == 'w' else 'w'

        # Check / checkmate / stalemate
        self.in_check = self._is_in_check(self.turn)
        all_moves     = self._all_legal_moves(self.turn)

        move_num = (len(self.move_log) // 2) + 1
        prefix   = f'{move_num}. ' if (len(self.move_log) % 2 == 0) else '   '
        if self.in_check:
            if not all_moves:
                note += '#'
                self._end_game('Checkmate!', prefix + note)
            else:
                note += '+'
        elif not all_moves:
            note += ' ½'
            self._end_game('Stalemate!', prefix + note, draw=True)

        self.move_log.append(prefix + note)
        self.log_box.insert(tk.END, prefix + note)
        self.log_box.yview(tk.END)
        self._update_status()

    def _end_game(self, title, last_move, draw=False):
        self.game_over = True
        winner = 'Draw!' if draw else (
            'White wins!' if self.turn == 'b' else 'Black wins!'
        )
        self.status_var.set(f'🏆 {winner}')
        self.check_var.set(title)
        self.check_lbl.configure(fg=ACCENT)
        self._draw_board()
        messagebox.showinfo('Game Over', f'{title}\n{winner}')

    # ── Legal Move Generation ───────────────────────────────────────────────────
    def _get_legal_moves(self, row, col):
        pseudo = self._pseudo_moves(row, col, self.board)
        legal  = []
        for (dr, dc) in pseudo:
            if not self._move_leaves_king_in_check(row, col, dr, dc):
                legal.append((dr, dc))
        return legal

    def _all_legal_moves(self, color):
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p and p[0] == color:
                    for mv in self._get_legal_moves(r, c):
                        moves.append(((r, c), mv))
        return moves

    def _move_leaves_king_in_check(self, sr, sc, dr, dc):
        tmp = copy.deepcopy(self.board)
        # En-passant capture on tmp board
        if self.board[sr][sc] and self.board[sr][sc][1] == 'P' and self.en_passant == (dr, dc):
            tmp[sr][dc] = None
        # Castling rook on tmp board
        piece = tmp[sr][sc]
        if piece and piece[1] == 'K' and abs(dc - sc) == 2:
            if dc > sc:
                tmp[dr][dc-1] = tmp[dr][7]; tmp[dr][7] = None
            else:
                tmp[dr][dc+1] = tmp[dr][0]; tmp[dr][0] = None
        tmp[dr][dc] = tmp[sr][sc]
        tmp[sr][sc] = None
        return self._is_in_check(self.turn, tmp)

    def _is_in_check(self, color, board=None):
        if board is None:
            board = self.board
        king_pos = self._find_king(color, board)
        if not king_pos:
            return False
        opp = 'b' if color == 'w' else 'w'
        for r in range(8):
            for c in range(8):
                p = board[r][c]
                if p and p[0] == opp:
                    if king_pos in self._pseudo_moves(r, c, board, ignore_ep=True):
                        return True
        return False

    def _find_king(self, color, board=None):
        if board is None:
            board = self.board
        for r in range(8):
            for c in range(8):
                if board[r][c] == color + 'K':
                    return (r, c)
        return None

    def _pseudo_moves(self, row, col, board, ignore_ep=False):
        piece = board[row][col]
        if not piece:
            return []
        color, kind = piece[0], piece[1]
        opp   = 'b' if color == 'w' else 'w'
        moves = []

        def in_bounds(r, c): return 0 <= r < 8 and 0 <= c < 8
        def empty(r, c):     return board[r][c] is None
        def enemy(r, c):     return in_bounds(r,c) and board[r][c] and board[r][c][0] == opp

        def slide(dirs):
            for dr, dc in dirs:
                r, c = row + dr, col + dc
                while in_bounds(r, c):
                    if empty(r, c):
                        moves.append((r, c))
                    elif enemy(r, c):
                        moves.append((r, c)); break
                    else:
                        break
                    r += dr; c += dc

        if kind == 'P':
            direction = -1 if color == 'w' else 1
            start_row =  6 if color == 'w' else 1
            r = row + direction
            if in_bounds(r, col) and empty(r, col):
                moves.append((r, col))
                r2 = row + 2 * direction
                if row == start_row and empty(r2, col):
                    moves.append((r2, col))
            for dc in [-1, 1]:
                r, c = row + direction, col + dc
                if in_bounds(r, c):
                    if enemy(r, c):
                        moves.append((r, c))
                    elif not ignore_ep and self.en_passant == (r, c):
                        moves.append((r, c))

        elif kind == 'N':
            for dr, dc in [(-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1)]:
                r, c = row+dr, col+dc
                if in_bounds(r, c) and (empty(r, c) or enemy(r, c)):
                    moves.append((r, c))

        elif kind == 'B':
            slide([(-1,-1),(-1,1),(1,-1),(1,1)])

        elif kind == 'R':
            slide([(-1,0),(1,0),(0,-1),(0,1)])

        elif kind == 'Q':
            slide([(-1,-1),(-1,1),(1,-1),(1,1),(-1,0),(1,0),(0,-1),(0,1)])

        elif kind == 'K':
            for dr, dc in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
                r, c = row+dr, col+dc
                if in_bounds(r, c) and (empty(r, c) or enemy(r, c)):
                    moves.append((r, c))
            # Castling
            if not ignore_ep:
                back_rank = 7 if color == 'w' else 0
                if row == back_rank and col == 4:
                    # Kingside
                    if (self.castling[color]['K']
                            and empty(back_rank,5) and empty(back_rank,6)
                            and board[back_rank][7] == color+'R'
                            and not self._is_in_check(color, board)
                            and not self._sq_attacked(back_rank,5,color,board)
                            and not self._sq_attacked(back_rank,6,color,board)):
                        moves.append((back_rank, 6))
                    # Queenside
                    if (self.castling[color]['Q']
                            and empty(back_rank,3) and empty(back_rank,2) and empty(back_rank,1)
                            and board[back_rank][0] == color+'R'
                            and not self._is_in_check(color, board)
                            and not self._sq_attacked(back_rank,3,color,board)
                            and not self._sq_attacked(back_rank,2,color,board)):
                        moves.append((back_rank, 2))
        return moves

    def _sq_attacked(self, r, c, color, board):
        opp = 'b' if color == 'w' else 'w'
        for rr in range(8):
            for cc in range(8):
                p = board[rr][cc]
                if p and p[0] == opp:
                    if (r, c) in self._pseudo_moves(rr, cc, board, ignore_ep=True):
                        return True
        return False

    # ── Controls ────────────────────────────────────────────────────────────────
    def _new_game(self):
        self.board       = copy.deepcopy(INITIAL_BOARD)
        self.turn        = 'w'
        self.selected    = None
        self.valid_moves = []
        self.move_log    = []
        self.en_passant  = None
        self.castling    = {'w': {'K': True, 'Q': True}, 'b': {'K': True, 'Q': True}}
        self.in_check    = False
        self.game_over   = False
        self.log_box.delete(0, tk.END)
        self.check_var.set('')
        self._draw_board()
        self._update_status()

    def _resign(self):
        if self.game_over:
            return
        loser  = 'White' if self.turn == 'w' else 'Black'
        winner = 'Black' if self.turn == 'w' else 'White'
        self.game_over = True
        self.status_var.set(f'🏳 {loser} resigned')
        self.check_var.set(f'{winner} wins!')
        self.check_lbl.configure(fg=ACCENT)
        messagebox.showinfo('Resign', f'{loser} resigned.\n{winner} wins!')


# ── Entry Point ─────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    root = tk.Tk()
    root.title('Chess')
    game = ChessGame(root)
    root.mainloop()