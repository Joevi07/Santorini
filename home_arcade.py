import arcade.gui
import random
import arcade
from menu import MenuView

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "Home page"

TEX_RED_BUTTON_NORMAL = arcade.load_texture(":resources:gui_basic_assets/button/red_normal.png")
TEX_RED_BUTTON_HOVER = arcade.load_texture(":resources:gui_basic_assets/button/red_hover.png")
TEX_RED_BUTTON_PRESS = arcade.load_texture(":resources:gui_basic_assets/button/red_press.png")


class GameView(arcade.View):
    

    def __init__(self):
        
        super().__init__()

        # Background image
        self.background = arcade.load_texture(r"C:\Users\evija\OneDrive\Sem 5\ai lab\AI_proj\sant_front_page.jpg")

        self.manager = arcade.gui.UIManager()
        self.manager.enable()

        # Start game button
        switch_menu_button = arcade.gui.UITextureButton(
            text="Start game",
            width=150,
            texture=TEX_RED_BUTTON_NORMAL,
            texture_hovered=TEX_RED_BUTTON_HOVER,
            texture_pressed=TEX_RED_BUTTON_PRESS,
        )

        # On button click
        @switch_menu_button.event("on_click")
        def on_click_switch_button(event):
            menu_view = MenuView(self)
            self.window.show_view(menu_view)

        # Anchor for button
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="bottom",
            child=switch_menu_button,
            align_y=50,
        )

    def on_draw(self):
        
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, self.window.width, self.window.height),
        )
        self.manager.draw()

    def on_key_press(self, key, modifiers):
       
        if key == arcade.key.ESCAPE:
            self.window.close()


def main():
    
    # Create window in full screen mode
    window = arcade.Window(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, fullscreen=True)
    game = GameView()
    window.show_view(game)
    arcade.run()


if __name__ == "__main__":
    main()
