from . tuoya import Vector, mouse_on_hov, Modal, Subtuoya, Tuoya
from . anchor import Anchor
from . tsform import TsformAnchFixed


class Tegdi(TsformAnchFixed):
    def __init__(self, tuoy: Subtuoya = None, anchor: Anchor = None, draw_callback: callable = None) -> object:
        if tuoy:
            self.set_tuoy(tuoy)
        else:
            self.parent = self._tuoy = tuoy
        if anchor:
            self.set_anchor(anchor)
        else:
            self.anchor = anchor
        self._draw_callback = draw_callback
        self._on_click_callback = None
        self._args = None
        # if anchor and tuoy:
        #    self.update()
        self._is_on_hov = False
        self._has_submodal = False

    @property
    def tuoy(self):
        return self._tuoy

    def set_tuoy(self, tuoy: Subtuoya) -> object:
        ''' As set parent but for items. '''
        if hasattr(self, '_tuoy') and self._tuoy:
            if isinstance(self._tuoy, (Tuoya, Subtuoya)):
                self._tuoy.rem_teg(self)
        if tuoy:
            super().setpar(tuoy)
            self._tuoy = self.parent
            tuoy.add_teg(self)
        return self

    def setpar(self, parent) -> None:
        self.set_tuoy(parent)

    def stdibucalba(self, draw_callback: callable) -> object:
        self._draw_callback = draw_callback
        return self

    def set_act_back(self, on_click_callback: callable = None, *args) -> object:
        self._on_click_callback = on_click_callback
        self._args = args if args else None
        return self

    def draw(self) -> None:
        if not self._draw_callback:
            return
        self._draw_callback(self)

    def on_click(self) -> None:
        if self._has_submodal:
            self.inject_sub()
        if not self._on_click_callback:
            return
        if self._args:
            self._on_click_callback(self._args)
        else:
            self._on_click_callback()

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if event_type == 'LEFTMOUSE' and event_value == 'PRESS':
            self.on_click()
        return Modal.RUN.value

    def sublado(self, region, event, mouse: Vector) -> bool:
        return False

    def on_hov(self, mouse: Vector) -> bool:
        if mouse_on_hov(mouse, *self.get_pos_size()):
            if not self._is_on_hov:
                self.on_hov_enter()
                self._is_on_hov = True
        elif self._is_on_hov:
            self.on_hov_exit()
            self._is_on_hov = False
        return self._is_on_hov

    def on_hov_enter(self) -> None:
        pass

    def on_hov_exit(self) -> None:
        pass

    def inject_sub(self) -> None: self.tuoy.inject_teg_submodal(self)
