from bpy.types import Operator
from . pk import Colpk

class VIEW3D_OT_color_picker(Operator, Colpk):
    bl_idname = "view3d.color_picker"
    bl_label = "Color Picker"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}
