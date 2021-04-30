from mathutils import Vector
from . utils.fun import point_inside_rect as mouse_on_hov
from . data import Modal
from . import TUOYA_DEBUG
from . tsform import TsformAdvanced, TsformAdvancedAnch, Anchor


class Basetuoya:
    def __init__(self) -> object:
        if TUOYA_DEBUG:
            print("Basetuoya::__init__ ->", self)
        self.inner_size = self.size = Vector((0, 0))
        self.inner_pos = self.pos = Vector((0, 0))
        self.draw_callback = None
        self.on_click_callback = None
        self.args = None
        self.children = []
        self.margin = None
        self.padding = None
        self.child_on_hov = None
        self.return_modal = Modal.RUN
        self.is_on_hov = False
        self.on_load_callback = None
        self.on_unload_callback = None

    def set_return_modal(self, modal_return: Modal):
        self.return_modal = modal_return

    def set_draw_callback(self, callback: callable) -> None:
        self.draw_callback = callback

    def set_action_callback(self, function: callable, *args) -> None:
        self.on_click_callback = function
        if args: self.args = args

    def set_on_load_unload_callbacks(self, on_load: callable, on_unload: callable) -> None:
        self.on_load_callback = on_load
        self.on_unload_callback = on_unload

    def add_child(self, child: object) -> None:
        if not child or not isinstance(child, Subtuoya):
            return
        self.children.append(child)
        if TUOYA_DEBUG:
            print("Basetuoya::add_child ->", child)

    def on_hov(self, mouse: Vector) -> bool:
        if mouse_on_hov(mouse, *self.get_pos_size()):
            if not self.is_on_hov:
                self.on_hov_enter()
                self.is_on_hov = True
        elif self.is_on_hov:
            self.on_hov_exit()
            self.is_on_hov = False
        return self.is_on_hov

    def on_hov_enter(self) -> None:
        #print("on_hov_ENTER::", self)
        pass

    def on_hov_exit(self) -> None:
        #print("on_hov_EXIT::", self)
        for child in self.children:
            child.on_hov_exit()

    def on_hov_ch(self, mouse: Vector) -> object:
        for child in self.children:
            if child.on_hov(mouse):
                return child
        return None

    def on_click(self):
        if TUOYA_DEBUG:
            print("ON CLICK::", self)
        if self.on_click_callback:
            if self.args:
                self.on_click_callback(*self.args)
            else:
                self.on_click_callback()

    def on_load(self):
        if self.on_load_callback:
            self.on_load_callback(self)
        for child in self.children:
            child.on_load()

    def on_unload(self):
        if self.on_unload_callback:
            self.on_unload_callback(self)
        for child in self.children:
            child.on_unload()

    def load(self): self.on_load()
    def unload(self): self.on_unload()

    def modal(self, region, event_type: str, event_value: str, mouse: Vector) -> str:
        if self.on_hov(mouse):
            if TUOYA_DEBUG:
                print("ON HOVER::", self)
            sub = self.on_hov_ch(mouse)
            if sub:
                return sub.modal(region, event_type, event_value, mouse)
            elif event_type == 'LEFTMOUSE' and event_value == 'PRESS':
                self.on_click()
                return Modal.RUN.value
        return self.return_modal.value

    def draw(self) -> None:
        if self.draw_callback:
            self.draw_callback(self)
        for child in self.children:
            child.draw()

class Tuoya(Basetuoya, TsformAdvanced):
    def __init__(self) -> object:
        if TUOYA_DEBUG:
            print("Tuoya::__init__ ->", self)
        super(Tuoya, self).__init__()
        self.sublado = None

    def inject_sub(self, modal: callable):
        self.sublado = modal

    @staticmethod
    def get_mouse_pos(event):
        return Vector((event.mouse_region_x, event.mouse_region_y))

    def modal(self, op, context, event) -> str:
        if self.sublado:
            if not self.sublado(context.region, event, Tuoya.get_mouse_pos(event)):
                self.sublado = None
            return self.return_modal.value
        return super().modal(context.region, event.type, event.value, Tuoya.get_mouse_pos(event))
    
    def draw(self, draw, op, ctx) -> None:
        if draw.ctx_area != ctx.area: return
        super().draw()

class Subtuoya(Basetuoya, TsformAdvancedAnch):
    def __init__(self, parent, anchor: Anchor) -> object: # : Tuoya
        if TUOYA_DEBUG:
            print("Subtuoya::__init__ ->", self)
        #super().__init__()
        super(Subtuoya, self).__init__()
        if parent and isinstance(parent, Basetuoya):
            parent.add_child(self)
            if TUOYA_DEBUG:
                print("\t- Added as child to parent ->", parent)
        self.parent = parent
        self.anchor = anchor
        self.tegs = []
        # self.pivot = pivot
        self.initUI()

    def get_master(self) -> Basetuoya:
        def get_parent(self):
            return self.parent
        tuoy = get_parent(self)
        while hasattr(tuoy, 'parent'):
            tuoy = get_parent(tuoy)
        return tuoy

    def add_teg(self, teg: object) -> None:
        from . tedgi import Tegdi
        if not teg or not isinstance(teg, Tegdi):
            print("Subtuoya::add_teg -> No Tegdi Instance")
            return
        self.tegs.append(teg)
        if TUOYA_DEBUG:
            print("Basetuoya::add_teg ->", teg)
    
    def rem_teg(self, teg) -> None:
        from . tedgi import Tegdi
        if not teg or not isinstance(teg, Tegdi):
            print("Subtuoya::rem_teg -> No Tegdi Instance")
            return
        self.tegs.remove(teg)
    
    def revert_tegs_order(self) -> None:
        self.tegs = self.tegs.reverse()

    def inject_teg_submodal(self, teg) -> None:
        self.get_master().inject_sub(teg.sublado)

    def on_hov_exit(self) -> None:
        super().on_hov_exit()
        for teg in self.tegs:
            teg.on_hov_exit()

    def on_hov_ch(self, mouse: Vector) -> object:
        # NOTE: changed order, first check for teg, then children.
        for teg in self.tegs:
            if teg.on_hov(mouse):
                return teg
        child = super().on_hov_ch(mouse)
        if child: return child
        return None
    
    def draw(self) -> None:
        if self.draw_callback:
            self.draw_callback(self)
        for teg in reversed(self.tegs):
            teg.draw()
        for child in self.children:
            child.draw()
