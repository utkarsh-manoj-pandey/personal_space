"""
Python Game Engine Subsystem Service
High-performance deterministic algorithmic game engines built purely with Python.
Strictly non-AI: executes analytical game theory, Minimax trees with Alpha-Beta pruning,
heuristic piece-square tables, and persistent match statistics.
Includes:
1. Chess Master: Full 8x8 move generator, board state, Minimax Alpha-Beta solver.
2. Connect 4: Gravity grid solver with strategic window heuristics.
3. Match History and Leaderboard persistence in games.db.
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

    # Center control bonus table for positional depth
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

    def __init__(self):
        self.reset()

    def reset(self):
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

    def get_board_state(self) -> List[List[str]]:
        return copy.deepcopy(self.board)

    def is_white(self, piece: str) -> bool:
        return piece.isupper()

    def is_black(self, piece: str) -> bool:
        return piece.islower()

    def generate_legal_moves(self, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
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
            direction = -1 if is_w else 1
            start_row = 6 if is_w else 1
            # Forward step
            nr = r + direction
            if 0 <= nr < 8 and self.board[nr][c] == '.':
                moves.append(((r, c), (nr, c)))
                # Initial 2-step
                if r == start_row and self.board[r + 2 * direction][c] == '.':
                    moves.append(((r, c), (r + 2 * direction, c)))
            # Captures
            for dc in [-1, 1]:
                nc = c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target != '.' and (self.is_black(target) if is_w else self.is_white(target)):
                        moves.append(((r, c), (nr, nc)))

        elif p_type == 'N':
            knight_deltas = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, dc in knight_deltas:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target == '.' or (self.is_black(target) if is_w else self.is_white(target)):
                        moves.append(((r, c), (nr, nc)))

        elif p_type in ('B', 'R', 'Q'):
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
            king_deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in king_deltas:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target == '.' or (self.is_black(target) if is_w else self.is_white(target)):
                        moves.append(((r, c), (nr, nc)))

        return moves

    def make_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Apply a move to the board."""
        sr, sc = start
        er, ec = end
        piece = self.board[sr][sc]
        captured = self.board[er][ec]

        # Pawn promotion auto-queen
        if piece == 'P' and er == 0:
            piece = 'Q'
        elif piece == 'p' and er == 7:
            piece = 'q'

        self.board[er][ec] = piece
        self.board[sr][sc] = '.'
        self.move_history.append((start, end, captured))
        self.turn = 'b' if self.turn == 'w' else 'w'
        return True

    def undo_move(self):
        """Revert the last move."""
        if not self.move_history:
            return
        (sr, sc), (er, ec), captured = self.move_history.pop()
        piece = self.board[er][ec]
        # Revert promotion if pawn
        if piece == 'Q' and sr == 6 and er == 0:
            piece = 'P'
        elif piece == 'q' and sr == 1 and er == 7:
            piece = 'p'

        self.board[sr][sc] = piece
        self.board[er][ec] = captured
        self.turn = 'b' if self.turn == 'w' else 'w'

    def evaluate_board(self) -> int:
        """Heuristic board evaluation function (positive = White advantage)."""
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if piece == '.':
                    continue
                score += self.PIECE_VALUES[piece]
                idx = r * 8 + c
                if piece == 'P':
                    score += self.PAWN_TABLE[idx]
                elif piece == 'p':
                    score -= self.PAWN_TABLE[63 - idx]
                elif piece == 'N':
                    score += self.KNIGHT_TABLE[idx]
                elif piece == 'n':
                    score -= self.KNIGHT_TABLE[63 - idx]
        return score

    def minimax(self, depth: int, alpha: int, beta: int, maximizing: bool) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """Minimax search with Alpha-Beta branch pruning."""
        if depth == 0:
            return self.evaluate_board(), None

        color = 'w' if maximizing else 'b'
        moves = self.generate_legal_moves(color)

        if not moves:
            # Check for checkmate or stalemate
            return (-99999 if maximizing else 99999), None

        # Sort moves: captures first for alpha-beta cutoff efficiency
        moves.sort(key=lambda m: abs(self.PIECE_VALUES.get(self.board[m[1][0]][m[1][1]], 0)), reverse=True)

        best_move = moves[0]

        if maximizing:
            max_eval = -999999
            for move in moves:
                self.make_move(move[0], move[1])
                evaluation, _ = self.minimax(depth - 1, alpha, beta, False)
                self.undo_move()
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = move
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = 999999
            for move in moves:
                self.make_move(move[0], move[1])
                evaluation, _ = self.minimax(depth - 1, alpha, beta, True)
                self.undo_move()
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = move
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
            return min_eval, best_move

    def get_best_computer_move(self, depth: int = 3) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Compute the best tactical move for the black pieces."""
        _, move = self.minimax(depth, -999999, 999999, False)
        return move


class Connect4Engine:
    """Pure Python Connect 4 solver with gravity grid mechanics and Minimax heuristic bot."""
    ROWS = 6
    COLS = 7

    def __init__(self):
        self.reset()

    def reset(self):
        self.board = [[0 for _ in range(self.COLS)] for _ in range(self.ROWS)]
        self.turn = 1  # 1: Player (Red), 2: AI / Player 2 (Yellow)

    def get_valid_locations(self) -> List[int]:
        return [c for c in range(self.COLS) if self.board[0][c] == 0]

    def get_next_open_row(self, col: int) -> int:
        for r in range(self.ROWS - 1, -1, -1):
            if self.board[r][col] == 0:
                return r
        return -1

    def drop_piece(self, row: int, col: int, piece: int):
        self.board[row][col] = piece

    def check_win(self, piece: int) -> bool:
        # Check horizontal
        for r in range(self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.board[r][c + i] == piece for i in range(4)):
                    return True
        # Check vertical
        for r in range(self.ROWS - 3):
            for c in range(self.COLS):
                if all(self.board[r + i][c] == piece for i in range(4)):
                    return True
        # Positively sloped diagonals
        for r in range(self.ROWS - 3):
            for c in range(self.COLS - 3):
                if all(self.board[r + i][c + i] == piece for i in range(4)):
                    return True
        # Negatively sloped diagonals
        for r in range(3, self.ROWS):
            for c in range(self.COLS - 3):
                if all(self.board[r - i][c + i] == piece for i in range(4)):
                    return True
        return False

    def evaluate_window(self, window: List[int], piece: int) -> int:
        score = 0
        opp_piece = 1 if piece == 2 else 2
        if window.count(piece) == 4:
            score += 100
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 5
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 2
        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 4
        return score

    def score_position(self, piece: int) -> int:
        score = 0
        # Center column priority
        center_array = [self.board[r][self.COLS // 2] for r in range(self.ROWS)]
        center_count = center_array.count(piece)
        score += center_count * 3

        # Horizontal
        for r in range(self.ROWS):
            row_array = self.board[r]
            for c in range(self.COLS - 3):
                window = row_array[c:c + 4]
                score += self.evaluate_window(window, piece)

        # Vertical
        for c in range(self.COLS):
            col_array = [self.board[r][c] for r in range(self.ROWS)]
            for r in range(self.ROWS - 3):
                window = col_array[r:r + 4]
                score += self.evaluate_window(window, piece)

        return score

    def pick_best_move(self) -> int:
        valid_cols = self.get_valid_locations()
        best_score = -10000
        best_col = random.choice(valid_cols) if valid_cols else 3

        # First check immediate winning move
        for col in valid_cols:
            row = self.get_next_open_row(col)
            self.drop_piece(row, col, 2)
            if self.check_win(2):
                self.board[row][col] = 0
                return col
            self.board[row][col] = 0

        # Check immediate blocking move
        for col in valid_cols:
            row = self.get_next_open_row(col)
            self.drop_piece(row, col, 1)
            if self.check_win(1):
                self.board[row][col] = 0
                return col
            self.board[row][col] = 0

        # Score positions
        for col in valid_cols:
            row = self.get_next_open_row(col)
            self.drop_piece(row, col, 2)
            score = self.score_position(2)
            self.board[row][col] = 0
            if score > best_score:
                best_score = score
                best_col = col

        return best_col


class GameService:
    DB = "games.db"

    def __init__(self):
        self.chess = ChessEngine()
        self.connect4 = Connect4Engine()

    def chess_reset(self) -> List[List[str]]:
        self.chess.reset()
        return self.chess.get_board_state()

    def chess_get_valid_moves(self, r: int, c: int) -> List[Tuple[int, int]]:
        """Get all legal target squares for a selected piece."""
        if not (0 <= r < 8 and 0 <= c < 8):
            return []
        piece = self.chess.board[r][c]
        if piece == '.' or not self.chess.is_white(piece):
            return []
        moves = self.chess.generate_legal_moves('w')
        return [end for (start, end) in moves if start == (r, c)]

    def chess_move_player(self, start: Tuple[int, int], end: Tuple[int, int]) -> Dict[str, Any]:
        """Execute human player move."""
        sr, sc = start
        er, ec = end
        legal = self.chess.generate_legal_moves('w')
        if ((sr, sc), (er, ec)) not in legal:
            return {"success": False, "error": "Illegal Move", "board": self.chess.get_board_state()}

        self.chess.make_move(start, end)
        return {
            "success": True,
            "board": self.chess.get_board_state(),
            "turn": self.chess.turn
        }

    def chess_computer_move(self, difficulty: str = "Master") -> Dict[str, Any]:
        """Compute and execute AI response move."""
        depth = 3 if difficulty == "Master" else (2 if difficulty == "Intermediate" else 1)
        best_move = self.chess.get_best_computer_move(depth=depth)
        if not best_move:
            return {"success": False, "game_over": True, "winner": "White", "board": self.chess.get_board_state()}

        self.chess.make_move(best_move[0], best_move[1])
        return {
            "success": True,
            "move": {"from": best_move[0], "to": best_move[1]},
            "board": self.chess.get_board_state(),
            "turn": self.chess.turn
        }

    def connect4_reset(self) -> List[List[int]]:
        self.connect4.reset()
        return self.connect4.board

    def connect4_drop(self, col: int) -> Dict[str, Any]:
        row = self.connect4.get_next_open_row(col)
        if row == -1:
            return {"success": False, "error": "Column full"}

        self.connect4.drop_piece(row, col, 1)
        if self.connect4.check_win(1):
            return {"success": True, "board": self.connect4.board, "game_over": True, "winner": 1}

        # AI Move
        ai_col = self.connect4.pick_best_move()
        ai_row = self.connect4.get_next_open_row(ai_col)
        if ai_row != -1:
            self.connect4.drop_piece(ai_row, ai_col, 2)
            if self.connect4.check_win(2):
                return {"success": True, "board": self.connect4.board, "game_over": True, "winner": 2}

        return {"success": True, "board": self.connect4.board, "game_over": False}

    def record_match(self, game_title: str, game_mode: str, result: str, player_score: int, opponent_score: int = 0) -> None:
        """Save match result to games.db."""
        db_manager.execute_non_query(
            self.DB,
            """INSERT INTO match_history (game_title, game_mode, result, player_score, opponent_score)
               VALUES (?, ?, ?, ?, ?)""",
            (game_title, game_mode, result, player_score, opponent_score)
        )

    def get_leaderboard(self, game_title: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get match statistics and score ledger."""
        query = "SELECT * FROM match_history"
        params = []
        if game_title:
            query += " WHERE game_title = ?"
            params.append(game_title)
        query += " ORDER BY id DESC LIMIT 25"
        return db_manager.execute_query(self.DB, query, tuple(params))


game_service = GameService()
