from colorsys import hsv_to_rgb
import pygame as pg
from pygame.font import Font


def hsv_rgb(h, s, v):
    r, g, b = hsv_to_rgb(h, s, v)
    return r * 255, g * 255, b * 255


class TextBox(object):
    def __init__(self, text: str, text_size, text_color, background_color=None, antialias=True, font='freesansbold.ttf',
                 rectangle_size=None, position=(0, 0)):
        rfont = Font(font, text_size)
        self.__font_name = font
        self.__font = rfont
        self.__text_size = text_size
        self.__text = text
        self.__text_color = text_color
        self.__bkg_color = background_color
        self.__rectangle_size = rectangle_size
        self.__antialias = antialias
        self.__text_box = rfont.render(text, antialias, text_color, None)
        self.__position = position
        if self.__rectangle_size is None:
            r = self.__text_box.get_rect()
            self.__rectangle_size = r[2], r[3]

    def update(self):
        self.__font = Font(self.__font_name, self.__text_size)
        self.__text_box = self.__font.render(self.__text, self.__antialias, self.__text_color, None)
        r = self.__text_box.get_rect()
        self.__rectangle_size = r[2], r[3]

    @property
    def text(self):
        return self.__text

    @text.setter
    def text(self, value: str):
        self.__text = value
        self.update()

    @property
    def font(self):
        return self.__font_name

    @font.setter
    def font(self, value: str):
        self.__font_name = value
        self.update()

    @property
    def text_size(self):
        return self.__text_size

    @text_size.setter
    def text_size(self, value: int):
        self.__text_size = value
        self.update()

    @property
    def rectangle_size(self):
        return self.__rectangle_size

    @rectangle_size.setter
    def rectangle_size(self, value):
        self.__rectangle_size = value[0], value[1]

    def __contains__(self, point):
        x, y = point
        px, py = self.__position
        w, h = self.rectangle_size
        if px <= x <= px + w and py <= y <= py + h:
            return True
        return False

    def __hash__(self):
        x, y = self.__position
        w, h = self.rectangle_size

        return hash(('TextBox', x, y, w, h, self.font, self.text, self.text_size, self.__text_color, self.__bkg_color,
                     self.__antialias))

    def render(self, surface):
        rect = self.__text_box.get_rect()
        if self.__rectangle_size is None:
            self.__rectangle_size = rect[2], rect[3]
        if self.__bkg_color:
            pg.draw.rect(surface, self.__bkg_color,
                         (self.__position[0], self.__position[1], self.__rectangle_size[0], self.__rectangle_size[1]))
        w, h = self.__rectangle_size
        pos = self.__position
        centralized = pos[0] + w / 2.0 - rect[2] / 2.0, pos[1] + h / 2.0 - rect[3] / 2.0
        surface.blit(self.__text_box, centralized)


class Clickable:
    def __init__(self):
        self.mouse_over = False
        self.functs = {}

    def set_click_command(self, command, button=0, *args):
        if type(button) == tuple or type(button) == list:
            for butt in button:
                self.set_click_command(command, butt, *args)
            return
        self.functs[button] = command, args

    def clicked(self, button: int):
        pass


class Button(Clickable):
    def __init__(self, text: str, text_size, text_color, background_color=None, antialias=True, font='freesansbold.ttf',
                 rectangle_size=None, position=(0, 0)):
        super().__init__()
        self.text_box = TextBox(text, text_size, text_color, background_color, antialias, font, rectangle_size,
                                position)
        self.clicked_command = None
        self.args = []

    def __contains__(self, pos):
        return (pos[0], pos[1]) in self.text_box

    def clicked(self, button: int = 0):
        unpack = self.functs.get(button)
        if unpack is not None:
            funct, args = unpack
            if len(args) == 0:
                return funct()
            else:
                return funct(*args)

    def render(self, surface):
        self.text_box.render(surface)

    def __hash__(self):
        return hash(('Button', hash(self.text_box), hash('Button')))


class Click_Handler:
    def __init__(self):
        self.mouse_first_press: list = [None] * 5
        self.mouse_stop_press: list = [None] * 5
        self.objects: set = set()
        self.mouse_over_position: tuple = None
        self.mouse_over_object: Clickable = None

    def add_object(self, *objects):
        for obj in objects:
            self.objects.add(obj)

    def update(self, event, update_objects_too=True):
        if not (event.type == pg.MOUSEMOTION or event.type == pg.MOUSEWHEEL):
            if event.type == pg.MOUSEBUTTONDOWN:
                pos = pg.mouse.get_pos()
                self.mouse_first_press[event.button - 1] = pos[0], pos[1]
            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                self.mouse_stop_press[event.button - 1] = pos[0], pos[1]
        if update_objects_too:
            self.update_objects()

    def update_objects(self):
        mouse_position = pg.mouse.get_pos()
        mouse_position = mouse_position[0], mouse_position[1]
        if self.mouse_over_object:
            self.mouse_over_object.mouse_over = False
            self.mouse_over_object = None
        for obj in self.objects:
            if mouse_position in obj:
                self.mouse_over_object = obj
        mouse_obj = self.mouse_over_object
        if mouse_obj:
            mouse_obj.mouse_over = True
            for button in range(5):
                pos_start = self.mouse_first_press[button]
                pos_end = self.mouse_stop_press[button]
                if pos_start and pos_end:
                    if (pos_start in mouse_obj) and (pos_end in mouse_obj):
                        mouse_obj.clicked(button)
                        self.mouse_first_press[button] = None
                        self.mouse_stop_press[button] = None

    def render_objects(self, surface):
        for obj in self.objects:
            obj.render(surface)
