from . tedgi import Tegdi, Subtuoya, Anchor, Vector, Modal
from . cursor import Cursor, CursorIcon
from . utils.fun import lerp
from . sld import NONE, PRESSED, SLIDING


class Sld2D(Tegdi):
    def __init__(self, tuoy: Subtuoya = None, anchor: Anchor = None, draw_callback: callable = None, step: float = 0.01, use_live_update: bool = False, allow_clicking: bool = True) -> object:
        super().__init__(tuoy, anchor, draw_callback)
        # self._init_mouse = 0
        self._has_submodal = True
        #self._off_precision = 10
        #self._factor_precision = 1
        self._step = step
        self._live_update = use_live_update
        self._handle_pos = Vector((0, 0))
        self._on_change_value_x = []
        self._on_change_value_y = []
        self._on_confirm_value = []
        self._state = NONE
        self._allow_clicking = allow_clicking

    def set_gr_handle(self, draw_callback: callable):
        self._draw_handle = draw_callback

    def set_gr_fill(self, draw_callback: callable):
        self._draw_fill = draw_callback

    def set_gr_overlay(self, draw_callback: callable):
        self._draw_overlay = draw_callback

    def set_sld_x(self, data_source, attr_source: str, min_value, max_value) -> None:
        self._prev_x = self._cur_x = getattr(data_source, attr_source)
        self._data_x = data_source
        self._attr_x = attr_source
        self._min_x = min_value
        self._max_x = max_value
        self._factor_x = (self._cur_x - self._min_x) / \
            (self._max_x - self._min_x)
        self._handle_pos.x = self.pos.x + self._factor_x * self.size.x

    def set_sld_y(self, data_source, attr_source: str, min_value, max_value) -> None:
        self._prev_y = self._cur_y = getattr(data_source, attr_source)
        self._data_y = data_source
        self._attr_y = attr_source
        self._min_y = min_value
        self._max_y = max_value
        self._factor_y = (self._cur_y - self._min_y) / \
            (self._max_y - self._min_y)
        self._handle_pos.y = self.pos.y + self._factor_y * self.size.y

    def upd_vals(self) -> None:
        if self._data_x and hasattr(self._data_x, self._attr_x):
            self._prev_x = self._cur_x = getattr(self._data_x, self._attr_x)
            self._factor_x = (self._cur_x - self._min_x) / \
                (self._max_x - self._min_x)
            self._handle_pos.x = self.pos.x + self._factor_x * self.size.x
        if self._data_y and hasattr(self._data_y, self._attr_y):
            self._prev_y = self._cur_y = getattr(self._data_y, self._attr_y)
            self._factor_y = (self._cur_y - self._min_y) / \
                (self._max_y - self._min_y)
            self._handle_pos.y = self.pos.y + self._factor_y * self.size.y

    def onechanval_x(self, callback: callable) -> None:
        self._on_change_value_x.append(callback)

    def onechanval_y(self, callback: callable) -> None:
        self._on_change_value_y.append(callback)

    def onestval(self, callback: callable) -> None:
        self._on_confirm_value.append(callback)

    def upd_handle(self):
        #self._factor_x = (self._cur_x - self._min_x) / (self._max_x - self._min_x)
        #self._factor_y = (self._cur_y - self._min_y) / (self._max_y - self._min_y)
        self._handle_pos = self.dot_center_center(
        ) + Vector((self._factor_x * self.size.x, self._factor_y * self.size.y))

    def upd_origin(self, update_x, update_y) -> None:
        if update_x:
            if self._data_x and hasattr(self._data_x, self._attr_x):
                setattr(self._data_x, self._attr_x, self._cur_x)
                if self._on_change_value_x:
                    for callback in self._on_change_value_x:
                        callback()
        if update_y:
            if self._data_y and hasattr(self._data_y, self._attr_y):
                setattr(self._data_y, self._attr_y, self._cur_y)
                if self._on_change_value_y:
                    for callback in self._on_change_value_y:
                        callback()

    def on_slide(self, m: Vector) -> None:
        p, s = self.get_pos_size()
        local_mouse_x = max(m.x - p.x, 0)
        local_mouse_y = max(m.y - p.y, 0)
        self._factor_x = min(max(local_mouse_x/s.x, 0), 1)
        self._factor_y = min(max(local_mouse_y/s.y, 0), 1)
        self._cur_x = lerp(self._min_x, self._max_x, self._factor_x)
        self._cur_y = lerp(self._min_y, self._max_y, self._factor_y)
        self.upd_handle()
        if self._live_update:
            self.upd_origin(self._prev_x != self._cur_x,
                            self._prev_y != self._cur_y)
        #print(self._factor_x, self._factor_y)

    def on_confirm(self) -> None:
        # if not self._live_update:
        self.upd_origin(True, True)
        self._prev_x = self._cur_x
        self._prev_y = self._cur_y
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        if self._on_confirm_value:
            for call in self._on_confirm_value:
                call()

    def on_cancel(self) -> None:
        self._cur_x = self._prev_x
        self._cur_y = self._prev_y
        Cursor.set_icon(None, CursorIcon.DEFAULT)
        # Restore values.
        if self._live_update:
            if self._data_x and hasattr(self._data_x, self._attr_x):
                setattr(self._data_x, self._attr_x, self._prev_x)
            if self._data_y and hasattr(self._data_y, self._attr_y):
                setattr(self._data_y, self._attr_y, self._prev_y)
        pos = self.dot_center_center()
        factor_x = (self._cur_x - self._min_x) / (self._max_x - self._min_x)
        self._handle_pos.x = pos.x + factor_x * self.size.x
        factor_y = (self._cur_y - self._min_y) / (self._max_y - self._min_y)
        self._handle_pos.y = pos.y + factor_y * self.size.y

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if event_type == 'LEFTMOUSE' and event_value == 'PRESS':
            self.on_click()
            # self._init_mouse = mouse
            self._prev_x = self._cur_x
            self._prev_y = self._cur_y
        return Modal.RUN.value

    def on_click(self) -> None:
        super().on_click()
        self._prev_x = self._cur_x
        self._prev_y = self._cur_y
        Cursor.set_icon(None, CursorIcon.PAINT_CROSS)

    def sublado(self, region, event, mouse: Vector) -> bool:
        if event.type in {'ESC', 'RIGHTMOUSE'}:
            self.on_cancel()
            return False
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            # To avoid change on just click.
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
        # Vector((pos.x + self._handle_pos, pos.y + size.y / 2))
        self._draw_callback(*self.get_pos_size(),
                            self._handle_pos, (self._factor_x, self._factor_y))
