from os.path import exists, isfile, isdir, join
from enum import Enum
from glob import glob

from bpy.types import PropertyGroup, Brush, Image
from bpy.props import *
from bpy import data as D


class Modal(Enum):
    PASS = 'PASS_TRHOUGH',
    RUN = 'RUNNING_MODAL',
    FINISH = 'FINISHED',
    CANCEL = 'CANCELLED'
    def __call__(self): return self.value


copktype = (
    ('SV_RECT', "SV Square", "Square to control Saturation and Value"),
    ('SV_H_RECT', "SV+H Square&Ring",
     "Square to control Saturation and Value plus a ring to control Hue"),
    ('HS_CIRC', "HS Circle",
     "Circle to control Hue and Saturation plus a sld to control Value"),
)


class ColorPicker(PropertyGroup):
    type: EnumProperty(
        items=copktype,
        default='SV_RECT',
        name="Color Picker Type"
    )
    use_slice: BoolProperty(default=False, name="Slice Color Picker")


class ColorPickerWidgetData(PropertyGroup):
    scale: FloatProperty(name="Scale Factor", min=0.5, max=2, default=1)
    color_picker: PointerProperty(type=ColorPicker)
    close_on_hotkey_release: BoolProperty(
        default=True, name="Close on Hot-key Release")

    is_dirty: BoolProperty(default=False)
