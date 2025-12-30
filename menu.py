import arcade
import arcade.gui
from ai_mode2 import Santorini
from player2 import Santorini_Player

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Menu page"

TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")


class MenuView(arcade.View):
   

    def __init__(self, main_view=None):
        super().__init__()

        self.main_view = main_view
        self.background = arcade.load_texture(r"C:\Users\evija\OneDrive\Sem 5\ai lab\AI_proj\bg_sant.jpg")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Buttons
        ai_button = arcade.gui.UITextureButton(
            text="AI VS PLAYER",
            width=350,
            height=100,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
        )

        start_new_game_button = arcade.gui.UITextureButton(
            text="PLAYER VS PLAYER",
            width=350,
            height=100,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
        )

        resume_button = arcade.gui.UITextureButton(
            text="GO BACK",
            width=350,
            height=100,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
        )

        # Layout
        self.grid = arcade.gui.UIGridLayout(column_count=1, row_count=3, horizontal_spacing=40, vertical_spacing=100)
        self.grid.add(ai_button, column=0, row=0)
        self.grid.add(start_new_game_button, column=0, row=1)
        self.grid.add(resume_button, column=0, row=2)

        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(anchor_x="center_x", anchor_y="center_y", child=self.grid, align_x=-20)

        # Button events
        @ai_button.event("on_click")
        def on_click_ai_button(event):
            game_view = Santorini()
            self.window.show_view(game_view)

        @start_new_game_button.event("on_click")
        def on_click_start_new_game_button(event):
            game_view = Santorini_Player()
            self.window.show_view(game_view)

        @resume_button.event("on_click")
        def on_click_resume_button(event):
            from home_arcade import GameView  # import inside to avoid circular imports
            game_view = GameView()
            arcade.schedule_once(lambda dt: self.window.show_view(game_view), 0.01)

    def on_hide_view(self):
        
        self.manager.disable()

    def on_show_view(self):
        
        self.manager.enable()

    def on_draw(self):
        
        self.clear()
        arcade.draw_texture_rect(self.background, arcade.LBWH(0, 0, self.window.width, self.window.height))
        self.manager.draw()

    def on_key_press(self, key, modifiers):
        
        if key == arcade.key.ESCAPE:
            self.window.close()


def main():
   
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, fullscreen=True)
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()
