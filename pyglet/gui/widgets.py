import pyglet

from . import util


class _Widget(pyglet.event.EventDispatcher):
    _x = 0
    _y = 0
    _width = 0
    _height = 0

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def aabb(self):
        return self._x, self._y, self._x + self._width, self._y + self._height

    def on_mouse_press(self, x, y, buttons, modifiers):
        pass

    def on_mouse_release(self, x, y, buttons, modifiers):
        pass

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        pass

    def on_mouse_scroll(self, x, y, mouse, direction):
        pass


_Widget.register_event_type('on_mouse_press')
_Widget.register_event_type('on_mouse_release')
_Widget.register_event_type('on_mouse_motion')
_Widget.register_event_type('on_mouse_scroll')
_Widget.register_event_type('on_mouse_drag')


class PushButton(_Widget):

    def __init__(self, x, y, pressed, depressed, hover=None, batch=None, group=None):
        self._pressed_img = pressed
        self._depressed_img = depressed
        self._hover_img = hover
        self._x = x
        self._y = y
        self._width = self._depressed_img.width
        self._height = self._depressed_img.height
        self._sprite = pyglet.sprite.Sprite(self._depressed_img, x, y, batch=batch, group=group)
        self._pressed = False

    def _check_hit(self, x, y):
        return self._x < x < self._x + self._width and self._y < y < self._y + self._height

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self._check_hit(x, y):
            return
        self._sprite.image = self._pressed_img
        self._pressed = True
        self.dispatch_event('on_press')

    def on_mouse_release(self, x, y, buttons, modifiers):
        if not self._pressed:
            return
        self._sprite.image = self._depressed_img
        self._pressed = False
        self.dispatch_event('on_release')

    def on_mouse_motion(self, x, y, dx, dy):
        if self._pressed:
            return
        if self._check_hit(x, y) and self._hover_img:
            self._sprite.image = self._hover_img
        else:
            self._sprite.image = self._depressed_img


PushButton.register_event_type('on_press')
PushButton.register_event_type('on_release')


class ToggleButton(PushButton):

    def on_mouse_press(self, x, y, buttons, modifiers):
        if not self._check_hit(x, y):
            return
        self._sprite.image = self._depressed_img if self._pressed else self._pressed_img
        self._pressed = not self._pressed
        self.dispatch_event('on_toggle', self._pressed)

    def on_mouse_release(self, x, y, buttons, modifiers):
        return


ToggleButton.register_event_type('on_toggle')
