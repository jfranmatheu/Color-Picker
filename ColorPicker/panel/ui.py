from bpy.types import Panel
from .. prefs import ColorPickerPreferences


class ColorPickerWidgetPanel(Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_context = ".paint_common"
    bl_category = 'Paint'

    bl_idname = "COLORPICKER_PT_teg"
    bl_label = "Color Picker"

    @classmethod
    def poll(cls, context):
        return context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}

    def draw(self, context):
        ColorPickerPreferences.draw(self, context)


classes = (
    ColorPickerWidgetPanel,
)

def register(reg):
    for cls in classes:
        reg(cls)

def unregister(unreg):
    for cls in reversed(classes):
        unreg(cls)
