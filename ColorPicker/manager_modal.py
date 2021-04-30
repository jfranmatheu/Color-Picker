

class ModalManager():
    def __init__(self, op, ctx, layout) -> object:
        from . manager_draw import DrawManager as Draw
        self.ctx_area = ctx.area
        self.ctx_region = ctx.region
        self.ctx_wm = ctx.window_manager
        self.layout = layout
        self.op = op
        self.draw = Draw(ctx, layout)

    def start(self, ctx) -> set:
        if not self.ctx_wm.modal_handler_add(self.op):
            return {'CANCELLED'}
        self.layout.load()
        self.draw.start(self.op, ctx)
        return {'RUNNING_MODAL'}
    
    def stop(self, context) -> None:
        self.draw.stop(context==None)
        self.layout.unload()

    def update_region(self) -> None: self.ctx_region.tag_redraw()
    def update_area(self) -> None: self.ctx_area.tag_redraw()

    def __call__(self, args) -> set:
        if args[1].area != self.ctx_area:
            self.stop(None)
            return {'CANCELLED'}
        self.update_region()
        return {self.layout.modal(*args)[0]}
