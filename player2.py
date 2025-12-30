# player_vs_player_view.py
import arcade
from enum import Enum


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
CELL = 100
BOARD_SIZE = 5
PAWN_R = CELL // 4
AI_DEPTH = 3

class Phase(Enum):
    PLACE = 1
    SELECT = 2
    MOVE = 3
    BUILD = 4
    GAME_OVER = 5

COLORS = {
    "levels": [arcade.color.BEIGE, arcade.color.LIGHT_GRAY,
               arcade.color.CORAL_PINK,      # 2nd floor
        arcade.color.SALMON],
    "dome": arcade.color.DARK_BLUE,
    "red": arcade.color.RED,
    "blue": arcade.color.BLUE,
    "highlight": arcade.color.GREEN,
}

class Santorini_Player(arcade.View):
  
    
    def __init__(self):
        super().__init__()
        self.background = arcade.load_texture(r"C:\Users\evija\OneDrive\Sem 5\ai lab\AI_proj\bg_sant.jpg")
        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Use window dimensions instead of get_size()
        self.screen_w = self.window.width
        self.screen_h = self.window.height

        self.board_px = CELL * BOARD_SIZE
        self.offset_x = (self.screen_w - self.board_px) // 2
        self.offset_y = (self.screen_h - self.board_px) // 2

        self.board = [[{"h": 0, "p": None} for _ in range(BOARD_SIZE)]
                      for _ in range(BOARD_SIZE)]

        self.phase = Phase.PLACE
        self.turn = "red"
        self.placed = 0
        self.win_label = None
        self.selected = None
        self.valid = []
        self.winner = None

        self.ui_label = arcade.Text("", 20, self.screen_h - 40, arcade.color.BLACK, 20)

        # Sound effects
        self.move_sound = arcade.load_sound(":resources:sounds/coin2.wav")
        self.build_sound = arcade.load_sound(":resources:sounds/upgrade2.wav")
        self.error_sound = arcade.load_sound(":resources:sounds/error1.wav")
        self.win_sound = arcade.load_sound(":resources:sounds/upgrade5.wav")

    def on_draw(self):
       
        self.clear()
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

        for r, c in self.valid:
            cx = self.offset_x + c * CELL + CELL / 2
            cy = self.offset_y + r * CELL + CELL / 2
            arcade.draw_circle_outline(cx, cy, PAWN_R * 1.2,
                                       COLORS["highlight"], 3)

    def draw_ui(self):
        
        if self.phase == Phase.PLACE and self.placed < 4:
            self.ui_label.text = f"{self.placed}/4 placed"
        elif self.phase != Phase.GAME_OVER:
            self.ui_label.text = f"{self.turn.title()}'s Turn"
        else:
            self.ui_label.text = ""  

        self.ui_label.draw()

        if self.phase == Phase.GAME_OVER and self.win_label:
            self.win_label.draw()

    def check_stalemate(self):
       
        workers = self.get_workers(self.turn)
        for worker in workers:
            moves = self.get_moves(*worker)
            if moves:  # If any worker can move, not a stalemate
                return False
        return True  # No worker can move = stalemate

    def end_game_stalemate(self):
       
        self.phase = Phase.GAME_OVER
        
        self.winner = "blue" if self.turn == "red" else "red"
        self.win_label = arcade.Text(f"{self.winner.title()} Wins! (Opponent cannot move)",
                                     self.screen_w / 2, self.screen_h / 2,
                                     arcade.color.BLACK, 30,
                                     anchor_x="center")
        arcade.play_sound(self.win_sound)

    def on_mouse_press(self, x, y, button, mod):
        
        if self.phase == Phase.GAME_OVER:
            return

        c = int((x - self.offset_x) // CELL)
        r = int((y - self.offset_y) // CELL)
        if not self.inside(r, c):
            return

        if self.phase == Phase.PLACE:
            self.place(r, c)
        elif self.phase == Phase.SELECT:
            self.select(r, c)
        elif self.phase == Phase.MOVE:
            self.move(r, c)
        elif self.phase == Phase.BUILD:
            self.build(r, c)

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

        if self.placed == 2:
            self.turn = "blue"
        if self.placed == 4:
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
        self.turn = "blue" if self.turn == "red" else "red"
        self.phase = Phase.SELECT
        self.valid = []
        
      
        if self.check_stalemate():
            self.end_game_stalemate()

    def get_workers(self, color):
       
        out = []
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                if self.board[r][c]["p"] == color:
                    out.append((r, c))
        return out

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

    def on_key_press(self,key,modifiers):
        if key==arcade.key.ESCAPE:
            self.window.close()

    def get_builds(self, r, c):
        
        return [(nr, nc) for nr, nc in self.neigh(r, c)
                if not self.board[nr][nc]["p"]
                and self.board[nr][nc]["h"] < 4]
