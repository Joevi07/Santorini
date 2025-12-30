import arcade
from enum import Enum
import math
import random

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CELL = 100
BOARD_SIZE = 5
PAWN_R = CELL // 4
AI_DEPTH = 3

COLORS = {
     "levels": [arcade.color.BEIGE, arcade.color.LIGHT_GRAY,
               arcade.color.CORAL_PINK,      # 2nd floor
        arcade.color.SALMON],
    "dome": arcade.color.DARK_BLUE,
    "red": arcade.color.RED,
    "blue": arcade.color.BLUE,
    "highlight": arcade.color.GREEN,
}

class Phase(Enum):
    PLACE = 1
    SELECT = 2
    MOVE = 3
    BUILD = 4
    GAME_OVER = 5

class Santorini(arcade.View):

    def __init__(self):
        super().__init__()
        self.window.set_fullscreen(True)

        # Use menu background
        self.background = arcade.load_texture(r"C:\Users\evija\OneDrive\Sem 5\ai lab\AI_proj\bg_sant.jpg")
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        self.screen_w = WINDOW_WIDTH
        self.screen_h = WINDOW_HEIGHT

        self.board_px = CELL * BOARD_SIZE
        self.offset_x = (self.screen_w - self.board_px) // 2
        self.offset_y = (self.screen_h - self.board_px) // 2

        # Board initialization
        self.board = [[{"h":0, "p":None} for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
        self.phase = Phase.PLACE
        self.turn = "red"
        self.placed = 0
        self.selected = None
        self.valid = []
        self.winner = None
        self.win_label = None

        # UI text
        self.ui_label = arcade.Text("", 20, self.screen_h - 40, arcade.color.BLACK, 20)
        self.ai_action_text = arcade.Text("", self.screen_w // 2, self.screen_h - 80,
                                          arcade.color.RED, 24, anchor_x="center")

        # AI highlights
        self.ai_selected_worker = None
        self.ai_move_target = None
        self.ai_build_target = None

        # Sound effects
        self.move_sound = arcade.load_sound(":resources:sounds/coin2.wav")
        self.build_sound = arcade.load_sound(":resources:sounds/upgrade2.wav")
        self.error_sound = arcade.load_sound(":resources:sounds/error1.wav")
        self.win_sound = arcade.load_sound(":resources:sounds/upgrade5.wav")

    def on_draw(self):
        self.clear()
        # Draw background
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
        )
        self.manager.draw()
        self.draw_board()
        self.draw_ui()

    def draw_board(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                cell = self.board[r][c]
                x = self.offset_x + c * CELL
                y = self.offset_y + r * CELL
                left, right = x + 2, x + CELL - 2
                bottom, top = y + 2, y + CELL - 2

                col = COLORS["levels"][min(cell["h"], 3)]
                arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, col)

                if cell["h"] >= 4:
                    arcade.draw_circle_filled(x + CELL / 2, y + CELL / 2,
                                              PAWN_R, COLORS["dome"])
                if cell["p"]:
                    arcade.draw_circle_filled(x + CELL / 2, y + CELL / 2,
                                              PAWN_R, COLORS[cell["p"]])

        # highlight valid squares
        for r, c in self.valid:
            cx = self.offset_x + c * CELL + CELL / 2
            cy = self.offset_y + r * CELL + CELL / 2
            arcade.draw_circle_outline(cx, cy, PAWN_R * 1.2,
                                       COLORS["highlight"], 3)
        
        # Highlight AI selected worker
        if self.ai_selected_worker:
            r, c = self.ai_selected_worker
            cx = self.offset_x + c * CELL + CELL / 2
            cy = self.offset_y + r * CELL + CELL / 2
            arcade.draw_circle_outline(cx, cy, PAWN_R * 1.4,
                                       arcade.color.YELLOW, 4)
        
        # Highlight AI move target
        if self.ai_move_target:
            r, c = self.ai_move_target
            cx = self.offset_x + c * CELL + CELL / 2
            cy = self.offset_y + r * CELL + CELL / 2
            arcade.draw_circle_outline(cx, cy, PAWN_R * 1.3,
                                       arcade.color.ORANGE, 4)
        
        # Highlight AI build target
        if self.ai_build_target:
            r, c = self.ai_build_target
            cx = self.offset_x + c * CELL + CELL / 2
            cy = self.offset_y + r * CELL + CELL / 2
            arcade.draw_circle_outline(cx, cy, PAWN_R * 1.2,
                                       arcade.color.PURPLE, 4)

    def draw_ui(self):
        if self.phase == Phase.PLACE and self.placed < 4:
            self.ui_label.text = f"{self.placed}/4 placed"
        elif self.phase != Phase.GAME_OVER:
            self.ui_label.text = f"{self.turn.title()}'s Turn"
        else:
            self.ui_label.text = ""

        self.ui_label.draw()
        
        # Draw AI action text
        if self.ai_action_text.text:
            self.ai_action_text.draw()

        if self.phase == Phase.GAME_OVER and self.win_label:
            self.win_label.draw()

    def check_stalemate(self):
        workers = self.get_workers(self.turn)
        for worker in workers:
            moves = self.get_moves(*worker)
            if moves:  # If any worker can move, not a stalemate
                return False
        return True  # No worker can move = stalemate

  
    def on_mouse_press(self, x, y, button, mod):
        if self.phase == Phase.GAME_OVER:
            return

        # convert mouse → board coordinates
        c = int((x - self.offset_x) // CELL)
        r = int((y - self.offset_y) // CELL)
        if not self.inside(r, c):
            return

        # If it's AI's turn ignore human clicks
        if self.turn == "blue":
            arcade.play_sound(self.error_sound)
            return

        if self.phase == Phase.PLACE:
            self.place(r, c)
           
            if self.turn == "blue" and self.phase == Phase.PLACE:
               
                arcade.schedule(self.ai_place_first, 1.0)
        elif self.phase == Phase.SELECT:
            self.select(r, c)
        elif self.phase == Phase.MOVE:
            self.move(r, c)
        elif self.phase == Phase.BUILD:
            self.build(r, c)
            # after player build, switch to AI if it's AI's turn
            if self.turn == "blue":
                arcade.schedule(self.ai_move_delayed, 1.0)

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.ESCAPE, arcade.key.Q):
           
            from menu import MenuView 
            menu = MenuView(None)  
            self.window.show_view(menu)
            arcade.schedule_once(lambda dt: self.window.show_view(menu), 0.01)

    
    def place(self, r, c):
        cell = self.board[r][c]
        if cell["p"] or cell["h"] >= 4:
            arcade.play_sound(self.error_sound)
            return
        cell["p"] = self.turn
        self.placed += 1
        arcade.play_sound(self.move_sound)

        # Red places 2 first, then AI places 2
        if self.placed == 2:
            self.turn = "blue"  # Switch to AI after red places 2
        elif self.placed == 4:
            # after all 4 placed, start game; red starts
            self.phase = Phase.SELECT
            self.turn = "red"
            # Check for stalemate right at game start
            if self.check_stalemate():
                self.end_game_stalemate()

    def select(self, r, c):
        if self.board[r][c]["p"] != self.turn:
            arcade.play_sound(self.error_sound)
            return
        self.selected = (r, c)
        self.valid = self.get_moves(r, c)
        if not self.valid:
            arcade.play_sound(self.error_sound)
            self.selected = None
            return
        self.phase = Phase.MOVE

    def move(self, r, c):
        if (r, c) not in self.valid:
            arcade.play_sound(self.error_sound)
            return
        sr, sc = self.selected
        pawn = self.board[sr][sc]["p"]
        self.board[sr][sc]["p"] = None
        self.board[r][c]["p"] = pawn
        arcade.play_sound(self.move_sound)

        # WIN CHECK: moving onto level 3 wins
        if self.board[r][c]["h"] == 3:
            self.phase = Phase.GAME_OVER
            self.winner = self.turn
            self.win_label = arcade.Text(f"{self.winner.title()} Wins!",
                                         self.screen_w / 2, self.screen_h / 2,
                                         arcade.color.BLACK, 36,
                                         anchor_x="center")
            arcade.play_sound(self.win_sound)
            return

        self.selected = (r, c)
        self.valid = self.get_builds(r, c)
        self.phase = Phase.BUILD

    def build(self, r, c):
        if (r, c) not in self.valid:
            arcade.play_sound(self.error_sound)
            return
        self.board[r][c]["h"] = min(4, self.board[r][c]["h"] + 1)
        arcade.play_sound(self.build_sound)
        # switch turn
        self.turn = "blue" if self.turn == "red" else "red"
        self.phase = Phase.SELECT
        self.valid = []
        
        # Check for stalemate after switching turns
        if self.check_stalemate():
            self.end_game_stalemate()

    def end_game_stalemate(self):
        
        self.phase = Phase.GAME_OVER
        # The opponent of current player wins (since current player can't move)
        self.winner = "blue" if self.turn == "red" else "red"
        self.win_label = arcade.Text(f"{self.winner.title()} Wins! (Opponent cannot move)",
                                     self.screen_w / 2, self.screen_h / 2,
                                     arcade.color.BLACK, 30,
                                     anchor_x="center")
        arcade.play_sound(self.win_sound)
        self.ai_action_text.text = ""

   
    def ai_place_first(self, delta_time):
       
        arcade.unschedule(self.ai_place_first)
        if self.turn == "blue" and self.phase == Phase.PLACE and self.placed < 4:
            self.ai_place_one()
            # Schedule second placement if needed
            if self.placed < 4:
                arcade.schedule(self.ai_place_second, 1.0)
    
    def ai_place_second(self, delta_time):
       
        arcade.unschedule(self.ai_place_second)
        if self.turn == "blue" and self.phase == Phase.PLACE and self.placed < 4:
            self.ai_place_one()
    
    def ai_move_delayed(self, delta_time):
        
        arcade.unschedule(self.ai_move_delayed)
        if self.turn == "blue" and self.phase == Phase.SELECT:
            # Check for stalemate before AI moves
            if self.check_stalemate():
                self.end_game_stalemate()
                return
            self.start_ai_turn()

    def ai_place_one(self):
        # Simple placement heuristic: prefer center, then corners, then others
        priorities = [
            (2, 2),  
            (1, 1), (1, 3), (3, 1), (3, 3),  
            (0, 0), (0, 4), (4, 0), (4, 4),
        ]
        # fill in remaining cells
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if (r, c) not in priorities:
                    priorities.append((r, c))

        for r, c in priorities:
            if self.board[r][c]["p"] is None and self.board[r][c]["h"] < 4:
                self.board[r][c]["p"] = "blue"
                self.placed += 1
                arcade.play_sound(self.move_sound)
                # Check if all pieces are placed
                if self.placed == 4:
                    self.phase = Phase.SELECT
                    self.turn = "red"
                    # Check for stalemate right after all pieces placed
                    if self.check_stalemate():
                        self.end_game_stalemate()
                return

    def start_ai_turn(self):
       
        if self.phase == Phase.GAME_OVER or self.turn != "blue":
            return

        # Find best move (same logic as before)
        best = None
        best_score = -math.inf
        blue_workers = self.get_workers("blue")
        
        if not blue_workers:
            return

        for worker in blue_workers:
            moves = self.get_moves(*worker)
            for move_to in moves:
                # Simulate move
                b1 = self.copy_board()
                self.apply_move_on_board(b1, worker, move_to)
                
                # Check immediate win
                if b1[move_to[0]][move_to[1]]["h"] == 3:
                    best = (worker, move_to, None)
                    best_score = 1e6
                    break
                
                # Try builds
                builds = self.get_builds_on_board(b1, move_to)
                if not builds:
                    builds = [None]  # No build possible
                    
                for build_at in builds:
                    b2 = self.copy_board(b1)
                    if build_at:
                        self.apply_build_on_board(b2, build_at)
                    
                    score = self.minimax(b2, AI_DEPTH - 1, -math.inf, math.inf, False)
                    if score > best_score:
                        best_score = score
                        best = (worker, move_to, build_at)
            
            if best_score >= 1e6:
                break

        if best is None:
            # Fallback
            w = blue_workers[0]
            moves = self.get_moves(*w)
            if moves:
                m = moves[0]
                builds = self.get_builds(*m)
                best = (w, m, builds[0] if builds else None)

        # Store the chosen action and show first step
        if best:
            self.chosen_worker, self.chosen_move, self.chosen_build = best
            # Step 1: Show selected worker
            self.ai_selected_worker = self.chosen_worker
            self.ai_action_text.text = f"AI selects worker at {self.chosen_worker}"
            arcade.schedule(self.ai_show_move, 1.5)

    def ai_show_move(self, delta_time):
        
        arcade.unschedule(self.ai_show_move)
        # Step 2: Show move target
        self.ai_move_target = self.chosen_move
        self.ai_action_text.text = f"AI moves to {self.chosen_move}"
        arcade.schedule(self.ai_execute_move, 1.5)

    def ai_execute_move(self, delta_time):
        arcade.unschedule(self.ai_execute_move)
        
        # Actually move the piece
        self.apply_move(self.chosen_worker, self.chosen_move)
        arcade.play_sound(self.move_sound)
        
        # Clear move highlights
        self.ai_selected_worker = None
        self.ai_move_target = None
        
        # Check win condition
        if self.board[self.chosen_move[0]][self.chosen_move[1]]["h"] == 3:
            self.phase = Phase.GAME_OVER
            self.winner = "blue"
            self.win_label = arcade.Text("Blue Wins!",
                                       self.screen_w / 2, self.screen_h / 2,
                                       arcade.color.BLACK, 36,
                                       anchor_x="center")
            self.ai_action_text.text = ""
            arcade.play_sound(self.win_sound)
            return
        
        # Step 3: Show build if there is one
        if self.chosen_build:
            self.ai_build_target = self.chosen_build
            self.ai_action_text.text = f"AI builds at {self.chosen_build}"
            arcade.schedule(self.ai_execute_build, 1.5)
        else:
            # No build, end turn
            self.ai_end_turn()

    def ai_execute_build(self, delta_time):
        arcade.unschedule(self.ai_execute_build)
        
        # Actually build
        if self.chosen_build:
            self.apply_build(self.chosen_build)
            arcade.play_sound(self.build_sound)
        
        # Clear build highlight
        self.ai_build_target = None
        self.ai_end_turn()

    def ai_end_turn(self):
        self.ai_action_text.text = ""
        self.ai_selected_worker = None
        self.ai_move_target = None
        self.ai_build_target = None
        
        self.turn = "red"
        self.phase = Phase.SELECT
        self.valid = []
        
        if self.check_stalemate():
            self.end_game_stalemate()

    def apply_move(self, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos
        pawn = self.board[fr][fc]["p"]
        self.board[fr][fc]["p"] = None
        self.board[tr][tc]["p"] = pawn

    def apply_build(self, pos):
        r, c = pos
        self.board[r][c]["h"] = min(4, self.board[r][c]["h"] + 1)

    def copy_board(self, board=None):
        base = self.board if board is None else board
        return [[{"h": base[r][c]["h"], "p": base[r][c]["p"]} for c in range(BOARD_SIZE)]
                for r in range(BOARD_SIZE)]

    def apply_move_on_board(self, board_state, from_pos, to_pos):
        fr, fc = from_pos
        tr, tc = to_pos
        pawn = board_state[fr][fc]["p"]
        board_state[fr][fc]["p"] = None
        board_state[tr][tc]["p"] = pawn

    def apply_build_on_board(self, board_state, pos):
        r, c = pos
        board_state[r][c]["h"] = min(4, board_state[r][c]["h"] + 1)

    def get_moves_on_board(self, board_state, r, c):
        h = board_state[r][c]["h"]
        out = []
        for nr, nc in self.neigh(r, c):
            cell = board_state[nr][nc]
            if cell["p"] or cell["h"] >= 4:
                continue
            if cell["h"] - h <= 1:
                out.append((nr, nc))
        return out

    def get_builds_on_board(self, board_state, r_c):
        r, c = r_c
        out = []
        for nr, nc in self.neigh(r, c):
            if board_state[nr][nc]["p"]:
                continue
            if board_state[nr][nc]["h"] < 4:
                out.append((nr, nc))
        return out

    def get_workers_on_board(self, board_state, color):
        out = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if board_state[r][c]["p"] == color:
                    out.append((r, c))
        return out

    # ------- Minimax with alpha-beta -------
    def minimax(self, board_state, depth, alpha, beta, maximizing_player):
        blue_workers = self.get_workers_on_board(board_state, "blue")
        red_workers = self.get_workers_on_board(board_state, "red")
        for (r, c) in blue_workers:
            if board_state[r][c]["h"] == 3:
                return 1e6  # AI win
        for (r, c) in red_workers:
            if board_state[r][c]["h"] == 3:
                return -1e6  # player win

        if depth == 0:
            return self.evaluate_board(board_state)

        if maximizing_player:
            max_eval = -math.inf
            workers = blue_workers
            for w in workers:
                moves = self.get_moves_on_board(board_state, *w)
                for m in moves:
                    b1 = self.copy_board(board_state)
                    self.apply_move_on_board(b1, w, m)
                    if b1[m[0]][m[1]]["h"] == 3:
                        return 1e6
                    builds = self.get_builds_on_board(b1, m)
                    if not builds:
                        eval_ = self.minimax(b1, depth - 1, alpha, beta, False)
                        max_eval = max(max_eval, eval_)
                        alpha = max(alpha, eval_)
                        if beta <= alpha:
                            return max_eval
                    else:
                        for build in builds:
                            b2 = self.copy_board(b1)
                            self.apply_build_on_board(b2, build)
                            eval_ = self.minimax(b2, depth - 1, alpha, beta, False)
                            max_eval = max(max_eval, eval_)
                            alpha = max(alpha, eval_)
                            if beta <= alpha:
                                return max_eval
            return max_eval if max_eval != -math.inf else self.evaluate_board(board_state)
        else:
            min_eval = math.inf
            workers = red_workers
            for w in workers:
                moves = self.get_moves_on_board(board_state, *w)
                for m in moves:
                    b1 = self.copy_board(board_state)
                    self.apply_move_on_board(b1, w, m)
                    if b1[m[0]][m[1]]["h"] == 3:
                        return -1e6
                    builds = self.get_builds_on_board(b1, m)
                    if not builds:
                        eval_ = self.minimax(b1, depth - 1, alpha, beta, True)
                        min_eval = min(min_eval, eval_)
                        beta = min(beta, eval_)
                        if beta <= alpha:
                            return min_eval
                    else:
                        for build in builds:
                            b2 = self.copy_board(b1)
                            self.apply_build_on_board(b2, build)
                            eval_ = self.minimax(b2, depth - 1, alpha, beta, True)
                            min_eval = min(min_eval, eval_)
                            beta = min(beta, eval_)
                            if beta <= alpha:
                                return min_eval
            return min_eval if min_eval != math.inf else self.evaluate_board(board_state)

    # Heuristic evaluation: mobility + heights + blocking
    def evaluate_board(self, board_state):
        blue_workers = self.get_workers_on_board(board_state, "blue")
        red_workers = self.get_workers_on_board(board_state, "red")

        blue_mobility = 0
        for w in blue_workers:
            blue_mobility += len(self.get_moves_on_board(board_state, *w))
        red_mobility = 0
        for w in red_workers:
            red_mobility += len(self.get_moves_on_board(board_state, *w))

        blue_height = sum(board_state[r][c]["h"] for r, c in blue_workers) if blue_workers else 0
        red_height = sum(board_state[r][c]["h"] for r, c in red_workers) if red_workers else 0

        def min_dist_to_level3(color_workers):
            dmin = 100
            for r in range(BOARD_SIZE):
                for c in range(BOARD_SIZE):
                    if board_state[r][c]["h"] == 3:
                        for wr, wc in color_workers:
                            d = abs(wr - r) + abs(wc - c)
                            dmin = min(dmin, d)
            return dmin if dmin != 100 else 10

        blue_dist = min_dist_to_level3(blue_workers)
        red_dist = min_dist_to_level3(red_workers)

        score = 0
        score += (blue_mobility - red_mobility) * 2.0
        score += (blue_height - red_height) * 1.0
        score += (red_dist - blue_dist) * 0.6
        score += random.uniform(-0.01, 0.01)
        return score

    # ------- utility wrappers using the live board -------
    def get_workers(self, color):
        out = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c]["p"] == color:
                    out.append((r, c))
        return out

    def get_moves(self, r, c):
        h = self.board[r][c]["h"]
        out = []
        for nr, nc in self.neigh(r, c):
            cell = self.board[nr][nc]
            if cell["p"] or cell["h"] >= 4:
                continue
            if cell["h"] - h <= 1:
                out.append((nr, nc))
        return out

    def get_builds(self, r, c):
        return [(nr, nc) for nr, nc in self.neigh(r, c)
                if not self.board[nr][nc]["p"]
                and self.board[nr][nc]["h"] < 4]

    def on_key_press(self,key,modifiers):
        if key==arcade.key.ESCAPE:
            self.window.close()

    # ------- Helpers -------
    def inside(self, r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE

    def neigh(self, r, c):
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.inside(nr, nc):
                    yield nr, nc
