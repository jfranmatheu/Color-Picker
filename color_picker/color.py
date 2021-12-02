from mathutils import Color as C, Vector as V
from . tedgi import Tegdi, mouse_on_hov

class ColPrev(Tegdi):
    def __init__(self, tuoy, anchor, draw_callback, data) -> object:
        super().__init__(tuoy, anchor, draw_callback)
        self._data = data
        
    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), getattr(self._data, 'color'))

class ColPrevSwitch(ColPrev):
    def __init__(self, tuoy, anchor, draw_callback, data) -> object:
        super().__init__(tuoy, anchor, draw_callback, data)
        self._on_hov_color = None
        self._on_switch_color = []

    def set_on_switch_color(self, callback: callable) -> None:
        self._on_switch_color.append(callback)

    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), getattr(self._data, 'color'), getattr(self._data, 'secondary_color'))

    def on_hov(self, mouse) -> bool:
        if not super().on_hov(mouse): return False
        half_height = self.size.y/2
        if mouse_on_hov(mouse, self.pos, (self.size.x, half_height)):
            self._on_hov_color = 'SECONDARY'
        elif mouse_on_hov(mouse, self.pos+V((0, half_height)), (self.size.x, half_height)):
            self._on_hov_color = 'MAIN'
        return True

    def on_click(self) -> None:
        if self._on_hov_color == 'SECONDARY':
            prev_main_col = getattr(self._data, 'color').copy()
            prev_seco_col = getattr(self._data, 'secondary_color').copy()
            setattr(self._data, 'secondary_color', prev_main_col)
            setattr(self._data, 'color', prev_seco_col)
            if self._on_switch_color:
                for call in self._on_switch_color: call()


class ColPrevDiff(ColPrev):
    def __init__(self, tuoy, anchor, draw_callback, data) -> object:
        super().__init__(tuoy, anchor, draw_callback, data)
        self._new_color = getattr(self._data, 'color')
        self._color = self._new_color.copy()

    #def update_color(self) -> None:
    #    self._new_color = 
    
    def confirm_new_color(self) -> None:
        self._color = self._new_color.copy()

    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), self._color, self._new_color)

from . utils.color.conversion.rgb2hex import rgb2hex
from . utils.clip import copy2clip
class ColPrevHex(ColPrev):
    def on_hov(self, mouse) -> bool:
        #self._is_on_hov = mouse_on_hov(mouse, *self.get_pos_size())
        return mouse_on_hov(mouse, *self.get_pos_size()) #self._is_on_hov

    def on_click(self) -> None:
        copy2clip(rgb2hex(*getattr(self._data, 'color')))

    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), rgb2hex(*getattr(self._data, 'color')))

from . utils.color import complementary, analogous, split_complementary, triadic, tetradic
class ColPrevComplementary(ColPrev):
    def on_click(self) -> None:
        setattr(self._data, 'color', complementary(getattr(self._data, 'color')))
    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), complementary(getattr(self._data, 'color')))

class ColPrevAnalogous(ColPrev):
    def on_click(self) -> None:
        setattr(self._data, 'color', analogous(getattr(self._data, 'color')))
    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), analogous(getattr(self._data, 'color')))

class ColPrevSplitComplementary(ColPrev):
    def on_click(self) -> None:
        setattr(self._data, 'color', split_complementary(getattr(self._data, 'color')))
    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), split_complementary(getattr(self._data, 'color')))

class ColPrevTriadic(ColPrev):
    def on_click(self) -> None:
        setattr(self._data, 'color', triadic(getattr(self._data, 'color')))
    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), triadic(getattr(self._data, 'color')))
   
class ColPrevTetradic(ColPrev):
    def on_click(self) -> None:
        setattr(self._data, 'color', tetradic(getattr(self._data, 'color')))
    def draw(self) -> None:
        self._draw_callback(*self.get_pos_size(), tetradic(getattr(self._data, 'color')))