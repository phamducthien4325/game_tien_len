import arcade
import arcade.gui

WIDTH = 1280
HEIGHT = 720

class LoginView(arcade.View):
    def __init__(self):
        super().__init__()
        self.text = ""  # Biến lưu trữ nội dung nhập
        self.active = False  # Trạng thái ô nhập liệu

    def on_show_view(self):
        """ Called when switching to this view"""
        self.window.background_color = arcade.color.GO_GREEN
    
    def on_draw(self):
        self.clear()
        color = arcade.color.BLUE if self.active else arcade.color.GRAY
        arcade.draw_rect_outline(arcade.rect.XYWH(100, 100, 200, 200), color, 10)
        arcade.draw_text(self.text, 160, 190, arcade.color.BLACK, 20, anchor_y="top")
        arcade.draw_text("Nhấp vào ô để nhập, ENTER để xác nhận", 150, 300, arcade.color.BLACK, 14)