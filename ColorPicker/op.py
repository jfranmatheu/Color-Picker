from bpy.types import Operator

from . utils.fun import *
from math import cos, sin, tan, pi, degrees, atan, floor
from mathutils import Color as VColor, Vector
from . cursor import Cursor, CursorIcon
from . layout import *
from . px import *
from . manager_modal import ModalManager as MOD
from . manager_draw import DrawManager as DRAW
from . slider import SliderGraphic, SliderHandle
from . pk_color import PkColorQuad, ToSlicePkColorQuad, PkColorCircle, PkColorRing
from colorsys import *
from . anchor import *
from . recent_colors import RecentColors
from . color import PreviewColorSwitch, PreviewColorDiff, PreviewColorHex, PreviewColorComplementary, PreviewColorAnalogous, PreviewColorSplitComplementary, PreviewColorTetradic, PreviewColorTriadic
from . slider_rad import SliderRadialDot
from . prefs import get_prefs

FACTOR_NUM_CHAR = 0.185 # 6666

class VIEW3D_OT_color_picker(Operator):
    bl_idname = "view3d.color_picker"
    bl_label = "Color Picker"

    @classmethod
    def poll(cls, context):
        return context.area.type == 'VIEW_3D' and context.mode in {'PAINT_TEXTURE', 'PAINT_VERTEX', 'PAINT_WEIGHT'}

    def invoke(self, context, event):
        self.init(context)
        return self.mod.start(context)
    
    def init_cursor(self, context):
        self.paint.show_brush = False
        Cursor.set_icon(context, CursorIcon.DEFAULT)

    def init(self, context):
        """ Init useful properties. """
        if context.mode == 'PAINT_TEXTURE':
            self.paint = context.tool_settings.image_paint
            self.texture = self.paint.brush.texture
        elif context.mode == 'PAINT_VERTEX':
            self.paint = context.tool_settings.vertex_paint
        elif context.mode == 'PAINT_WEIGHT':
            self.paint = context.tool_settings.weight_paint
        brush = self.paint.brush
        if not brush:
            self.finish(context)
            return {'FINISHED'}
        self.brush = brush
        self.ups = context.tool_settings.unified_paint_settings
        self.size = brush.size if not self.ups.use_unified_size else self.ups.size
        self.strength = brush.strength if not self.ups.use_unified_strength else self.ups.strength
        from . km import get_keyitem
        kmi = get_keyitem(context)
        self.key = kmi.type if kmi else 'SPACE'
        self.ctx_area = context.area
        self.ctx_region = context.region
        self.init_cursor(context)
        self.prefs = get_prefs(context)
        self.close_at_release = self.prefs.close_on_hotkey_release
        self.picker_type = self.prefs.color_picker_type
        self.auto_size = self.prefs.size_mode == 'AUTO'
        self.color = brush.color if not self.ups.use_unified_color else self.ups.color
        self.secondary_color = brush.secondary_color if not self.ups.use_unified_color else self.ups.secondary_color
        self.picking_color = False
        self.dpi = self.prefs.screen_dpi
        from . draw.text import text_settings
        text_settings['dpi'] = self.dpi
        if context.mode == 'PAINT_TEXTURE':
            self.init_layout_texture(context)
        elif context.mode == 'PAINT_VERTEX':
            self.init_layout_vertex(context)
        elif context.mode == 'PAINT_WEIGHT':
            self.init_layout_weight(context)
        self.mod = MOD(self, context, self.main_layout)
    
    def init_ui(self, context, attr):
        left = 0
        bottom = 0
        d_top = 0
        d_right = 0
        for reg in self.ctx_area.regions:
            if reg.type == 'UI':
                if reg.alignment == 'RIGHT':
                    d_right += reg.width + 10
                else:
                    left += reg.width
            elif reg.type == 'TOOLS':
                if reg.alignment == 'RIGHT':
                    d_right += reg.width
                else:
                    left += reg.width
            elif reg.type == 'HEADER':
                if reg.alignment == 'TOP':
                    d_top += reg.height
                    bottom += 10
                else:
                    bottom += reg.height
                    d_top += 10
        pivot = Vector((.5, .5))
        if self.auto_size and context.mode == 'PAINT_TEXTURE':
            ideal_width = 1292
            ideal_width_factor = 0.75
            ideal_height = 1010
            ideal_height_factor = 0.5
            width = context.area.width
            height = context.area.height
            rel_ideal_width_height = ideal_height / ideal_width
            rel_width_height = height / width
            rel_width = width / ideal_width
            rel_height = height / ideal_height
            fx = ideal_width_factor * rel_width
            fy = ideal_height_factor * rel_height
        else:
            fx, fy = getattr(self.prefs, attr)
        hfx = fx/2
        hfy = fy/2
        anchor_min = Vector((pivot.x-hfx, pivot.y-hfy))
        anchor_max = Vector((pivot.x+hfx, pivot.y+hfy))
        rw, rh = self.ctx_region.width, self.ctx_region.height
        if d_right != 0:
            rw -= d_right
        if d_top != 0:
            rh -= d_top
        xi = rw * anchor_min.x
        yi = rh * anchor_min.y
        xf = rw * anchor_max.x
        yf = rh * anchor_max.y
        if xi < left:
            xi = left
        if yi < bottom:
            yi = bottom
        def draw(self):
            DiRCTRND(*self.get_pos_size(), RGBA(Color.BLACK, .92), 10)
        main_layout = Layout()
        main_layout.set_unified_padding(10)
        main_layout.set_pos(xi, yi)
        main_layout.set_size(xf - xi, yf - yi)
        main_layout.set_draw_callback(draw)
        self.main_layout = main_layout
        self.wrapper = SubLayout(self.main_layout, Anchor(.0, 1.0, .0, 1.0)).set_unified_padding(10)
    
    def init_layout_weight(self, context):
        self.init_ui(context, 'weight_size_factor')
        wrapper = self.wrapper
        def draw_box(self):
            DiRCT(*self.get_pos_size(), RGBA(Color.BLACK, .95))
        def draw(data, wpos, wsize, fpos, fsize, value):
            DiRCTGRADBARLIN(wpos+wsize/2, wsize.x/2, (0, 0, 1, 1), (0, 1, 0, 1), (1, 0, 0, 1), wsize.y / wsize.x)
            SetLineSBlend(6)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
            Draw_Text_AlignCenter(*wpos + wsize/2, value[:4], 32, (1,1,1,.75))
        weight_slider_box = SubLayout(wrapper, Anchor(0, 1, 0, 1))
        weight_slider_box.set_draw_callback(draw_box)
        weight_slider_box.set_unified_padding(4)
        brush = self.brush if not self.ups.use_unified_weight else self.ups
        weight_slider = SliderGraphic(brush, 'weight', 0, 1, 0.001, True)
        weight_slider.set_anchor(Anchor(0, 1, 0, 1))
        weight_slider.set_layout(weight_slider_box)
        weight_slider.set_draw_callback(draw)
    
    def init_layout_texture(self, context):
        self.init_ui(context, 'texture_size_factor')
        self.init_pk(context, self.wrapper)
    
    def init_layout_vertex(self, context):
        self.init_ui(context, 'vertex_size_factor')
        self.init_pk(context, self.wrapper)
    
    def init_pk(self, context, layout, half=False):
        TEXT_S11_DIM_X, TEXT_S11_DIM_Y = SetFontSizeGetDim(0, 11, self.dpi, "O")
        if self.picker_type.startswith('SV'):
            #slcs = self.prefs.slices
            def draw(p, s, handle, co, slices, slicin):
                if slicin:
                    s_half_x = s.x/2
                    s_half_y = s.y/2
                    DiRCROMALIN(p, s_half_x, co.h)
                    DiRCTDOTMASK(p, s_half_x, (0, 0, 0, .65), slices)
                    SetLineSBlend(2)
                    if slices.min.x != 0:
                        hp = p.x+s.x*slices.min.x-s_half_x
                        DiLN((0, 0, 0, 1), Vector((hp, p.y-s_half_x)), Vector((hp, p.y + s_half_y)))
                    if slices.max.x != 0:
                        hp = p.x+s.x*slices.max.x-s_half_x
                        DiLN((0, 0, 0, 1), Vector((hp, p.y-s_half_x)), Vector((hp, p.y + s_half_y)))
                    if slices.min.y != 0:
                        hp = p.y+s.y*slices.min.y-s_half_y
                        DiLN((0, 0, 0, 1), Vector((p.x-s_half_x, hp)), Vector((p.x + s_half_x, hp)))
                    if slices.max.y != 0:
                        hp = p.y+s.y*slices.max.y-s_half_y
                        DiLN((0, 0, 0, 1), Vector((p.x-s_half_x, hp)), Vector((p.x + s_half_x, hp)))
                    RstLineSBlend()
                else:
                    DiRCROMALINSLICE(p, s.x/2, co.h, slices)
                    DiCFS(handle, 6, (pow(co[0], 2.2), pow(co[1], 2.2), pow(co[2], 2.2), 1)) # COLOR OK!
                    DiCLS(handle, 6, 10, 1.2, (1, 1, 1, 1))
            if self.picker_type == 'SV_H_RECT':
                def draw_anillo(p, s, handle, thick, co):
                    rad_handle = thick/4
                    DiCRCROMA(p, s, 1, 1)
                    DiCFS(handle, rad_handle, (1, 1, 1, 1))
                    DiCLS(handle, rad_handle, 10, 1.2, (0, 0, 0, 1))
                pkanillo = PkColorRing(self.brush, layout, Anchor(0, .48, 0.5, 1) if half else Anchor(0, .48, 0, 1), 20, draw_anillo)
                pkcol = ToSlicePkColorQuad(self.brush, layout, Anchor(.11, .36, 0.5, 1) if half else Anchor(.11, .36, 0, 1), draw)
                pkanillo.set_inner_widget(pkcol)
                pkanillo.set_on_change_value(pkcol.update_values)
                pkcol.set_on_confirm_value(pkanillo.update_value)
            else:
                pkcol = ToSlicePkColorQuad(self.brush, layout, Anchor(0, .48, 0.5, 1) if half else Anchor(0, .48, 0, 1), draw) # PkColorQuad
            def draw_slicer(data, wpos, wsize, fpos, fsize, value):
                SetLineSBlend(3.0)
                DiLN((.32, .32, .32, 1), Vector((fpos.x, fpos.y+5)), Vector((fpos.x, fpos.y-4)))
                RstLineSBlend()
            from . pk_color import cache
            has_cache = 'slices' in cache
            slice_slider_min_x = SliderHandle(pkcol.slices.min, 'x', 0, 1 if has_cache else (pkcol.slices.max, 'x', -.1), 0.001, True)
            slice_slider_min_x.snap_to_widget(pkcol, BOTTOM, OUTER, 10)
            slice_slider_min_x.set_draw_callback(draw_slicer)
            slice_slider_min_x.set_on_change_value(pkcol.enable_slicing)
            slice_slider_min_x.set_on_confirm_value(pkcol.disable_slicing)
            slice_slider_max_x = SliderHandle(pkcol.slices.max, 'x', 0.00001 if has_cache else (pkcol.slices.min, 'x', .1), 1, 0.001, True)
            slice_slider_max_x.snap_to_widget(pkcol, BOTTOM, OUTER, 10)
            slice_slider_max_x.set_draw_callback(draw_slicer)
            slice_slider_max_x.set_on_change_value(pkcol.enable_slicing)
            slice_slider_max_x.set_on_confirm_value(pkcol.disable_slicing)
            def draw_slicer(data, wpos, wsize, fpos, fsize, value):
                SetLineSBlend(3.0)
                DiLN((.32, .32, .32, 1), Vector((fpos.x+4, fpos.y)), Vector((fpos.x-5, fpos.y)))
                RstLineSBlend()
            slice_slider_min_y = SliderHandle(pkcol.slices.min, 'y', 0, 1 if has_cache else (pkcol.slices.max, 'y', -.1), 0.001, True, 1)
            slice_slider_min_y.snap_to_widget(pkcol, RIGHT, OUTER, 10)
            slice_slider_min_y.set_draw_callback(draw_slicer)
            slice_slider_min_y.set_on_change_value(pkcol.enable_slicing)
            slice_slider_min_y.set_on_confirm_value(pkcol.disable_slicing)
            slice_slider_max_y = SliderHandle(pkcol.slices.max, 'y', 0.00001 if has_cache else (pkcol.slices.min, 'y', .1), 1, 0.001, True, 1)
            slice_slider_max_y.snap_to_widget(pkcol, RIGHT, OUTER, 10)
            slice_slider_max_y.set_draw_callback(draw_slicer)
            slice_slider_max_y.set_on_change_value(pkcol.enable_slicing)
            slice_slider_max_y.set_on_confirm_value(pkcol.disable_slicing)
        else:
            def draw(c, r, handle, co):
                DiCCROMA(c, r, co.v)
                DiCFS(handle, 6, (pow(co[0], 2.2), pow(co[1], 2.2), pow(co[2], 2.2), 1)) # COLOR OK!
                DiCLS(handle, 6, 10, 1.2, (1, 1, 1, 1))
            pkcol = PkColorCircle(self.brush, layout, Anchor(0, .48, 0.5, 1) if half else Anchor(0, .48, 0, 1), draw)
        hsv_sliders = SubLayout(layout, Anchor(.5, 1, 0.70, .88) if half else Anchor(.5, 1, .4, .75)) # .5 + (.88-.5) / 2 * 1 + 0.04
        height_fac = 1.0 / 3.0
        def draw_box(self):
            DiRCT(*self.get_pos_size(), RGBA(Color.BLACK, .95))
        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5, wpos.y + TEXT_S11_DIM_Y/2, "H", 11)
            DiBARCromaH(wpos+wsize/2, wsize.x/2, data.s, data.v, wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        hue_slider_box = SubLayout(hsv_sliders, Anchor(0, 1, 1 - height_fac, 1))
        hue_slider_box.set_draw_callback(draw_box)
        hue_slider_box.set_padding(TEXT_S11_DIM_X + 10, 4, 4, 4)
        hue_slider = SliderGraphic(self.brush.color, 'h', 0, 1, 0.001, True)
        hue_slider.set_anchor(Anchor(0, 1, 0, 1))
        hue_slider.set_layout(hue_slider_box)
        hue_slider.set_draw_callback(draw)
        if self.picker_type == 'HS_CIRC':
            hue_slider.set_on_change_value(pkcol.update_values)
        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5, wpos.y + TEXT_S11_DIM_Y/2, "S", 11)
            DiBARCromaS(wpos+wsize/2, wsize.x/2, data.h, data.v, wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        sat_slider_box = SubLayout(hsv_sliders, Anchor(0, 1, height_fac, 1 - height_fac))
        sat_slider_box.set_draw_callback(draw_box)
        sat_slider_box.set_padding(TEXT_S11_DIM_X + 10, 4, 4, 4)
        sat_slider = SliderGraphic(self.brush.color, 's', 0.00001, 1, 0.001, True)
        sat_slider.set_anchor(Anchor(0, 1, 0, 1))
        sat_slider.set_layout(sat_slider_box)
        sat_slider.set_draw_callback(draw)
        pkcol.set_on_change_value_x(sat_slider.update_value)
        sat_slider.set_on_change_value(pkcol.update_values)
        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5, wpos.y + TEXT_S11_DIM_Y/2, "V", 11)
            DiBARCromaV(wpos+wsize/2, wsize.x/2, data.h, data.s, wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        val_slider_box = SubLayout(hsv_sliders, Anchor(0, 1, 0, height_fac))
        val_slider_box.set_draw_callback(draw_box)
        val_slider_box.set_padding(TEXT_S11_DIM_X + 10, 4, 4, 4)
        val_slider = SliderGraphic(self.brush.color, 'v', 0.00001, 1, 0.001, True)
        val_slider.set_anchor(Anchor(0, 1, 0, 1))
        val_slider.set_layout(val_slider_box)
        val_slider.set_draw_callback(draw)
        pkcol.set_on_change_value_x(val_slider.update_value)
        val_slider.set_on_change_value(pkcol.update_values)
        rgb_sliders = SubLayout(layout, Anchor(.5, 1, 0.5, 0.68) if half else Anchor(.5, 1, 0, .35)) # .5 + (.88-.5) / 2 * 1 + 0.04
        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5, wpos.y + TEXT_S11_DIM_Y/2, "R", 11)
            DiBARCromaR(wpos+wsize/2, wsize.x/2, (data.r, data.g, data.b), wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        red_slider_box = SubLayout(rgb_sliders, Anchor(0, 1, 1 - height_fac, 1)) # height_fac * 2, 1 - height_fac * 3
        red_slider_box.set_draw_callback(draw_box)
        red_slider_box.set_padding(TEXT_S11_DIM_X + 10, 4, 4, 4)
        red_slider = SliderGraphic(self.brush.color, 'r', 0, 1, 0.001, True)
        red_slider.set_anchor(Anchor(0, 1, 0, 1))
        red_slider.set_layout(red_slider_box)
        red_slider.set_draw_callback(draw)
        hue_slider.set_on_change_value(red_slider.update_value)
        sat_slider.set_on_change_value(red_slider.update_value)
        val_slider.set_on_change_value(red_slider.update_value)
        red_slider.set_on_change_value(hue_slider.update_value)
        red_slider.set_on_change_value(sat_slider.update_value)
        red_slider.set_on_change_value(val_slider.update_value)
        pkcol.set_on_change_value_x(red_slider.update_value)
        red_slider.set_on_change_value(pkcol.update_values)
        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5, wpos.y + TEXT_S11_DIM_Y/2, "G", 11)
            DiBARCromaG(wpos+wsize/2, wsize.x/2, (data.r, data.g, data.b), wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        green_slider_box = SubLayout(rgb_sliders, Anchor(0, 1, height_fac, 1 - height_fac)) # height_fac, 1 - height_fac * 4
        green_slider_box.set_draw_callback(draw_box)
        green_slider_box.set_padding(TEXT_S11_DIM_X + 10, 4, 4, 4)
        green_slider = SliderGraphic(self.brush.color, 'g', 0, 1, 0.001, True)
        green_slider.set_anchor(Anchor(0, 1, 0, 1))
        green_slider.set_layout(green_slider_box)
        green_slider.set_draw_callback(draw)
        hue_slider.set_on_change_value(green_slider.update_value)
        sat_slider.set_on_change_value(green_slider.update_value)
        val_slider.set_on_change_value(green_slider.update_value)
        green_slider.set_on_change_value(hue_slider.update_value)
        green_slider.set_on_change_value(sat_slider.update_value)
        green_slider.set_on_change_value(val_slider.update_value)
        pkcol.set_on_change_value_x(green_slider.update_value)
        green_slider.set_on_change_value(pkcol.update_values)
        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5, wpos.y + TEXT_S11_DIM_Y/2, "B", 11)
            DiBARCromaB(wpos+wsize/2, wsize.x/2, (data.r, data.g, data.b), wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        blue_slider_box = SubLayout(rgb_sliders, Anchor(0, 1, 0, height_fac)) # 0, 1 - height_fac * 5
        blue_slider_box.set_draw_callback(draw_box)
        blue_slider_box.set_padding(TEXT_S11_DIM_X + 10, 4, 4, 4)                           
        blue_slider = SliderGraphic(self.brush.color, 'b', 0, 1, 0.001, True)
        blue_slider.set_anchor(Anchor(0, 1, 0, 1))
        blue_slider.set_layout(blue_slider_box)
        blue_slider.set_draw_callback(draw)
        hue_slider.set_on_change_value(blue_slider.update_value)
        sat_slider.set_on_change_value(blue_slider.update_value)
        val_slider.set_on_change_value(blue_slider.update_value)
        blue_slider.set_on_change_value(hue_slider.update_value)
        blue_slider.set_on_change_value(sat_slider.update_value)
        blue_slider.set_on_change_value(val_slider.update_value)
        pkcol.set_on_change_value_x(blue_slider.update_value)
        blue_slider.set_on_change_value(pkcol.update_values)
        colors_box = SubLayout(layout, Anchor(.5, 1, .9, 1) if half else Anchor(.5, 1, .8, 1))
        colors_box.set_draw_callback(draw_box)
        colors_box.set_unified_padding(4)
        def draw(pos, size, color, new_color):
            half_height = size.y/2
            DiRCT(pos+Vector((0, half_height)), (size.x, half_height), (*color, 1))
            DiRCT(pos, (size.x, half_height), (*new_color, 1))
            DiMARCRCT(pos, size, (.7, .7, .7, 1))
        preview_diff = PreviewColorDiff(colors_box, Anchor(0, 0.08, 0, 1), draw, self.brush)
        hue_slider.set_on_confirm_value(preview_diff.confirm_new_color)
        sat_slider.set_on_confirm_value(preview_diff.confirm_new_color)
        val_slider.set_on_confirm_value(preview_diff.confirm_new_color)
        red_slider.set_on_confirm_value(preview_diff.confirm_new_color)
        green_slider.set_on_confirm_value(preview_diff.confirm_new_color)
        blue_slider.set_on_confirm_value(preview_diff.confirm_new_color)
        pkcol.set_on_confirm_value(preview_diff.confirm_new_color)
        if self.prefs.show_hex:
            def draw(pos, size, hex):
                Draw_Text(*pos, hex, 10)
            dim = SetFontSizeGetDim(0,10,self.dpi,'#000000')
            preview_hex = PreviewColorHex(layout, Anchor(1, dim[0]+5*self.dpi/72, .48, dim[1]) if half else Anchor(1, dim[0]+5*self.dpi/72, -0.05, dim[1]), draw, self.brush)
        def draw(slots, size, data, hov_idx):
            n = len(slots) - 1
            for i, co in enumerate(reversed(data)):
                if i >= n:
                    break
                DiRCT(slots[i], size, (*co, 1))  
            if hov_idx != -1:
                DiMARCRCT(slots[hov_idx], size, (1, 1, 1, 1))
        recent_colors_widget = RecentColors(colors_box, Anchor(.1, 1, 0, 1), draw, 2, 10, 2, self.brush, 'color', 0, True, 'RecentColors')
        hue_slider.set_on_confirm_value(recent_colors_widget.learn)
        sat_slider.set_on_confirm_value(recent_colors_widget.learn)
        val_slider.set_on_confirm_value(recent_colors_widget.learn)
        red_slider.set_on_confirm_value(recent_colors_widget.learn)
        green_slider.set_on_confirm_value(recent_colors_widget.learn)
        blue_slider.set_on_confirm_value(recent_colors_widget.learn)
        pkcol.set_on_confirm_value(recent_colors_widget.learn)
        recent_colors_widget.set_on_click_callback(hue_slider.update_value)
        recent_colors_widget.set_on_click_callback(sat_slider.update_value)
        recent_colors_widget.set_on_click_callback(val_slider.update_value)
        recent_colors_widget.set_on_click_callback(red_slider.update_value)
        recent_colors_widget.set_on_click_callback(green_slider.update_value)
        recent_colors_widget.set_on_click_callback(blue_slider.update_value)
        recent_colors_widget.set_on_click_callback(pkcol.update_values)
        recent_colors_widget.set_on_click_callback(preview_diff.confirm_new_color)
        if self.picker_type == 'SV_H_RECT':
            hue_slider.set_on_change_value(pkanillo.update_value)
            pkanillo.set_on_confirm_value(hue_slider.update_value)
            red_slider.set_on_confirm_value(pkanillo.update_value)
            green_slider.set_on_confirm_value(pkanillo.update_value)
            blue_slider.set_on_confirm_value(pkanillo.update_value)
            pkanillo.set_on_confirm_value(red_slider.update_value)
            pkanillo.set_on_confirm_value(green_slider.update_value)
            pkanillo.set_on_confirm_value(blue_slider.update_value)
            recent_colors_widget.set_on_click_callback(pkanillo.update_value)
            pkanillo.set_on_confirm_value(recent_colors_widget.learn)

    def modal(self, context, event):
        if (event.type == self.key and event.value == 'RELEASE' and self.close_at_release) or (event.type == self.key and event.value == 'PRESS' and not self.close_at_release) or event.type == 'ESC' or (event.type == 'LEFTMOUSE' and event.value == 'PRESS' and not self.close_at_release and not point_inside_rect((event.mouse_region_x, event.mouse_region_y), *self.main_layout.get_pos_size())):
            self.finish(context if context.area==self.ctx_area else None)
            return {'FINISHED'}
        return self.mod((self, context, event)) # TODO: finish this :-(

    def finish(self, context=None):
        self.mod.stop(context==None)
        self.paint.show_brush = True
        Cursor.set_icon(context, CursorIcon.PAINT_CROSS)
