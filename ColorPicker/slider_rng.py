from . widget import Widget, SubLayout, Anchor, Vector, Modal
from . cursor import Cursor, CursorIcon
from . utils.fun import lerp, clamp, angle, point_inside_ring
from . slider import NONE, PRESSED, SLIDING
from math import radians as rad, cos, sin, pi, degrees


class SliderRing(Widget):
    def __init__(self, layout: SubLayout = None, anchor: Anchor = None, thickness: float = 20, draw_callback: callable = None, use_live_update: bool = False, allow_clicking: bool = True) -> object:
        super().__init__(layout, anchor, draw_callback)
        self._has_submodal = True
        self._live_update = use_live_update
        self._handle_pos = Vector((0, 0))
        self._on_change_value = []
        self._on_confirm_value = []
        self._state = NONE
        self._allow_clicking = allow_clicking
        self._thickness = thickness

    def set_slider_value(self, data_source, attr_source: str, min_value, max_value) -> None:
        self._prev_value = self._cur_value = 1 - getattr(data_source, attr_source)
        self._data = data_source
        self._attr = attr_source
        self._min_value = min_value
        self._max_value = max_value
        
        self.update_handle_pos()

    def update_value(self) -> None:
        self._prev_value = self._cur_value = 1 - getattr(self._data, self._attr)
        self.update_handle_pos()

    def set_on_change_value(self, callback: callable) -> None:
        self._on_change_value.append(callback)

    def set_on_confirm_value(self, callback: callable) -> None:
        self._on_confirm_value.append(callback)

    def update_handle_pos(self):
        factor_angle = (self._cur_value - self._min_value) / (self._max_value - self._min_value)
        angle = factor_angle * 360
        radians = rad(angle)
        
        radius = self.size[0] / 2 - self._thickness / 2
        off_x = cos(radians) * radius
        off_y = sin(radians) * radius
        self._handle_pos = self.dot_center_center() + Vector((off_x, off_y))

    def update_origin_data(self) -> None:
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
        
        self.update_handle_pos()
        if self._live_update:
            self.update_origin_data()
    
    def on_confirm(self) -> None:
        self.update_origin_data()
        self._prev_value = self._cur_value
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        if self._on_confirm_value:
            for call in self._on_confirm_value: call()

    def on_cancel(self) -> None:
        self._cur_value = self._prev_value
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        # Restore values.
        self.update_handle_pos()
        self.update_origin_data()

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if event_type == 'LEFTMOUSE' and event_value == 'PRESS': self.on_click()
        return Modal.RUN.value

    def on_click(self) -> None:
        super().on_click()
        self._prev_value = self._cur_value
        Cursor.set_icon(None, CursorIcon.PAINT_CROSS)

    def submodal(self, region, event, mouse: Vector) -> bool:
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
        
    def on_hover(self, mouse):
        shalf = self.size.x/2
        return point_inside_ring(mouse, self.dot_center_center(), shalf-self._thickness, shalf)


class SliderRingDot(SliderRing):
    def draw(self) -> None:
        if not self._draw_callback:
            return
        self._draw_callback(self.dot_center_center(), self.size.x/2, self._handle_pos, self._thickness)
