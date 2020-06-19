from weakref import WeakSet as _WeakSet
from functools import lru_cache as _lru_cache

import pyglet
from pyglet.gl import GL_TRIANGLES

from . import util


class _SpatialHash:
    def __init__(self, cell_size=64):
        self.cell_size = cell_size
        self.buckets = {}

    @_lru_cache(maxsize=8192)
    def _hash(self, x, y):
        """Normalize vector to cell size"""
        return int(x / self.cell_size), int(y / self.cell_size)

    def insert_body(self, body):
        """Insert body into approprite bucket"""
        min_vec, max_vec = self._hash(*body.aabb[0:2]), self._hash(*body.aabb[2:4])
        for i in range(min_vec[0], max_vec[0]+1):
            for j in range(min_vec[1], max_vec[1]+1):
                self.buckets.setdefault((i, j), _WeakSet()).add(body)

    def insert_bodies(self, bodies):
        """Insert bodies into approprite bucket"""
        for body in bodies:
            min_vec, max_vec = self._hash(*body.aabb[0:2]), self._hash(*body.aabb[2:4])
            for i in range(min_vec[0], max_vec[0]+1):
                for j in range(min_vec[1], max_vec[1]+1):
                    self.buckets.setdefault((i, j), _WeakSet()).add(body)

    def remove_body(self, body):
        """Remove body from buckets"""
        min_vec, max_vec = self._hash(*body.aabb[0:2]), self._hash(*body.aabb[2:4])
        for i in range(min_vec[0], max_vec[0]+1):
            for j in range(min_vec[1], max_vec[1]+1):
                self.buckets.get((i, j)).remove(body)

    def get_hits(self, aabb):
        aleft, abottom, aright, atop = aabb
        min_vec, max_vec = self._hash(aleft, abottom), self._hash(aright, atop)

        def simple_overlap(body_aabb):
            bleft, bbottom, bright, btop = body_aabb
            # An overlap has occured if ALL of these are True, otherwise return False:
            return bleft < aright and bright > aleft and btop > abottom and bbottom < atop

        hits = set()

        for i in range(min_vec[0], max_vec[0]+1):
            for j in range(min_vec[1], max_vec[1]+1):
                # append to each intersecting cell
                hits |= {body for body in self.buckets.get((i, j), set()) if simple_overlap(body.aabb)}

        return hits


class Frame:
    def __init__(self, window, title, x, y, width, height, batch=None):
        self._window = window
        self._x = x
        self._y = y
        self._width = width
        self._height = height

        self._border = 3
        self._menusize = 25
        self._color1 = 25, 25, 25
        self._color2 = 50, 50, 50

        self._batch = batch or pyglet.graphics.Batch()
        self._bgroup = pyglet.graphics.OrderedGroup(order=0)
        self._fgroup = pyglet.graphics.OrderedGroup(order=1)

        self._title = pyglet.text.Label(title, bold=True, batch=self._batch, group=self._fgroup)
        self._title.x = x + 5
        self._title.y = y + height - self._title.content_height

        img = util.make_rect(width, height, color=(50, 50, 50, 255))
        self.sprite = pyglet.sprite.Sprite(img, x, y, batch=self._batch)

        self.in_update = False

        self._widget_buffer = 8
        self._widgets = []
        self._window.push_handlers(self)

    @property
    def position(self):
        return self._x, self._y

    def _get_widget_position(self, new_height):
        """Automatically offset the position of the new widgets being added."""
        y_offset = sum([widget.height + self._widget_buffer for widget in self._widgets]) + new_height
        return self._x + self._border + self._widget_buffer, self._height - self._menusize/2 - self._border - y_offset

    def add_widget(self, widget):
        self._window.push_handlers(widget)
        widget.batch = self._batch
        widget.group = self._fgroup
        widget.create_verts(*self._get_widget_position(widget.height))
        self._widgets.append(widget)

    def check_hit(self, x, y):
        return (self._x < x < self._x + self._width and
                self._y + self._height - self._menusize - self._border < y < self._y + self._height)

    def on_mouse_press(self, x, y, buttons, modifiers):
        if self.check_hit(x, y):
            self.in_update = True

    def on_mouse_release(self, x, y, buttons, modifiers):
        self.in_update = False

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if not self.in_update:
            return

        # Update all widget, and frame positions:
        for widget in self._widgets:
            widget.update_verts(dx, dy)

        # vertices = self.vertex_list.vertices[:]
        # vertices[0::2] = [x + dx for x in vertices[0::2]]
        # vertices[1::2] = [y + dy for y in vertices[1::2]]
        # self.vertex_list.vertices[:] = vertices

        # Update the menu title position:
        self._title.x += dx
        self._title.y += dy

        # Save the new position:
        self._x += dx
        self._y += dy

    def draw(self):
        self._batch.draw()
