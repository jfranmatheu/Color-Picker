from . widget import Widget, SubLayout, Anchor, Vector, mouse_on_hover
from . tempo_memo import TempoMemo


class RecentColors(Widget, TempoMemo):
    def __init__(self, layout: SubLayout, anchor: Anchor, draw_callback: callable, rows: int, min_row_height: int, sep: int, data, attr: str, memo_size: int, can_remember: bool = False, id: str = '') -> object:
        Widget.__init__(self, layout, anchor, draw_callback)
        TempoMemo.__init__(self, data, attr, memo_size, can_remember, id)
        self._rows = rows
        self._min_row_height = min_row_height
        self._sep = sep
        self._on_hover_slot_index = -1
        self._inverted = True
        self._alignment = 'CENTER'
        self.init_color_slots()
        self._on_click_callback = []
    
    def set_on_click_callback(self, callback: callable):
        self._on_click_callback.append(callback)
        
    def init_color_slots(self):
        self._color_slots = []
        slot_size = 10
        pos, size = self.get_pos_size()

        height = size.y
        
        if self._memo_size != 0:
            slots_per_row = self._memo_size / self._rows
        if size.y <= self._min_row_height:
            slot_height = size.y
            slots_per_row = self._memo_size
            self._rows = 1
        else:
            slot_height = height / self._rows
            while slot_height < self._min_row_height:
                self._rows -= 1
                slot_height = height / self._rows
            slots_per_row = self._memo_size / self._rows
            if self._rows == 1:
                slot_height = size.y
        
        from math import floor
        # Real number of slots per row with fixed height.
        slots_per_row = floor( size.x / slot_height )
        
        if self._memo_size == 0:
            self._memo_size = slots_per_row * self._rows + 1 # NOTE.
        
        row_index = self._rows-1 # 0
        col_index = 0
        x0 = pos.x
        y0 = pos.y
        if self._alignment == 'CENTER':
            rel_x = x0 + slot_height * slots_per_row
            abs_x = x0 + size.x
            diff = abs(abs_x-rel_x)
            x0 += int(diff/2)
        for i in range(0, self._memo_size):
            x = x0 + slot_height * col_index
            y = y0 + slot_height * row_index
            if col_index == (slots_per_row-1):
                row_index -= 1
                col_index = 0
            else:
                col_index += 1
            self._color_slots.append((x, y))
        
        self._slot_size = [slot_height-self._sep]*2
        
    def get_data(self):
        return getattr(self._data, self._attr).copy()
    
    def on_hover(self, mouse) -> bool:
        if not super().on_hover(mouse): return False
        i = 0
        
        for slot in self._color_slots:
            if mouse_on_hover(mouse, slot, self._slot_size):
                if self._taken_size > i:
                    self._on_hover_slot_index = i
                    return True
                return False
            i+=1
        self._on_hover_slot_index = -1
        return True
    
    def on_click(self):
        if self._on_hover_slot_index != -1:
            if self._inverted:
                setattr(self._data, self._attr, self._data_blocks[self._taken_size-1-self._on_hover_slot_index])
            else:
                setattr(self._data, self._attr, self._data_blocks[self._on_hover_slot_index])
            for call in self._on_click_callback: call()
    
    def draw(self) -> None:
        self._draw_callback(self._color_slots, self._slot_size, self._data_blocks, self._on_hover_slot_index)
