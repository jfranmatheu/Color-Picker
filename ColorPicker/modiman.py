

class Modiman():
    def __init__(self, op, ctx, tuoy) -> object:
        from . dibuman import Dibuman as Draw
        self.ctx_area = ctx.area
        self.ctx_region = ctx.region
        self.ctx_wm = ctx.window_manager
        self.tuoy = tuoy
        self.op = op
        self.draw = Draw(ctx, tuoy)

    def start(self, ctx) -> set:
        if not self.ctx_wm.modal_handler_add(self.op):
            return {'CANCELLED'}
        self.tuoy.load()
        self.draw.start(self.op, ctx)
        return {'RUNNING_MODAL'}
    
    def stop(self, context) -> None:
        self.draw.stop(context==None)
        self.tuoy.unload()

    def update_region(self) -> None: self.ctx_region.tag_redraw()
    def update_area(self) -> None: self.ctx_area.tag_redraw()

    def __call__(self, args) -> set:
        if args[1].area != self.ctx_area:
            self.stop(None)
            return {'CANCELLED'}
        self.update_region()
        return {self.tuoy.modal(*args)[0]}
