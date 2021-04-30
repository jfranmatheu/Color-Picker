from . widget import Widget, SubLayout, Anchor, Vector, Modal
from . cursor import Cursor, CursorIcon
from . utils.fun import lerp, distance_between, clamp, angle, point_inside_circle
from . slider import NONE, PRESSED, SLIDING
from math import radians as rad, cos, sin, pi, degrees


class SliderRadial(Widget):
    def __init__(self, layout: SubLayout = None, anchor: Anchor = None, draw_callback: callable = None, use_live_update: bool = False, allow_clicking: bool = True) -> object:
        super().__init__(layout, anchor, draw_callback)
        self._has_submodal = True
        self._live_update = use_live_update
        self._handle_pos = Vector((0, 0))
        self._on_change_value = []
        self._on_confirm_value = []
        self._state = NONE
        self._allow_clicking = allow_clicking

    def set_slider_angle(self, data_source, attr_source: str, min_value, max_value) -> None:
        self._prev_angle = self._cur_angle = 1 - getattr(data_source, attr_source)
        self._data_angle = data_source
        self._attr_angle = attr_source
        self._min_angle = min_value
        self._max_angle = max_value
        
        self.update_handle_pos()

    def set_slider_distance(self, data_source, attr_source: str, min_value, max_value) -> None:
        self._prev_dist = self._cur_dist = getattr(data_source, attr_source)
        self._data_dist = data_source
        self._attr_dist = attr_source
        self._min_dist = min_value
        self._max_dist = max_value

        self.update_handle_pos()

    def update_values(self) -> None:
        if hasattr(self, '_data_angle'):
            self._prev_angle = self._cur_angle = 1 - getattr(self._data_angle, self._attr_angle)
        if hasattr(self, '_data_dist'):
            self._prev_dist = self._cur_dist = getattr(self._data_dist, self._attr_dist)
        self.update_handle_pos()

    def set_on_change_value(self, callback: callable) -> None:
        self._on_change_value.append(callback)

    def set_on_confirm_value(self, callback: callable) -> None:
        self._on_confirm_value.append(callback)

    def update_handle_pos(self):
        if not hasattr(self, '_data_angle') or not hasattr(self, '_data_dist'):
            return

        factor_angle = (self._cur_angle - self._min_angle) / (self._max_angle - self._min_angle)
        angle = factor_angle * 360
        radians = rad(angle)

        radius = self.size.x / 2
        factor_distance = (self._cur_dist - self._min_dist) / (self._max_dist - self._min_dist)
        distance = factor_distance * radius

        off_x = cos(radians) * distance
        off_y = sin(radians) * distance
        self._handle_pos = self.dot_center_center() + Vector((off_x, off_y))

    def update_origin_data(self) -> None:
        if self._data_angle and hasattr(self._data_angle, self._attr_angle):
            setattr(self._data_angle, self._attr_angle, 1-self._cur_angle)
        if self._data_dist and hasattr(self._data_dist, self._attr_dist):
            setattr(self._data_dist, self._attr_dist, self._cur_dist)
        
        for callback in self._on_change_value: callback()

    def on_slide(self, m: Vector) -> None:
        c = self.dot_center_center() 
        local_mouse = Vector((m.x - c.x, m.y - c.y))
        radius = self.size.x/2
        
        factor_distance = clamp(0, 1, distance_between(m, c) / radius)
        if factor_distance < 0.0001 or local_mouse == Vector((0, 0)) or m == c:
            self._handle_pos = c
            if self._live_update:
                self.update_origin_data()
            return
        self._cur_dist = lerp(self._min_dist, self._max_dist, factor_distance)

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

        self._cur_angle = lerp(self._min_angle, self._max_angle, factor_angle)
        
        self.update_handle_pos()
        if self._live_update:
            self.update_origin_data()
    
    def on_confirm(self) -> None:
        self.update_origin_data()
        self._prev_angle = self._cur_angle
        self._prev_dist = self._cur_dist
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        if self._on_confirm_value:
            for call in self._on_confirm_value: call()

    def on_cancel(self) -> None:
        self._cur_angle = self._prev_angle
        self._cur_dist = self._prev_dist
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        # Restore values.
        self.update_handle_pos()
        self.update_origin_data()

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if event_type == 'LEFTMOUSE' and event_value == 'PRESS': self.on_click()
        return Modal.RUN.value

    def on_click(self) -> None:
        super().on_click()
        self._prev_angle = self._cur_angle
        self._prev_dist = self._cur_dist
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
        return point_inside_circle(mouse, self.dot_center_center(), self.size.x/2)


class SliderRadialDot(SliderRadial):
    def draw(self) -> None:
        if not self._draw_callback:
            return
        self._draw_callback(self.dot_center_center(), self.size.x/2, self._handle_pos)
    
    def set_on_change_value_x(self, callback: callable) -> None:
        self.set_on_change_value(callback)
        
    def set_on_change_value_y(self, callback: callable) -> None:
        self.set_on_change_value(callback)
