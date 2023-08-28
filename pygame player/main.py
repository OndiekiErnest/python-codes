import pygame
import os
import math
from configparser import ConfigParser

pygame.font.init()

class Display():

    """Initialize window for diplay"""
    _CONFIGURE = ConfigParser()
    _CONFIGURE.read("lazylog.ini")

    #---------------------------Nested Button class-------------------------------------
    class Button:

        """clickable pygame button"""

        def __init__(self, color, x, y, text="", radius=0):
            self._color = color
            self._x = x
            self._y = y
            self._text = text
            self._radius = int(radius)

        def _draw_ellipse(self, win, width, height=50, outline=None):
            """Draws the ellipse button on the screen"""

            if outline:
                pygame.draw.ellipse(win, outline, (self._x - 2, self._y - 2, self._width + 4, self._height + 4), 0)

            pygame.draw.ellipse(win, self._color, (self._x, self._y, self._width, self._height), 0)
            if self._text != "":
                font = pygame.font.SysFont("arial", 12)
                text = font.render(self._text, 1, (255, 255, 255))
                win.blit(text, (self._x + (self._width / 2 - text.get_width() / 2), self._y + (self._height / 2 - text.get_height() / 2)))

        def _draw_rect(self, win, width, height=50, outline=None):
            """Draws the rectangle button on the screen"""

            if outline:
                pygame.draw.rect(win, outline, (self._x - 2, self._y - 2, self._width + 4, self._height + 4), 0)

            pygame.draw.rect(win, self._color, (self._x, self._y, self._width, self._height), 0)
            if self._text != "":
                font = pygame.font.SysFont("arial", 12)
                text = font.render(self._text, 1, (255, 255, 255))
                win.blit(text, (self._x + (self._width / 2 - text.get_width() / 2), self._y + (self._height / 2 - text.get_height() / 2)))

        def _draw_circle(self, win, outline=None):
            """Draws the button on the screen"""

            if outline:
                pygame.draw.circle(win, outline, (self._x - 2, self._y - 2), self._radius)

            self._cir = pygame.draw.circle(win, self._color, (self._x, self._y), self._radius)
            if self._text != "":
                font = pygame.font.SysFont("arial", 12)
                text = font.render(self._text, 1, (255, 255, 255))
                win.blit(text, (self._x + (self._radius - text.get_width() / 2), self._y + (self._radius - text.get_height() / 2)))

        def _isOver(self, pos):
            """pos is the mouse position"""

            if self._radius == 0:
                if (pos[0] > self._x and pos[0] < self._x + self._width):
                    if (pos[1] > self._y and pos[1] < self._y + self._height):
                        return True

            elif self._radius > 0:
                if (pos[0] > self._cir.x and pos[0] < self._cir.x + self._radius * 2):
                    if (pos[1] > self._cir.y and pos[1] < self._cir.y + self._radius * 2):
                        return True
            return False

    #---------------------------End Nested Button class---------------------------------

    def __init__(self):
        self.W = 400
        self.H = 145
        self.theme = Display._CONFIGURE["theme"]["current"]
        self._btn_color = self._conv(Display._CONFIGURE[self.theme]["bg"])
        self._bg_image = Display._CONFIGURE[self.theme]["photo"]
        self._white = (255,255,255)
        self._black = (0,0,0)
        self._red = (150,0,0)
        os.environ["SDL_VIDEO_WINDOW_POS"] = "%d,%d" % (955, 30)
        pygame.display.init()
        ICON = pygame.image.load("cat_head.png")
        self._BG = pygame.transform.scale(pygame.image.load(self._bg_image), (self.W, self.H))
        pygame.display.set_caption("Lazy Selector".ljust(50))
        pygame.display.set_icon(ICON)
        self._WIN = pygame.display.set_mode((self.W, self.H))

        self._MENU = pygame.transform.scale(pygame.image.load("menu.png"), (20, 20))
        self._PLAY_BTN = pygame.transform.scale(pygame.image.load("play.png"), (40, 40))
        self._PAUSE_BTN = pygame.transform.scale(pygame.image.load("pause.png"), (40, 40))
        self._PREV_BTN = pygame.transform.scale(pygame.image.load("prev.png"), (32, 32))
        self._NEXT_BTN = pygame.transform.scale(pygame.image.load("next.png"), (32, 32))
        self._LIKE_BTN = pygame.transform.scale(pygame.image.load("RGB_fav.png"), (17, 17))

        self._main()

    def _conv(self, string):
            
            f, s, t = tuple(string.split())
            return (int(f),int(s),int(t))

    def _main(self):

        run = True
        self.FPS = 60
        self._clock = pygame.time.Clock()
        self._prev_btn = Display.Button(self._btn_color, 161, 119, radius=16)
        self._pause_btn = Display.Button(self._btn_color, 200, 119, radius=19)
        self._next_btn = Display.Button(self._btn_color, 239, 119, radius=16)
        self._menu_btn = Display.Button(self._btn_color, 385, 12, radius=11)
        self._like_btn = Display.Button(self._btn_color, 361, 12, radius=11)
        title_font = pygame.font.SysFont("sans", 12)
        self.title_text = title_font.render(os.path.basename("C:\\Users\\code\\Music\\Colbie Caillat - Try (Official Video).mp3"),
                             1, self._white)

        def win_update():

            self._WIN.blit(self._BG, (0, 0))

            self._prev_btn._draw_circle(self._WIN)
            self._pause_btn._draw_circle(self._WIN)
            self._next_btn._draw_circle(self._WIN)
            self._menu_btn._draw_circle(self._WIN)
            self._like_btn._draw_circle(self._WIN)
            self._WIN.blit(self._LIKE_BTN, (self.W - 48, 4))
            self._WIN.blit(self._MENU, (self.W - 25, 2))
            self._WIN.blit(self._PREV_BTN, (145, 103))
            self._WIN.blit(self._PAUSE_BTN, (180, 98))
            self._WIN.blit(self._NEXT_BTN, (223, 103))
            self._WIN.blit(self.title_text,(10,10))

            pygame.display.update()

        while run:
            win_update()

            self._clock.tick(self.FPS)

            for event in pygame.event.get():
                self._mouse_pos = pygame.mouse.get_pos()
                if event.type == pygame.QUIT:
                    run = False
                    pygame.quit()

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self._prev_btn._isOver(self._mouse_pos):
                        print("I<< Clicked")
                    elif self._pause_btn._isOver(self._mouse_pos):
                        print("PAUSE Clicked")
                    elif self._next_btn._isOver(self._mouse_pos):
                        print(">>I Clicked")

                    elif self._like_btn._isOver(self._mouse_pos):
                        self._like_btn._color = self._red
                    elif self._menu_btn._isOver(self._mouse_pos):
                        from extend_main import main_win
                        main_win()

                if event.type == pygame.MOUSEMOTION:
                    if self._prev_btn._isOver(self._mouse_pos):
                        self._prev_btn._color = (60, 60, 60)
                    else:
                        self._prev_btn._color = self._btn_color

                    if self._next_btn._isOver(self._mouse_pos):
                        self._next_btn._color = (60, 60, 60)
                    else:
                        self._next_btn._color = self._btn_color

                    if self._pause_btn._isOver(self._mouse_pos):
                        self._pause_btn._color = (60, 60, 60)
                    else:
                        self._pause_btn._color = self._btn_color

                    if self._like_btn._isOver(self._mouse_pos):
                        self._like_btn._color = (60, 60, 60)
                    else:
                        self._like_btn._color = self._btn_color

                    if self._menu_btn._isOver(self._mouse_pos):
                        self._menu_btn._color = (60, 60, 60) 
                    else:
                        self._menu_btn._color = self._btn_color


Display()
