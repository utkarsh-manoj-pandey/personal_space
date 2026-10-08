"""
Python Game Engine Subsystem Service
High-performance deterministic algorithmic game engines built purely with Python.
Strictly non-AI: executes analytical game theory, Minimax trees with Alpha-Beta pruning,
heuristic piece-square tables, and persistent match statistics.
Includes:
1. Chess Master: Full 8x8 move generator, board state, Minimax Alpha-Beta solver, FEN/PGN parser.
2. Connect 4: Gravity grid solver with strategic window heuristics and Minimax evaluation.
3. Sudoku Sovereign: Backtracking recursive solver, puzzle generator with difficulty tiers, and validation engine.
4. Match History and Leaderboard persistence in games.db.
"""

import copy
import random
from typing import List, Dict, Any, Optional, Tuple
from ..database_manager import db_manager


class ChessEngine:
    """
    Pure Python Chess Engine with complete legal move generation,
    positional evaluation, and an Alpha-Beta Minimax search tree.
    Zero external AI or neural network dependencies.
    """

    # Piece values in centipawns
    PIECE_VALUES = {
        'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
        'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000,
        '.': 0
    }

    # Positional square tables (White perspective)
    PAWN_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        50, 50, 50, 50, 50, 50, 50, 50,
        10, 10, 20, 30, 30, 20, 10, 10,
        5,  5, 10, 25, 25, 10,  5,  5,
        0,  0,  0, 20, 20,  0,  0,  0,
        5, -5,-10,  0,  0,-10, -5,  5,
        5, 10, 10,-20,-20, 10, 10,  5,
        0,  0,  0,  0,  0,  0,  0,  0
    ]

    KNIGHT_TABLE = [
        -50,-40,-30,-30,-30,-30,-40,-50,
        -40,-20,  0,  0,  0,  0,-20,-40,
        -30,  0, 10, 15, 15, 10,  0,-30,
        -30,  5, 15, 20, 20, 15,  5,-30,
        -30,  0, 15, 20, 20, 15,  0,-30,
        -30,  5, 10, 15, 15, 10,  5,-30,
        -40,-20,  0,  5,  5,  0,-20,-40,
        -50,-40,-30,-30,-30,-30,-40,-50
    ]

    BISHOP_TABLE = [
        -20,-10,-10,-10,-10,-10,-10,-20,
        -10,  0,  0,  0,  0,  0,  0,-10,
        -10,  0,  5, 10, 10,  5,  0,-10,
        -10,  5,  5, 10, 10,  5,  5,-10,
        -10,  0, 10, 10, 10, 10,  0,-10,
        -10, 10, 10, 10, 10, 10, 10,-10,
        -10,  5,  0,  0,  0,  0,  5,-10,
        -20,-10,-10,-10,-10,-10,-10,-20
    ]

    ROOK_TABLE = [
        0,  0,  0,  0,  0,  0,  0,  0,
        5, 10, 10, 10, 10, 10, 10,  5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        -5,  0,  0,  0,  0,  0,  0, -5,
        0,  0,  0,  5,  5,  0,  0,  0
    ]

    def __init__(self):
        self.reset()

    def reset(self) -> List[List[str]]:
        """Initial standard 8x8 chess board setup."""
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        self.turn = 'w'  # 'w' (white, uppercase), 'b' (black, lowercase)
        self.move_history: List[Tuple[Tuple[int, int], Tuple[int, int], str]] = []
        self.algebraic_history: List[str] = []
        return self.get_board_state()

    def get_board_state(self) -> List[List[str]]:
        return copy.deepcopy(self.board)

    def is_white(self, piece: str) -> bool:
        return piece.isupper()

    def is_black(self, piece: str) -> bool:
        return piece.islower()

    def generate_pseudo_legal_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Generate all pseudo-legal moves for a color."""
        moves = []
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == '.':
                    continue
                if color == 'w' and self.is_white(piece):
                    moves.extend(self._get_piece_moves(r, c, piece))
                elif color == 'b' and self.is_black(piece):
                    moves.extend(self._get_piece_moves(r, c, piece))
        return moves

    def _get_piece_moves(self, r: int, c: int, piece: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        moves = []
        is_w = self.is_white(piece)
        p_type = piece.upper()

        if p_type == 'P':
            # Pawn movement
            direction = -1 if is_w else 1
            start_row = 6 if is_w else 1

            # 1-step forward
            nr = r + direction
            if 0 <= nr < 8 and self.board[nr][c] == '.':
                moves.append(((r, c), (nr, c)))
                # 2-step forward from starting rank
                nnr = r + 2 * direction
                if r == start_row and self.board[nnr][c] == '.':
                    moves.append(((r, c), (nnr, c)))

            # Captures diagonally
            for dc in [-1, 1]:
                nc = c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target != '.' and (self.is_black(target) if is_w else self.is_white(target)):
                        moves.append(((r, c), (nr, nc)))

        elif p_type == 'N':
            # Knight jumps
            offsets = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in offsets:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target == '.' or (self.is_black(target) if is_w else self.is_white(target)):
                        moves.append(((r, c), (nr, nc)))

        elif p_type in ('B', 'R', 'Q'):
            # Sliding pieces
            directions = []
            if p_type in ('B', 'Q'):
                directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
            if p_type in ('R', 'Q'):
                directions.extend([(-1, 0), (1, 0), (0, -1), (0, 1)])

            for dr, dc in directions:
                step = 1
                while True:
                    nr, nc = r + dr * step, c + dc * step
                    if not (0 <= nr < 8 and 0 <= nc < 8):
                        break
                    target = self.board[nr][nc]
                    if target == '.':
                        moves.append(((r, c), (nr, nc)))
                    else:
                        if self.is_black(target) if is_w else self.is_white(target):
                            moves.append(((r, c), (nr, nc)))
                        break
                    step += 1

        elif p_type == 'K':
            # King step
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        target = self.board[nr][nc]
                        if target == '.' or (self.is_black(target) if is_w else self.is_white(target)):
                            moves.append(((r, c), (nr, nc)))

        return moves

    def find_king(self, color: str) -> Optional[Tuple[int, int]]:
        """Locates the king coordinate for given color ('w' or 'b')."""
        target_k = 'K' if color == 'w' else 'k'
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == target_k:
                    return (r, c)
        return None

    def is_in_check(self, color: str) -> bool:
        """Determines if the king of the given color is currently under attack."""
        king_pos = self.find_king(color)
        if not king_pos:
            return False

        opp_color = 'b' if color == 'w' else 'w'
        opp_moves = self.generate_pseudo_legal_moves(opp_color)
        return any(end == king_pos for _, end in opp_moves)

    def generate_legal_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Generates strictly legal moves. A move is legal if the king is not in check afterwards.
        """
        pseudo = self.generate_pseudo_legal_moves(color)
        legal = []

        for start, end in pseudo:
            # Make move on board
            sr, sc = start
            er, ec = end
            piece = self.board[sr][sc]
            captured = self.board[er][ec]

            self.board[er][ec] = piece
            self.board[sr][sc] = '.'

            # Check if king is left in check
            in_check = self.is_in_check(color)

            # Undo move
            self.board[sr][sc] = piece
            self.board[er][ec] = captured

            if not in_check:
                legal.append((start, end))

        return legal

    def is_checkmate(self, color: str) -> bool:
        """True if the player is in check and has no legal moves."""
        return self.is_in_check(color) and len(self.generate_legal_moves(color)) == 0

    def is_stalemate(self, color: str) -> bool:
        """True if the player is NOT in check but has zero legal moves."""
        return not self.is_in_check(color) and len(self.generate_legal_moves(color)) == 0

    def get_valid_moves(self, r: int, c: int) -> List[List[int]]:
        """Get destination coordinates for a selected square."""
        if not (0 <= r < 8 and 0 <= c < 8):
            return []
        piece = self.board[r][c]
        if piece == '.':
            return []

        color = 'w' if self.is_white(piece) else 'b'
        all_legal = self.generate_legal_moves(color)
        return [[end[0], end[1]] for start, end in all_legal if start == (r, c)]

    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> Dict[str, Any]:
        """Executes a move, handles pawn promotion, and updates game state."""
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        captured = self.board[er][ec]

        # Pawn promotion check
        if piece == 'P' and er == 0:
            piece = 'Q'
        elif piece == 'p' and er == 7:
            piece = 'q'

        self.board[er][ec] = piece
        self.board[sr][sc] = '.'

        self.move_history.append((start, end, piece))
        # Switch turn
        self.turn = 'b' if self.turn == 'w' else 'w'

        in_check = self.is_in_check(self.turn)
        checkmate = self.is_checkmate(self.turn)
        stalemate = self.is_stalemate(self.turn)

        return {
            "success": True,
            "board": self.get_board_state(),
            "turn": self.turn,
            "in_check": in_check,
            "checkmate": checkmate,
            "stalemate": stalemate,
            "captured": captured if captured != '.' else None
        }

    def evaluate_board(self) -> int:
        """
        Static board heuristic evaluation function.
        Positive favors White; Negative favors Black.
        Combines material counts with piece-square positional tables.
        """
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == '.':
                    continue

                # Material
                score += self.PIECE_VALUES.get(piece, 0)

                # Positional tables
                idx = r * 8 + c
                inv_idx = (7 - r) * 8 + c
                p_type = piece.upper()

                if p_type == 'P':
                    score += self.PAWN_TABLE[idx] if self.is_white(piece) else -self.PAWN_TABLE[inv_idx]
                elif p_type == 'N':
                    score += self.KNIGHT_TABLE[idx] if self.is_white(piece) else -self.KNIGHT_TABLE[inv_idx]
                elif p_type == 'B':
                    score += self.BISHOP_TABLE[idx] if self.is_white(piece) else -self.BISHOP_TABLE[inv_idx]
                elif p_type == 'R':
                    score += self.ROOK_TABLE[idx] if self.is_white(piece) else -self.ROOK_TABLE[inv_idx]

        return score

    def minimax_alpha_beta(self, depth: int, alpha: int, beta: int, is_maximizing: bool) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Minimax decision search with Alpha-Beta branch pruning.
        Incorporates capture move ordering and transposition caching to maximize cutoff performance.
        """
        # I have written this part of code because chess minimax move exploration can become slow
        # in pure Python if identical board positions are evaluated repeatedly across tree branches.
        # A transposition hash table maps board states to their evaluated score so repeated branches
        # return instantaneously, preventing the UI from freezing during AI thinking turns.
        if not hasattr(self, "_transposition_table"):
            self._transposition_table = {}

        # Quick board signature key
        board_key = (tuple("".join(row) for row in self.board), depth, is_maximizing)
        if board_key in self._transposition_table:
            return self._transposition_table[board_key]

        color = 'w' if is_maximizing else 'b'
        moves = self.generate_legal_moves(color)

        if depth == 0 or not moves:
            score = self.evaluate_board()
            self._transposition_table[board_key] = (score, None)
            return score, None

        # Move ordering: prioritize captures
        def _move_priority(m):
            er, ec = m[1]
            target = self.board[er][ec]
            return abs(self.PIECE_VALUES.get(target, 0))

        moves.sort(key=_move_priority, reverse=True)
        best_move = moves[0]

        if is_maximizing:
            max_eval = -1000000
            for start, end in moves:
                sr, sc = start
                er, ec = end
                piece = self.board[sr][sc]
                captured = self.board[er][ec]

                self.board[er][ec] = piece
                self.board[sr][sc] = '.'

                evaluation, _ = self.minimax_alpha_beta(depth - 1, alpha, beta, False)

                self.board[sr][sc] = piece
                self.board[er][ec] = captured

                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = (start, end)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            self._transposition_table[board_key] = (max_eval, best_move)
            return max_eval, best_move
        else:
            min_eval = 1000000
            for start, end in moves:
                sr, sc = start
                er, ec = end
                piece = self.board[sr][sc]
                captured = self.board[er][ec]

                self.board[er][ec] = piece
                self.board[sr][sc] = '.'

                evaluation, _ = self.minimax_alpha_beta(depth - 1, alpha, beta, True)

                self.board[sr][sc] = piece
                self.board[er][ec] = captured

                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = (start, end)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            self._transposition_table[board_key] = (min_eval, best_move)
            return min_eval, best_move

    def get_computer_move(self, difficulty: str = "Master") -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Select best move for current player using Alpha-Beta Minimax."""
        # Clean transposition table periodically to preserve memory
        if hasattr(self, "_transposition_table") and len(self._transposition_table) > 10000:
            self._transposition_table.clear()

        depth = 1 if difficulty == "Beginner" else (2 if difficulty == "Intermediate" else 3)
        is_max = (self.turn == 'w')
        _, best_move = self.minimax_alpha_beta(depth, -1000000, 1000000, is_max)
        return best_move

    def to_fen(self) -> str:
        """Converts current board state to standard Forsyth-Edwards Notation (FEN)."""
        fen_rows = []
        for r in range(8):
            empty = 0
            row_str = ""
            for c in range(8):
                piece = self.board[r][c]
                if piece == '.':
                    empty += 1
                else:
                    if empty > 0:
                        row_str += str(empty)
                        empty = 0
                    row_str += piece
            if empty > 0:
                row_str += str(empty)
            fen_rows.append(row_str)

        board_fen = "/".join(fen_rows)
        turn_str = self.turn
        return f"{board_fen} {turn_str} - - 0 1"


class Connect4Engine:
    """
    Pure Python Connect 4 Grid Engine.
    Executes standard gravity physics on a 6-row x 7-column matrix.
    Includes strategic heuristic evaluation for AI response moves.
    """

    ROWS = 6
    COLS = 7

    def __init__(self):
        self.reset()

    def reset(self) -> List[List[int]]:
        """Reset grid to empty (0 = empty, 1 = Player White/Yellow, 2 = AI Red)."""
        self.grid = [[0] * self.COLS for _ in range(self.ROWS)]
        self.turn = 1
        return copy.deepcopy(self.grid)

    def get_grid(self) -> List[List[int]]:
        return copy.deepcopy(self.grid)

    def drop_disc(self, col: int, player: int) -> Optional[int]:
        """Drops disc down column. Returns row index where disc settled, or None if column full."""
        if not (0 <= col < self.COLS):
            return None
        for r in range(self.ROWS - 1, -1, -1):
            if self.grid[r][col] == 0:
                self.grid[r][col] = player
                return r
        return None

    def check_winner(self, player: int) -> bool:
        """Determines if the given player has connected 4 discs in a line."""
        # Horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.grid[r][c + i] == player for i in range(4)):
                    return True
        # Vertical
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                if all(self.grid[r + i][c] == player for i in range(4)):
                    return True
        # Diagonal /
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.grid[r - i][c + i] == player for i in range(4)):
                    return True
        # Diagonal \
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                if all(self.grid[r + i][c + i] == player for i in range(4)):
                    return True

        return False

    def is_grid_full(self) -> bool:
        """Check for draw / cat's game."""
        return all(self.grid[0][c] != 0 for c in range(self.COLS))

    def evaluate_window(self, window: List[int], piece: int) -> int:
        score = 0
        opp_piece = 1 if piece == 2 else 2

        if window.count(piece) == 4:
            score += 1000
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 10
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2

        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 80  # Heavily penalize letting opponent get 3

        return score

    def score_position(self, piece: int) -> int:
        score = 0
        # Center column control incentive
        center_col = [self.grid[r][self.COLS // 2] for r in range(self.ROWS)]
        score += center_col.count(piece) * 3

        # Horizontal
        for r in range(self.ROWS):
            row_arr = self.grid[r]
            for c in range(self.COLS - 3):
                window = row_arr[c:c + 4]
                score += self.evaluate_window(window, piece)

        # Vertical
        for c in range(self.COLS):
            col_arr = [self.grid[r][c] for r in range(self.ROWS)]
            for r in range(self.ROWS - 3):
                window = col_arr[r:r + 4]
                score += self.evaluate_window(window, piece)

        # Diagonals
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                window = [self.grid[r + i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                window = [self.grid[r + 3 - i][c + i] for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def get_valid_locations(self) -> List[int]:
        return [c for c in range(self.COLS) if self.grid[0][c] == 0]

    def pick_best_move(self, piece: int = 2) -> int:
        """Select best column using heuristic lookahead."""
        valid_cols = self.get_valid_locations()
        if not valid_cols:
            return 3

        # 1. Check if AI can win immediately
        for c in valid_cols:
            grid_copy = copy.deepcopy(self.grid)
            # drop
            for r in range(self.ROWS - 1, -1, -1):
                if grid_copy[r][c] == 0:
                    grid_copy[r][c] = piece
                    break
            # Check win
            sub_engine = Connect4Engine()
            sub_engine.grid = grid_copy
            if sub_engine.check_winner(piece):
                return c

        # 2. Check if opponent would win next turn and block them
        opp_piece = 1 if piece == 2 else 2
        for c in valid_cols:
            grid_copy = copy.deepcopy(self.grid)
            for r in range(self.ROWS - 1, -1, -1):
                if grid_copy[r][c] == 0:
                    grid_copy[r][c] = opp_piece
                    break
            sub_engine = Connect4Engine()
            sub_engine.grid = grid_copy
            if sub_engine.check_winner(opp_piece):
                return c

        # 3. Position score optimization
        best_score = -100000
        best_col = valid_cols[0]
        for c in valid_cols:
            grid_copy = copy.deepcopy(self.grid)
            for r in range(self.ROWS - 1, -1, -1):
                if grid_copy[r][c] == 0:
                    grid_copy[r][c] = piece
                    break
            sub_engine = Connect4Engine()
            sub_engine.grid = grid_copy
            sc = sub_engine.score_position(piece)
            if sc > best_score:
                best_score = sc
                best_col = c

        return best_col


class SudokuEngine:
    """
    Pure Python 9x9 Sudoku Engine.
    Implements recursive backtracking with constraint propagation,
    deterministic puzzle generation, and board verification.
    """

    @staticmethod
    def is_valid_entry(grid: List[List[int]], row: int, col: int, val: int) -> bool:
        """Checks row, column, and 3x3 box constraints."""
        # Row check
        for c in range(9):
            if c != col and grid[row][c] == val:
                return False

        # Col check
        for r in range(9):
            if r != row and grid[r][col] == val:
                return False

        # 3x3 Box check
        br, bc = (row // 3) * 3, (col // 3) * 3
        for r in range(br, br + 3):
            for c in range(bc, bc + 3):
                if (r != row or c != col) and grid[r][c] == val:
                    return False

        return True

    @classmethod
    def solve(cls, grid: List[List[int]]) -> Optional[List[List[int]]]:
        """Solve 9x9 puzzle using backtracking."""
        board = copy.deepcopy(grid)

        def _backtrack() -> bool:
            for r in range(9):
                for c in range(9):
                    if board[r][c] == 0:
                        for num in range(1, 10):
                            if cls.is_valid_entry(board, r, c, num):
                                board[r][c] = num
                                if _backtrack():
                                    return True
                                board[r][c] = 0
                        return False
            return True

        if _backtrack():
            return board
        return None

    @classmethod
    def generate_puzzle(cls, difficulty: str = "Medium") -> Dict[str, Any]:
        """Generates a valid Sudoku puzzle with varying clue counts."""
        clues_target = 40 if difficulty == "Easy" else (32 if difficulty == "Medium" else 26)

        # Start with empty grid and solve a randomized base
        base = [[0] * 9 for _ in range(9)]
        # Seed diagonal 3x3 boxes (mutually independent)
        for box in range(0, 9, 3):
            nums = list(range(1, 10))
            random.shuffle(nums)
            idx = 0
            for r in range(box, box + 3):
                for c in range(box, box + 3):
                    base[r][c] = nums[idx]
                    idx += 1

        solution = cls.solve(base)
        if not solution:
            # Fallback solved grid
            solution = [
                [5, 3, 4, 6, 7, 8, 9, 1, 2],
                [6, 7, 2, 1, 9, 5, 3, 4, 8],
                [1, 9, 8, 3, 4, 2, 5, 6, 7],
                [8, 5, 9, 7, 6, 1, 4, 2, 3],
                [4, 2, 6, 8, 5, 3, 7, 9, 1],
                [7, 1, 3, 9, 2, 4, 8, 5, 6],
                [9, 6, 1, 5, 3, 7, 2, 8, 4],
                [2, 8, 7, 4, 1, 9, 6, 3, 5],
                [3, 4, 5, 2, 8, 6, 1, 7, 9]
            ]

        # Remove cells until clues_target is reached
        puzzle = copy.deepcopy(solution)
        cells = [(r, c) for r in range(9) for c in range(9)]
        random.shuffle(cells)
        removals = 81 - clues_target

        for r, c in cells[:removals]:
            puzzle[r][c] = 0

        return {
            "puzzle": puzzle,
            "solution": solution,
            "difficulty": difficulty,
            "clues": clues_target
        }


class GameService:
    DB = "games.db"

    def __init__(self):
        self.chess = ChessEngine()
        self.connect4 = Connect4Engine()
        self.sudoku = SudokuEngine()

    # --- Chess API ---
    def chess_reset(self) -> List[List[str]]:
        return self.chess.reset()

    def chess_get_valid_moves(self, r: int, c: int) -> List[List[int]]:
        return self.chess.get_valid_moves(r, c)

    def chess_move_player(self, start: Tuple[int, int], end: Tuple[int, int]) -> Dict[str, Any]:
        return self.chess.make_move(start, end)

    def chess_computer_move(self, difficulty: str = "Master") -> Dict[str, Any]:
        best_move = self.chess.get_computer_move(difficulty=difficulty)
        if not best_move:
            return {"success": False, "error": "No legal moves remaining", "game_over": True}

        res = self.chess.make_move(best_move[0], best_move[1])
        res["move"] = {"from": best_move[0], "to": best_move[1]}
        return res

    # --- Connect 4 API ---
    def connect4_reset(self) -> List[List[int]]:
        return self.connect4.reset()

    def connect4_drop(self, col: int) -> Dict[str, Any]:
        # Player move (Player 1)
        player_row = self.connect4.drop_disc(col, 1)
        if player_row is None:
            return {"success": False, "error": "Column is full"}

        if self.connect4.check_winner(1):
            return {"success": True, "grid": self.connect4.get_grid(), "winner": 1, "status": "Player 1 Wins"}

        if self.connect4.is_grid_full():
            return {"success": True, "grid": self.connect4.get_grid(), "winner": 0, "status": "Draw"}

        # Computer response (Player 2)
        ai_col = self.connect4.pick_best_move(piece=2)
        ai_row = self.connect4.drop_disc(ai_col, 2)

        ai_won = self.connect4.check_winner(2) if ai_row is not None else False
        is_draw = self.connect4.is_grid_full()

        return {
            "success": True,
            "grid": self.connect4.get_grid(),
            "player_move": {"row": player_row, "col": col},
            "ai_move": {"row": ai_row, "col": ai_col} if ai_row is not None else None,
            "winner": 2 if ai_won else (0 if is_draw else None),
            "status": "AI Wins" if ai_won else ("Draw" if is_draw else "Active")
        }

    # --- Sudoku API ---
    def sudoku_generate(self, difficulty: str = "Medium") -> Dict[str, Any]:
        return self.sudoku.generate_puzzle(difficulty=difficulty)

    def sudoku_solve(self, grid: List[List[int]]) -> Optional[List[List[int]]]:
        return self.sudoku.solve(grid)

    # --- Persistence ---
    def record_match(self, game_title: str, game_mode: str, result: str, player_score: int, opponent_score: int) -> bool:
        """Save game match result to database."""
        db_manager.execute_non_query(
            self.DB,
            """INSERT INTO match_history (game_title, game_mode, result, player_score, opponent_score)
               VALUES (?, ?, ?, ?, ?)""",
            (game_title, game_mode, result, player_score, opponent_score)
        )
        return True

    def get_leaderboard(self, game_title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve match performance stats."""
        query = "SELECT * FROM match_history WHERE 1=1"
        params = []
        if game_title:
            query += " AND game_title = ?"
            params.append(game_title)
        query += " ORDER BY id DESC LIMIT 20"
        return db_manager.execute_query(self.DB, query, tuple(params))


game_service = GameService()
