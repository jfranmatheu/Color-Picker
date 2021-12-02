from . tedgi import Tegdi, Subtuoya, Anchor, Vector, Modal
from . cursor import Cursor, CursorIcon
from . utils.fun import lerp, clamp, angle, point_inside_ring
from . sld import NONE, PRESSED, SLIDING
from math import radians as rad, cos, sin, pi, degrees


class SldRng(Tegdi):
    def __init__(self, tuoy: Subtuoya = None, anchor: Anchor = None, thickness: float = 20, draw_callback: callable = None, use_live_update: bool = False, allow_clicking: bool = True) -> object:
        super().__init__(tuoy, anchor, draw_callback)
        self._has_submodal = True
        self._live_update = use_live_update
        self._handle_pos = Vector((0, 0))
        self._on_change_value = []
        self._on_confirm_value = []
        self._state = NONE
        self._allow_clicking = allow_clicking
        self._thickness = thickness

    def set_sld_val(self, data_source, attr_source: str, min_value, max_value) -> None:
        self._prev_value = self._cur_value = 1 - getattr(data_source, attr_source)
        self._data = data_source
        self._attr = attr_source
        self._min_value = min_value
        self._max_value = max_value
        
        self.upd_handle()

    def upd_val(self) -> None:
        self._prev_value = self._cur_value = 1 - getattr(self._data, self._attr)
        self.upd_handle()

    def onchangeval(self, callback: callable) -> None:
        self._on_change_value.append(callback)

    def onsetval(self, callback: callable) -> None:
        self._on_confirm_value.append(callback)

    def upd_handle(self):
        factor_angle = (self._cur_value - self._min_value) / (self._max_value - self._min_value)
        angle = factor_angle * 360
        radians = rad(angle)
        
        radius = self.size[0] / 2 - self._thickness / 2
        off_x = cos(radians) * radius
        off_y = sin(radians) * radius
        self._handle_pos = self.dot_center_center() + Vector((off_x, off_y))

    def upd_origin(self) -> None:
        if self._data and hasattr(self._data, self._attr):
            setattr(self._data, self._attr, 1-self._cur_value)
        for callback in self._on_change_value: callback()

    def on_slide(self, m: Vector) -> None:
        c = self.dot_center_center() 
        local_mouse = Vector((m.x - c.x, m.y - c.y))
        radius = self.size.x/2

        v1 = Vector((1, 0))
        v2 = Vector((
            clamp( -1, 1, local_mouse.x / radius ),
            clamp( -1, 1, local_mouse.y / radius )
        ))
        _angle = angle(v1, v2)

        if v2.y < 0:
            diff = pi*2 - (_angle + pi)
            _angle = pi + diff
        factor_angle = clamp(0, 1, _angle / pi/2)
        self._cur_value = lerp(self._min_value, self._max_value, factor_angle)
        
        self.upd_handle()
        if self._live_update:
            self.upd_origin()
    
    def on_confirm(self) -> None:
        self.upd_origin()
        self._prev_value = self._cur_value
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        if self._on_confirm_value:
            for call in self._on_confirm_value: call()

    def on_cancel(self) -> None:
        self._cur_value = self._prev_value
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        # Restore values.
        self.upd_handle()
        self.upd_origin()

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if event_type == 'LEFTMOUSE' and event_value == 'PRESS': self.on_click()
        return Modal.RUN.value

    def on_click(self) -> None:
        super().on_click()
        self._prev_value = self._cur_value
        Cursor.set_icon(None, CursorIcon.PAINT_CROSS)

    def sublado(self, region, event, mouse: Vector) -> bool:
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.on_cancel()
            return False
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self._state == SLIDING:
                self.on_confirm()
            else:
                if self._allow_clicking:
                    self.on_slide(mouse)
                    self.on_confirm()
            self._state = NONE
            return False
        elif event.type == 'MOUSEMOVE':
            self._state = SLIDING
            self.on_slide(mouse)
        return True

    def draw(self) -> None:
        if not self._draw_callback:
            return
        self._draw_callback(*self.get_pos_size(), self._handle_pos)
        
    def on_hov(self, mouse):
        shalf = self.size.x/2
        return point_inside_ring(mouse, self.dot_center_center(), shalf-self._thickness, shalf)


class SldRngDot(SldRng):
    def draw(self) -> None:
        if not self._draw_callback:
            return
        self._draw_callback(self.dot_center_center(), self.size.x/2, self._handle_pos, self._thickness)
