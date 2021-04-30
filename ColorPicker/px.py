from . dibu import *
from . draw.image import Draw_Image
from . draw.text import Draw_Text, Draw_Text_AlignCenter
from . utils.color import RGBA, Color, RGB

def draw_callback_px(op, ctx, tuoy):
    if ctx.area != op.ctx_area: return
    tuoy.draw()
