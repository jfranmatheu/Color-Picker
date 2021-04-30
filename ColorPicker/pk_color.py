from . tedgi import Subtuoya, Anchor, Vector
from . sld_2d import Sld2D
from . utils.color import C as Color
from . cursor import Cursor, CursorIcon
from . utils.fun import clamp, rotate
from . sld_rad import SldRadDot
from . sld_rng import SldRngDot
cache = {}


class PkColorQuad(Sld2D):
    def __init__(self, _brush, tuoy: Subtuoya = None, anchor: Anchor = None, draw_callback: callable = None) -> object:
        super().__init__(tuoy, anchor, draw_callback)
        self._color = _brush.color
        self.set_pos(self.pos.x+self.size.x/2, self.pos.y+self.size.y/2)
        minimo = min(self.size.x, self.size.y)
        self.set_size(minimo, minimo)
        self.set_sld_x(self._color, 's', 0.00001)
        self.set_sld_y(self._color, 'v', 0.00001)
        self._live_update = True

    def get_pos_size(self) -> (Vector, Vector):
        return self.dot_center_center(), self.size

    def set_sld_x(self, data_source, attr_source: str, min_value: float = 0, max_value: float = 1) -> None:
        super().set_sld_x(data_source, attr_source, min_value, max_value)
        self._handle_pos.x = self.dot_center_center().x + self._factor_x * self.size.x # pow(self._factor_x, .454545)

    def set_sld_y(self, data_source, attr_source: str, min_value: float = 0, max_value: float = 1) -> None:
        super().set_sld_y(data_source, attr_source, min_value, max_value)
        self._handle_pos.y = self.dot_center_center().y + self._factor_y * self.size.y

    def upd_vals(self) -> None:
        if self._data_x and hasattr(self._data_x, self._attr_x):
            self._prev_x = self._cur_x = getattr(self._data_x, self._attr_x)
            self._factor_x = (self._cur_x - self._min_x) / (self._max_x - self._min_x)
            self._handle_pos.x = self.dot_center_center().x + self._factor_x * self.size.x
        if self._data_y and hasattr(self._data_y, self._attr_y):
            self._prev_y = self._cur_y = getattr(self._data_y, self._attr_y)
            self._factor_y = (self._cur_y - self._min_y) / (self._max_y - self._min_y)
            self._handle_pos.y = self.dot_center_center().y + self._factor_y * self.size.y

    def draw(self) -> None:
        self._draw_callback(self.pos, self.size, self._handle_pos, self._color)

MIN_X = 0
MIN_Y = 1
MAX_X = 2
MAX_Y = 3

class ToSlicePkColorQuad(PkColorQuad):
    def __init__(self, _brush, tuoy: Subtuoya = None, anchor: Anchor = None, draw_callback: callable = None) -> object:
        super().__init__(_brush, tuoy, anchor, draw_callback)
        self.slices = Anchor(0, 1, 0, 1)
        self.__slicing = False
        self._is_sliced = False
        data = cache.get('slices', None)
        if data:
            self.slices = data
            print(self.slices.min, self.slices.max)
            #self._is_sliced = self.slices.min.x != 0 or self.slices.max.x != 1 or self.slices.min.y != 0 or self.slices.max.y != 1
            #if self._is_sliced: self.ensure_handle_pos()
            #else: del cache['slices']
            self.update_slicing()
    
    def enable_slicing(self) -> None:
        self.__slicing = True

    def disable_slicing(self) -> None:
        self.__slicing = False
        self.update_slicing()

    def set_slices(self, xi, xf, yi, yf) -> None:
        self.slices = Anchor(xi, xf, yi, yf)
        self.update_slicing()

    def on_hov_enter(self) -> None:
        super().on_hov_enter()
        Cursor.set_icon(None, CursorIcon.DEFAULT)

    def update_slicing(self) -> None:
        self.set_sld_x(self._data_x, self._attr_x, max(self.slices.min.x, 0.0001), self.slices.max.x)
        self.set_sld_y(self._data_y, self._attr_y, max(self.slices.min.y, 0.0001), self.slices.max.y)
        self.upd_vals()
        self.on_slide(self._handle_pos) # Fake slide event.
        self._is_sliced = self.slices.min.x != 0 or self.slices.max.x != 1 or self.slices.min.y != 0 or self.slices.max.y != 1
    
    def ensure_handle_pos(self) -> None:
        c, s = self.get_pos_size()
        self._handle_pos.x = clamp(c.x, c.x+s.x, self._handle_pos.x)
        self._handle_pos.y = clamp(c.y, c.y+s.y, self._handle_pos.y)
    
    def upd_vals(self) -> None:
        super().upd_vals()
        if self._is_sliced: self.ensure_handle_pos(); cache['slices'] = self.slices

    def draw(self) -> None:
        self._draw_callback(self.pos, self.size, self._handle_pos, self._color, self.slices, self.__slicing)


class SlicedPkColorQuad(PkColorQuad):
    def __init__(self, _brush, tuoy: Subtuoya = None, anchor: Anchor = None, draw_callback: callable = None) -> object:
        super().__init__(_brush, tuoy, anchor, draw_callback)
        self._slices = Anchor(0, 1, 0, 1)
        self._prev_slice_factor = 0
        self._on_hov_slicer = None

    def set_sld_x(self, data_source, attr_source: str, min_value: float = 0, max_value: float = 1) -> None:
        super().set_sld_x(data_source, attr_source, min_value, max_value)
        self._handle_pos.x = self.dot_center_center().x + self._factor_x * (self.size.x-8) + 4 # pow(self._factor_x, .454545)

    def set_sld_y(self, data_source, attr_source: str, min_value: float = 0, max_value: float = 1) -> None:
        super().set_sld_y(data_source, attr_source, min_value, max_value)
        self._handle_pos.y = self.dot_center_center().y + self._factor_y * (self.size.y-8) + 4

    def upd_vals(self) -> None:
        if self._data_x and hasattr(self._data_x, self._attr_x):
            self._prev_x = self._cur_x = getattr(self._data_x, self._attr_x)
            self._factor_x = (self._cur_x - self._min_x) / (self._max_x - self._min_x)
            self._handle_pos.x = self.dot_center_center().x + self._factor_x * (self.size.x-8) + 4
        if self._data_y and hasattr(self._data_y, self._attr_y):
            self._prev_y = self._cur_y = getattr(self._data_y, self._attr_y)
            self._factor_y = (self._cur_y - self._min_y) / (self._max_y - self._min_y)
            self._handle_pos.y = self.dot_center_center().y + self._factor_y * (self.size.y-8) + 4

    def on_confirm(self) -> None:
        if not self._on_hov_slicer:
            super().on_confirm()
            return

        self._prev_slice_factor = 0
        Cursor.set_icon(None, CursorIcon.DEFAULT)

    def on_cancel(self) -> None:
        if not self._on_hov_slicer:
            super().on_cancel()
            return
        
        if self._on_hov_slicer == MIN_X: self._slices.min.x = self._prev_slice_factor
        elif self._on_hov_slicer == MIN_Y: self._slices.min.y = self._prev_slice_factor
        elif self._on_hov_slicer == MAX_X: self._slices.max.x = self._prev_slice_factor
        elif self._on_hov_slicer == MAX_Y: self._slices.max.y = self._prev_slice_factor
        
        Cursor.set_icon(None, CursorIcon.DEFAULT)

    def on_click(self) -> None:
        super().on_click()
        if self._on_hov_slicer:
            if self._on_hov_slicer in {MIN_X, MAX_X}:
                Cursor.set_icon(None, CursorIcon.MOVE_X)
                if self._on_hov_slicer == MIN_X: self._prev_slice_factor = self._slices.min.x
                else: self._prev_slice_factor = self._slices.max.x
            elif self._on_hov_slicer in {MIN_Y, MAX_Y}:
                Cursor.set_icon(None, CursorIcon.MOVE_Y)
                if self._on_hov_slicer == MIN_Y: self._prev_slice_factor = self._slices.min.y
                else: self._prev_slice_factor = self._slices.max.y

    def on_hov(self, mouse: Vector) -> bool:
        if not super().on_hov(mouse): return False
        # Si el mouse está en el rehueco de la derecha...
        if mouse.x > self.pos.x + self.size.x - 4:
            # Mirar si está cerca del slicer del MAX_Y.
            if abs(mouse.y - (self.pos.y + self.size.y * self._slices.max.y)) < 4:
                self._on_hov_slicer = MAX_Y
                Cursor.set_icon(None, CursorIcon.MOVE_Y)
            # Mirar si está cerca del slicer del MIN_Y.
            elif abs(mouse.y - (self.pos.y + self.size.y * self._slices.min.y)) < 4:
                self._on_hov_slicer = MIN_Y
                Cursor.set_icon(None, CursorIcon.MOVE_Y)
        elif mouse.y < self.pos.y + 4:
            # Mirar si está cerca del slicer del MAX_X.
            if abs(mouse.x - (self.pos.x + self.size.x * self._slices.max.x)) < 4:
                self._on_hov_slicer = MAX_X
                Cursor.set_icon(None, CursorIcon.MOVE_X)
            # Mirar si está cerca del slicer del MIN_X.
            elif abs(mouse.x - (self.pos.x + self.size.x * self._slices.min.x)) < 4:
                self._on_hov_slicer = MIN_X
                Cursor.set_icon(None, CursorIcon.MOVE_X)
        else:
            self._on_hov_slicer = None
            Cursor.set_icon(None, CursorIcon.DEFAULT)
        return True
    
    def on_slide(self, mouse: Vector) -> None:
        if not self._on_hov_slicer:
            super().on_slide(mouse)
            return
        # print("On Slide slicer")
        local_mouse = mouse - self.pos + Vector((4, 4))
        if self._on_hov_slicer == MIN_X:
            # pos_x = clamp(self.pos.x+4, self.pos.x+self.size.x-4, mouse.x)
            pos_x = clamp(0, self.size.x-4, local_mouse.x)
            self._slices.min.x = clamp(0, self._slices.max.x-.1, pos_x/(self.size.x-4))
        elif self._on_hov_slicer == MAX_X:
            pos_x = clamp(0, self.size.x-4, local_mouse.x)
            self._slices.max.x = clamp(self._slices.min.x+.1, 1, pos_x/(self.size.x-4))
        elif self._on_hov_slicer == MIN_Y:
            pos_y = clamp(0, self.size.y-4, local_mouse.y)
            self._slices.min.y = clamp(0, self._slices.max.y-.1, pos_y/(self.size.y-4))
        elif self._on_hov_slicer == MAX_Y:
            pos_y = clamp(0, self.size.y-4, local_mouse.y)
            self._slices.max.y = clamp(self._slices.min.y+.1, 1, pos_y/(self.size.y-4))

    def draw(self) -> None:
        self._draw_callback(self.pos+Vector((4, 4)), self.size-Vector((8, 8)), self._handle_pos, self._color, self._slices)

class PkColorCircle(SldRadDot):
    def __init__(self, _brush, tuoy: Subtuoya = None, anchor: Anchor = None, draw_callback: callable = None) -> object:
        super().__init__(tuoy, anchor, draw_callback)
        self._color = _brush.color
        self.set_pos(self.pos.x+self.size.x/2, self.pos.y+self.size.y/2)
        minimo = min(self.size.x, self.size.y)
        self.set_size(minimo, minimo)
        self.set_sld_ang(self._color, 'h', 0.0, 1.0)
        self.set_sld_dist(self._color, 's', 0.0, 1.0)
        self._live_update = True
        
    def dot_center_center(self):
        return self.pos

    def draw(self) -> None:
        self._draw_callback(self.dot_center_center(), self.size.x/2, self._handle_pos, self._color)

class PkColorRing(SldRngDot):
    def __init__(self, _brush, tuoy: Subtuoya = None, anchor: Anchor = None, thickness: float = 20, draw_callback: callable = None) -> object:
        super().__init__(tuoy, anchor, thickness, draw_callback)
        self._color = _brush.color
        self.set_pos(self.pos.x+self.size.x/2, self.pos.y+self.size.y/2)
        minimo = min(self.size.x, self.size.y)
        self.set_size(minimo, minimo)
        self.set_sld_val(self._color, 'h', 0.0, 1.0)
        self._live_update = True
        side = self.size.x
        self._thickness = side - side * .9125
        self.upd_handle()

    def set_inner_teg(self, teg):
        self.inner_teg = teg
        c = self.dot_center_center()
        down_over_thicknes = Vector((c.x, c.y - self.size.y + self._thickness))
        teg.pos = c + Vector((-3, 3)) # rotate(c, down_over_thicknes, -45) 
        side = (self.size.x - self._thickness * 4) * .9125
        teg.size = Vector((side, side)) + Vector((-10, -10))
        if isinstance(teg, ToSlicePkColorQuad):
            teg.upd_vals()
    
    def dot_center_center(self):
        return self.pos

    def draw(self) -> None:
        self._draw_callback(self.dot_center_center(), self.size.x/2, self._handle_pos, self._thickness, self._color)
