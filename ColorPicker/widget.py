from . layout import Vector, mouse_on_hover, Modal, SubLayout, Layout
from . anchor import Anchor
from . transform import TransformAnchoredFixed


class Widget(TransformAnchoredFixed):
    def __init__(self, layout: SubLayout = None, anchor: Anchor = None, draw_callback: callable = None) -> object:
        if layout:
            self.set_layout(layout)
        else:
            self.parent = self._layout = layout
        if anchor:
            self.set_anchor(anchor)
        else:
            self.anchor = anchor
        self._draw_callback = draw_callback
        self._on_click_callback = None
        self._args = None
        #if anchor and layout:
        #    self.update()
        self._is_on_hover = False
        self._has_submodal = False

    @property
    def layout(self):
        return self._layout

    def set_layout(self, layout: SubLayout) -> object:
        ''' As set parent but for items. '''
        if hasattr(self, '_layout') and self._layout:
            if isinstance(self._layout, (Layout, SubLayout)):
                self._layout.remove_widget(self)
        if layout:
            super().set_parent(layout)
            self._layout = self.parent
            layout.add_widget(self)
        return self

    def set_parent(self, parent) -> None:
        self.set_layout(parent)

    def set_draw_callback(self, draw_callback: callable) -> object:
        self._draw_callback = draw_callback
        return self

    def set_on_click_callback(self, on_click_callback: callable = None, *args) -> object:
        self._on_click_callback = on_click_callback
        self._args = args if args else None
        return self

    def draw(self) -> None:
        if not self._draw_callback:
            return
        self._draw_callback(self)

    def on_click(self) -> None:
        if self._has_submodal:
            self.inject_submodal()
        if not self._on_click_callback:
            return
        if self._args:
            self._on_click_callback(self._args)
        else:
            self._on_click_callback()

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if event_type == 'LEFTMOUSE' and event_value == 'PRESS': self.on_click()
        return Modal.RUN.value

    def submodal(self, region, event, mouse: Vector) -> bool:
        return False

    def on_hover(self, mouse: Vector) -> bool:
        if mouse_on_hover(mouse, *self.get_pos_size()):
            if not self._is_on_hover:
                self.on_hover_enter()
                self._is_on_hover = True
        elif self._is_on_hover:
            self.on_hover_exit()
            self._is_on_hover = False
        return self._is_on_hover
    
    def on_hover_enter(self) -> None:
        pass
    
    def on_hover_exit(self) -> None:
        pass

    def inject_submodal(self) -> None: self.layout.inject_widget_submodal(self)
