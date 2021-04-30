from mathutils import Vector
from . utils.fun import point_inside_rect as mouse_on_hover
from . data import Modal
from . import LAYOUT_DEBUG
from . transform import TransformAdvanced, TransformAdvancedAnchored, Anchor


class BaseLayout:
    def __init__(self) -> object:
        if LAYOUT_DEBUG:
            print("BaseLayout::__init__ ->", self)
        self.inner_size = self.size = Vector((0, 0))
        self.inner_pos = self.pos = Vector((0, 0))
        self.draw_callback = None
        self.on_click_callback = None
        self.args = None
        self.children = []
        self.margin = None
        self.padding = None
        self.child_on_hover = None
        self.return_modal = Modal.RUN
        self.is_on_hover = False
        self.on_load_callback = None
        self.on_unload_callback = None

    def set_return_modal(self, modal_return: Modal):
        self.return_modal = modal_return

    def set_draw_callback(self, callback: callable) -> None:
        self.draw_callback = callback

    def set_on_click_callback(self, function: callable, *args) -> None:
        self.on_click_callback = function
        if args: self.args = args

    def set_on_load_unload_callbacks(self, on_load: callable, on_unload: callable) -> None:
        self.on_load_callback = on_load
        self.on_unload_callback = on_unload

    def add_child(self, child: object) -> None:
        if not child or not isinstance(child, SubLayout):
            return
        self.children.append(child)
        if LAYOUT_DEBUG:
            print("BaseLayout::add_child ->", child)

    def on_hover(self, mouse: Vector) -> bool:
        if mouse_on_hover(mouse, *self.get_pos_size()):
            if not self.is_on_hover:
                self.on_hover_enter()
                self.is_on_hover = True
        elif self.is_on_hover:
            self.on_hover_exit()
            self.is_on_hover = False
        return self.is_on_hover

    def on_hover_enter(self) -> None:
        #print("ON_HOVER_ENTER::", self)
        pass

    def on_hover_exit(self) -> None:
        #print("ON_HOVER_EXIT::", self)
        for child in self.children:
            child.on_hover_exit()

    def on_hover_children(self, mouse: Vector) -> object:
        for child in self.children:
            if child.on_hover(mouse):
                return child
        return None

    def on_click(self):
        if LAYOUT_DEBUG:
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
        if self.on_hover(mouse):
            if LAYOUT_DEBUG:
                print("ON HOVER::", self)
            sub = self.on_hover_children(mouse)
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

class Layout(BaseLayout, TransformAdvanced):
    def __init__(self) -> object:
        if LAYOUT_DEBUG:
            print("Layout::__init__ ->", self)
        super(Layout, self).__init__()
        self.submodal = None

    def inject_submodal(self, modal: callable):
        self.submodal = modal

    @staticmethod
    def get_mouse_pos(event):
        return Vector((event.mouse_region_x, event.mouse_region_y))

    def modal(self, op, context, event) -> str:
        if self.submodal:
            if not self.submodal(context.region, event, Layout.get_mouse_pos(event)):
                self.submodal = None
            return self.return_modal.value
        return super().modal(context.region, event.type, event.value, Layout.get_mouse_pos(event))
    
    def draw(self, draw, op, ctx) -> None:
        if draw.ctx_area != ctx.area: return
        super().draw()

class SubLayout(BaseLayout, TransformAdvancedAnchored):
    def __init__(self, parent, anchor: Anchor) -> object: # : Layout
        if LAYOUT_DEBUG:
            print("SubLayout::__init__ ->", self)
        #super().__init__()
        super(SubLayout, self).__init__()
        if parent and isinstance(parent, BaseLayout):
            parent.add_child(self)
            if LAYOUT_DEBUG:
                print("\t- Added as child to parent ->", parent)
        self.parent = parent
        self.anchor = anchor
        self.widgets = []
        # self.pivot = pivot
        self.initUI()

    def get_master(self) -> BaseLayout:
        def get_parent(self):
            return self.parent
        layout = get_parent(self)
        while hasattr(layout, 'parent'):
            layout = get_parent(layout)
        return layout

    def add_widget(self, widget: object) -> None:
        from . widget import Widget
        if not widget or not isinstance(widget, Widget):
            print("SubLayout::add_widget -> No Widget Instance")
            return
        self.widgets.append(widget)
        if LAYOUT_DEBUG:
            print("BaseLayout::add_widget ->", widget)
    
    def remove_widget(self, widget) -> None:
        from . widget import Widget
        if not widget or not isinstance(widget, Widget):
            print("SubLayout::remove_widget -> No Widget Instance")
            return
        self.widgets.remove(widget)
    
    def revert_widgets_order(self) -> None:
        self.widgets = self.widgets.reverse()

    def inject_widget_submodal(self, widget) -> None:
        self.get_master().inject_submodal(widget.submodal)

    def on_hover_exit(self) -> None:
        super().on_hover_exit()
        for widget in self.widgets:
            widget.on_hover_exit()

    def on_hover_children(self, mouse: Vector) -> object:
        # NOTE: changed order, first check for widget, then children.
        for widget in self.widgets:
            if widget.on_hover(mouse):
                return widget
        child = super().on_hover_children(mouse)
        if child: return child
        return None
    
    def draw(self) -> None:
        if self.draw_callback:
            self.draw_callback(self)
        for widget in reversed(self.widgets):
            widget.draw()
        for child in self.children:
            child.draw()
