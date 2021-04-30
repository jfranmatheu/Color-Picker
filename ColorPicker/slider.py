from . widget import Widget, Vector, Modal, SubLayout
from . anchor import *
from . utils.fun import lerp, clamp, point_inside_circle
from enum import Enum
from math import ceil
from . cursor import CursorIcon, Cursor

NONE = 0
PRESSED = 1
SLIDING = 2
TYPING = 3

HORIZONTAL = 0
VERTICAL = 1

class SlideType(Enum):
    REAL = 0,
    STEP = 1,
    OFFS = 2

class Slider(Widget):
    def __init__(self, data_source, attr_source: str, min_value, max_value, step, use_live_update: bool = False, direction: int = HORIZONTAL, slide_type: SlideType = SlideType.REAL, allow_clicking: bool = True) -> object:
        super().__init__()
        self._prev_value = self._value = getattr(data_source, attr_source)
        self._data = data_source
        self._attr = attr_source
        self.min_value = min_value
        self.max_value = max_value
        self._live_update = use_live_update
        self._state = NONE
        self._init_mouse_axis = 0
        self._has_submodal = True
        self._off_precision = 10
        self._step = step
        self._slide_type = slide_type
        self._value_type = float
        self._factor_precision = 1
        # self.output = []
        self._on_change_value_callbacks = []
        self._on_confirm_value_callbacks = []
        self._direction = direction
        self._allow_clicking = allow_clicking
    
    @property
    def min_value(self):
        if self._min_value_dynamic:
            data, attr, off = self._min_value_dynamic
            return getattr(data, attr) + off
        return self._min_value
    
    @property
    def max_value(self):
        if self._max_value_dynamic:
            data, attr, off = self._max_value_dynamic
            return getattr(data, attr) + off
        return self._max_value
    
    @min_value.setter
    def min_value(self, min_value):
        if isinstance(min_value, (int, float)):
            self._min_value = min_value
            self._min_value_dynamic = None
        else:
            data, attr, off = min_value
            self._min_value = getattr(data, attr)
            self._min_value_dynamic = min_value
            
    @max_value.setter
    def max_value(self, max_value):
        if isinstance(max_value, (int, float)):
            self._max_value = max_value
            self._max_value_dynamic = None
        else:
            data, attr, off = max_value
            self._max_value = getattr(data, attr)
            self._max_value_dynamic = max_value

    def get_factor(self) -> float:
        return (self._value - self._min_value) / (self._max_value - self._min_value)

    def set_value(self, value) -> None:
        self._value = min(max(value, self.min_value), self.max_value)
        self.on_sliding()

    def set_direction(self, dir: int) -> None:
        self._direction = clamp(0, 1, dir)
        # TODO: update all the thing...
        
    def update_value(self) -> None:
        if self._data and hasattr(self._data, self._attr):
            self._prev_value = self._value = getattr(self._data, self._attr) 

    def set_value_type(self, _type: type) -> None:
        self._value_type = _type
    
    def set_on_change_value(self, callback: callable) -> None:
        self._on_change_value_callbacks.append(callback)
        
    def set_on_confirm_value(self, callback: callable) -> None:
        self._on_confirm_value_callbacks.append(callback)

    def update_origin_data(self) -> None:
        if self._data and hasattr(self._data, self._attr):
            setattr(self._data, self._attr, self._value)
            if self._on_change_value_callbacks:
                for callback in self._on_change_value_callbacks: callback()

    def match_value_type(self) -> None:
        if self._value_type == int:
            self._value = int(self._value)
        elif self._value_type == float:
            self._value = float(self._value)

    def on_sliding(self) -> None:
        self.match_value_type()
        if self._live_update and self._prev_value != self._value:
            self.update_origin_data()

    def slide_step(self, m_axis: int) -> None:
        dir = 1 if m_axis > self._init_mouse_axis else -1
        self.set_value(self._value + dir * self.step, self.min_value)

    def slide_off(self, m_axis: int) -> None:
        if abs(m_axis - self._init_mouse_axis) < self._off_precision:
            return
        self.slide_step(m_axis)

    def slide_real(self, m_axis: int) -> None:
        p, s = self.get_pos_size()
        if self._direction == HORIZONTAL:
            local_mouse_x = int(max(m_axis - p.x, 0))
            f = min(max(local_mouse_x/s.x, 0), 1)
        else:
            local_mouse_y = int(max(m_axis - p.y, 0))
            f = min(max(local_mouse_y/s.y, 0), 1)
        value = lerp(self._min_value, self._max_value, f)
        self.set_value(ceil(value-0.5) if self._value_type == int else value)

    def on_confirm(self) -> None:
        self.match_value_type()
        self._state = NONE
        #if not self._live_update:
        self.update_origin_data()
        self._prev_value = self._value
        if self._on_confirm_value_callbacks:
            for call in self._on_confirm_value_callbacks: call()

    def on_cancel(self) -> None:
        self._value = self._prev_value
        self._state = NONE
        # self._init_mouse = Vector((0, 0))
        if self._live_update:
            if self._data and hasattr(self._data, self._attr):
                setattr(self._data, self._attr, self._value)

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if self._state == PRESSED:
            if event_type == 'MOUSEMOVE':
                self._state = SLIDING
                self._init_mouse_axis = mouse.x if self._direction == HORIZONTAL else mouse.y
                self._prev_value = self._value
                self.on_click()
                return Modal.RUN.value
            elif event_type == 'LEFTMOUSE' and event_value == 'RELEASE':
                self._state = TYPING
                self.on_click()
                return Modal.RUN.value
        elif event_type == 'LEFTMOUSE' and event_value == 'PRESS':
            self._state = PRESSED
            
            self._init_mouse_axis = mouse.x if self._direction == HORIZONTAL else mouse.y
            self._prev_value = self._value
            self.on_click()

        return Modal.RUN.value

    def submodal(self, region, event, mouse: Vector) -> bool:
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.on_cancel()
            return False
        elif event.type == 'MOUSEMOVE':
            self._state = SLIDING
            if self._slide_type == SlideType.REAL:
                self.slide_real(mouse.x if self._direction == HORIZONTAL else mouse.y)
            elif self._slide_type == SlideType.STEP:
                self.slide_step(mouse.x if self._direction == HORIZONTAL else mouse.y)
            elif self._slide_type == SlideType.OFFS:
                self.slide_off(mouse.x if self._direction == HORIZONTAL else mouse.y)
            return True
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            if self._state == SLIDING:
                self.on_confirm()
            else:
                if self._allow_clicking:
                    self.slide_real(mouse.x if self._direction == HORIZONTAL else mouse.y)
                    self.on_confirm()
                self._state = NONE
            return False
        return True
    
    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), str(self._value), self.get_factor())
        
class SliderHandle(Slider):
    def __init__(self, data_source, attr_source: str, min_value, max_value, step, use_live_update: bool = False, direction: int = HORIZONTAL, slide_type: SlideType = SlideType.REAL) -> object:
        super().__init__(data_source, attr_source, min_value, max_value, step, use_live_update, direction, slide_type)
        self._handle_pos = Vector((-1, -1))
        self._handle_radius = 5
        #self.init_handle()
        self._was_on_hover = False
        
    def init_handle(self):
        if self._direction == HORIZONTAL:
            self._handle_pos.x = getattr(self._data, self._attr)
            self._handle_pos.y = self.pos.y
        else:
            self._handle_pos.x = self.pos.x
            self._handle_pos.y = getattr(self._data, self._attr)
    
    def snap_to_widget(self, widget: Widget, align: int, side: int, thickness: int) -> None:
        self.set_anchor(Anchor(0, 0, 0, 0))
        self.set_layout(widget.parent) # NOTE: was layout but changed to parent don't know why but LOL lets keep it so until it gives problems.
        pos, size = widget.get_pos_size()
        if align == BOTTOM:
            self.size = Vector((size.x, thickness))
            if side == OUTER: self.pos = Vector((pos.x, pos.y - thickness))
            else: self.pos = Vector((pos.x, pos.y))
        elif align == RIGHT:
            self.size = Vector((thickness, size.y))
            if side == OUTER: self.pos = Vector((pos.x + size.x, pos.y))
            else: self.pos = Vector((pos.x + size.x - thickness, pos.y))
        #self.set_anchor(Anchor(*self.pos, *(self.pos+self.size)))
        #self.set_layout(widget.layout)
        self.init_handle()
        if self._direction == HORIZONTAL:
            self._handle_pos.x = int(self.size.x * self.get_factor())
        else:
            self._handle_pos.y = int(self.size.y * self.get_factor())
    
    def on_hover(self, mouse: Vector) -> bool:
        if not super().on_hover(mouse):
            if self._was_on_hover:
                Cursor.set_icon(None, CursorIcon.DEFAULT)
                self._was_on_hover = False
            return False
        if self._direction == HORIZONTAL:
            p = Vector((self.pos.x + self._handle_pos.x, self.pos.y + self.size.y / 2))
        else:
            p = Vector((self.pos.x + self.size.x / 2, self.pos.y + self._handle_pos.y))
        if point_inside_circle(mouse, p, self._handle_radius):
            self._was_on_hover = True
            Cursor.set_icon(None, CursorIcon.MOVE_X if self._direction == HORIZONTAL else CursorIcon.MOVE_Y)
            return True
        elif self._was_on_hover:
            Cursor.set_icon(None, CursorIcon.DEFAULT)
            self._was_on_hover = False
        return False
    
    def on_hover_exit(self) -> None:
        super().on_hover_exit()
        if self._was_on_hover:
            Cursor.set_icon(None, CursorIcon.DEFAULT)
            self._was_on_hover = False
        
    def on_sliding(self) -> None:
        super().on_sliding()
        if self._direction == HORIZONTAL:
            self._handle_pos.x = int(self.size.x * self.get_factor())
        else:
            self._handle_pos.y = int(self.size.y * self.get_factor())

    def draw(self) -> None:
        pos, size = self.get_pos_size()
        if self._draw_callback:
            if self._direction == HORIZONTAL:
                self._draw_callback(self._data, pos, size, Vector((pos.x + self._handle_pos.x, pos.y + size.y / 2)), Vector((self._handle_pos.x, size.y)), str(self._value))
            else:
                self._draw_callback(self._data, pos, size, Vector((pos.x + size.x / 2, pos.y + self._handle_pos.y)), Vector((size.x, self._handle_pos.y)), str(self._value))

class SliderGraphic(Slider):
    def __init__(self, data_source, attr_source: str, min_value, max_value, step, use_live_update: bool = False, direction: int = HORIZONTAL, slide_type: SlideType = SlideType.REAL) -> object:
        super().__init__(data_source, attr_source, min_value, max_value, step, use_live_update, direction, slide_type)
        self._draw_handle = None
        self._draw_bg = None
        self._draw_fill = None
        self._draw_overlay = None

    def set_gr_handle(self, draw_callback: callable):
        self._draw_handle = draw_callback

    def set_gr_bg(self, draw_callback: callable):
        self._draw_bg = draw_callback

    def set_gr_fill(self, draw_callback: callable):
        self._draw_fill = draw_callback

    def set_gr_overlay(self, draw_callback: callable):
        self._draw_overlay = draw_callback

    def draw(self) -> None:
        pos, size = self.get_pos_size()
        if self._direction == HORIZONTAL:
            handle = int(size.x * self.get_factor())
        else:
            handle = int(size.y * self.get_factor())
        if self._draw_callback:
            self._draw_callback(self._data, pos, size, Vector((pos.x + handle, pos.y + size.y / 2)), Vector((handle, size.y)), str(self._value))
            return
        if self._draw_bg:
            self._draw_bg(pos, size)
        if self._draw_fill:
            if self._direction == HORIZONTAL:
                self._draw_fill(pos, Vector((handle, size.y)))
            else:
                self._draw_fill(pos, Vector((handle, size.x)))
        if self._draw_handle:
            if self._direction == HORIZONTAL:
                self._draw_handle(Vector((pos.x + handle, pos.y + size.y / 2)), size.y)
            else:
                self._draw_handle(Vector((pos.x + size.y / 2, pos.y + handle)), size.x)
        if self._draw_overlay:
            self._draw_overlay(pos, size, str(self._value), str(self.min_value), str(self.max_value))
