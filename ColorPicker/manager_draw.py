


class DrawManager():
    def __init__(self, ctx, layout) -> object: # callback: callable,
        self.ctx_area = ctx.area
        self.ctx_region = ctx.region
        self.ctx_space = ctx.space_data
        # self.draw = callback 
        self.layout = layout

    def start(self, op, ctx) -> object:
        self._handler = self.ctx_space.draw_handler_add(self, (op, ctx), 'WINDOW', 'POST_PIXEL')
        self.ctx_area.tag_redraw()
        return self

    def stop(self, error: bool = False) -> None:
        if error:
            from bpy.types import SpaceView3D
            if hasattr(self, '_handler'):
                SpaceView3D.draw_handler_remove(self._handler, 'WINDOW')
                del self._handler
        else:
            if hasattr(self, '_handler'):
                self.ctx_space.draw_handler_remove(self._handler, 'WINDOW')
                del self._handler
            self.ctx_area.tag_redraw()

    def update_region(self) -> None: self.ctx_region.tag_redraw()
    def update_area(self) -> None: self.ctx_area.tag_redraw()

    def __call__(self, arg1, arg2) -> None:
        self.layout.draw(self, arg1, arg2)
