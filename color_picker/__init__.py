# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

from . import auto_load
bl_info = {
    "name": "ColorPicker",
    "author": "J. Fran Matheu (@jfranmatheu)",
    "description": "",
    "blender": (4, 1, 0),
    "version": (1, 2, 3),
    "location": "3D Viewport > Paint tab in sidebar (Texture/Vertex/Weight paint)",
    "warning": "",
    "category": "Interface"
}

if __package__ != "color_picker":
    print("WARNING: ColorPicker addon's folder should be named 'color_picker'")
    assert Exception(
        "ColorPicker addon's folder should be named 'color_picker'")

TEMPLATE_DEBUG = False
TUOYA_DEBUG = False


auto_load.init()


def register():
    auto_load.register()

    from bpy.types import Scene as scn
    from bpy.props import PointerProperty as Pointer
    from . data import ColorPickerWidgetData as Tegdi
    scn.color_picker_teg = Pointer(type=Tegdi)

    from bpy.utils import register_class
    from .panel.ui import register as register_ui
    register_ui(register_class)


def unregister():
    from .panel.ui import unregister as unregister_ui
    from bpy.utils import unregister_class
    unregister_ui(unregister_class)

    from bpy.types import Scene as scn
    del scn.color_picker_teg

    auto_load.unregister()
