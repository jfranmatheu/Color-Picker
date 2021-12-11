from . utils.fun import *
from math import cos, sin, tan, pi, degrees, atan, floor
from mathutils import Color as VColor, Vector
from . cursor import Cursor, CursorIcon
from . tuoya import *
from . px import *
from . modiman import Modiman as MOD
from . dibuman import Dibuman as DRAW
from . sld import SldGraphic, SldHandle
from . pk_color import PkColorQuad, ToSlicePkColorQuad, PkColorCircle, PkColorRing
from colorsys import *
from . anchor import *
from . colrec import ColRec
from . color import ColPrevSwitch, ColPrevDiff, ColPrevHex, ColPrevComplementary, ColPrevAnalogous, ColPrevSplitComplementary, ColPrevTetradic, ColPrevTriadic
from . sld_rad import SldRadDot
from . prefs import get_prefs

FACTOR_NUM_CHAR = 0.185  # 6666


class Colpk(object):
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
        self.color = brush.color if not self.ups.use_unified_color else self.ups.color
        self.secondary_color = brush.secondary_color if not self.ups.use_unified_color else self.ups.secondary_color
        self.picking_color = False
        self.dpi = self.prefs.screen_dpi
        from . draw.text import text_settings
        text_settings['dpi'] = self.dpi
        if context.mode == 'PAINT_TEXTURE':
            self.init_tuoy_texture(context)
        elif context.mode == 'PAINT_VERTEX':
            self.init_tuoy_vertex(context)
        elif context.mode == 'PAINT_WEIGHT':
            self.init_tuoy_weight(context)
        self.mod = MOD(self, context, self.main_tuoy)

    def init_ui(self, context):
        '''
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
        '''

        reg = context.region
        reg_center = Vector((
            int(reg.width / 2),
            int(reg.height / 2)
        ))

        scale = self.dpi/72 * getattr(self.prefs, 'scale', 1)

        if context.mode == 'PAINT_WEIGHT':
            _width = 360 * scale
            _heigth = _width * .2
        else:
            _width = 400 * scale
            _heigth = _width * .5

        _w_2 = int(_width / 2)
        _h_2 = int(_heigth / 2)

        xi = reg_center.x - _w_2
        xf = reg_center.x + _w_2
        yi = reg_center.y - _h_2
        yf = reg_center.y + _h_2

        ''' ###################################
        WORKAROUND:
            BUG introduced in API (2.93+) due to bgl module deprecation,
            limits the 'POINT' shader type to 128px of radius (total dimensions of 256x256px).
        '''
        '''
        if context.mode == 'PAINT_WEIGHT':
            width = xf - xi
            if width > 284:
                w_2 = (width - 284) / 2.0
                xf -= w_2
                xi += w_2

            elif width < 170:
                w_2 = (170 - width) / 2.0
                xf += w_2
                xi -= w_2
            
            width = xf - xi
            height = yf - yi
            if height > width / 2.5:
                h_2 = (height - (width / 2.5)) / 2.0
                yf -= h_2
                yi += h_2

            elif height < 80:
                h_2 = (80 - height) / 2.0
                yf += h_2
                yi -= h_2

        else:
            width = xf - xi
            if width > 574:
                w_2 = (width - 574) / 2.0
                xf -= w_2
                xi += w_2

            elif width < 256:
                w_2 = (256 - width) / 2.0
                xf += w_2
                xi -= w_2
            
            height = yf - yi
            if height > 310:
                h_2 = (height - 310) / 2.0
                yf -= h_2
                yi += h_2

            elif height < 256:
                h_2 = (256 - height) / 2.0
                yf += h_2
                yi -= h_2
        '''

        ''' ################################### '''

        def draw(self):
            DiRCTRND(*self.get_pos_size(), RGBA(Color.BLACK, .92), 10)
        main_tuoy = Tuoya()
        main_tuoy.set_unified_padding(10)
        main_tuoy.set_pos(xi, yi)
        main_tuoy.set_size(_width, _heigth)  # (xf - xi, yf - yi)
        main_tuoy.stdibucalba(draw)
        self.main_tuoy = main_tuoy
        self.wrapper = Subtuoya(
            self.main_tuoy, Anchor(.0, 1.0, .0, 1.0)).set_unified_padding(10)

    def init_tuoy_weight(self, context):
        self.init_ui(context)
        wrapper = self.wrapper

        def draw_box(self):
            DiRCT(*self.get_pos_size(), RGBA(Color.BLACK, .95))

        def draw(data, wpos, wsize, fpos, fsize, value):
            DiRCTGRADBARLIN(wpos+wsize/2, wsize.x/2, (0, 0, 1, 1),
                            (0, 1, 0, 1), (1, 0, 0, 1), wsize.y / wsize.x)
            SetLineSBlend(6)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
            Draw_Text_AlignCenter(
                *wpos + wsize/2, value[:4], 20, (1, 1, 1, .75))
        weight_sld_box = Subtuoya(wrapper, Anchor(0, 1, 0, 1))
        weight_sld_box.stdibucalba(draw_box)
        weight_sld_box.set_unified_padding(4)
        brush = self.brush if not self.ups.use_unified_weight else self.ups
        weight_sld = SldGraphic(brush, 'weight', 0, 1, 0.001, True)
        weight_sld.set_anchor(Anchor(0, 1, 0, 1))
        weight_sld.set_tuoy(weight_sld_box)
        weight_sld.stdibucalba(draw)

    def init_tuoy_texture(self, context):
        self.init_ui(context)
        self.init_pk(context, self.wrapper)

    def init_tuoy_vertex(self, context):
        self.init_ui(context)
        self.init_pk(context, self.wrapper)

    def init_pk(self, context, tuoy, half=False):
        TEXT_S11_DIM_X, TEXT_S11_DIM_Y = SetFontSizeGetDim(
            0, 11, self.dpi, "O")
        #tuoy_top = Subtuoya(tuoy, Anchor(0, 1, .5, 1))
        #tuoy_top.set_pad(0, 0, 16, 0)
        tuoy_top = tuoy
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
                        DiLN((0, 0, 0, 1), Vector((hp, p.y-s_half_x)),
                             Vector((hp, p.y + s_half_y)))
                    if slices.max.x != 0:
                        hp = p.x+s.x*slices.max.x-s_half_x
                        DiLN((0, 0, 0, 1), Vector((hp, p.y-s_half_x)),
                             Vector((hp, p.y + s_half_y)))
                    if slices.min.y != 0:
                        hp = p.y+s.y*slices.min.y-s_half_y
                        DiLN((0, 0, 0, 1), Vector((p.x-s_half_x, hp)),
                             Vector((p.x + s_half_x, hp)))
                    if slices.max.y != 0:
                        hp = p.y+s.y*slices.max.y-s_half_y
                        DiLN((0, 0, 0, 1), Vector((p.x-s_half_x, hp)),
                             Vector((p.x + s_half_x, hp)))
                    RstLineSBlend()
                else:
                    DiRCROMALINSLICE(p, s.x/2, co.h, slices)
                    DiCFS(handle, 6, (pow(co[0], 2.2), pow(
                        co[1], 2.2), pow(co[2], 2.2), 1))  # COLOR OK!
                    DiCLS(handle, 6, 10, 1.2, (1, 1, 1, 1))
            if self.picker_type == 'SV_H_RECT':
                def draw_anillo(p, s, handle, thick, co):
                    rad_handle = thick/4
                    DiCRCROMA(p, s, 1, 1)
                    DiCFS(handle, rad_handle, (1, 1, 1, 1))
                    DiCLS(handle, rad_handle, 10, 1.2, (0, 0, 0, 1))
                pkanillo = PkColorRing(self.brush, tuoy_top, Anchor(
                    0, .48, 0.5, 1) if half else Anchor(0, .48, 0, 1), 20, draw_anillo)
                pkcol = ToSlicePkColorQuad(
                    self.brush, tuoy_top, Anchor(.11, .36, 0.5, 1) if half else Anchor(.11, .36, 0, 1), draw)
                pkanillo.set_inner_teg(pkcol)
                pkanillo.onechanval(pkcol.upd_vals)
                pkcol.onestval(pkanillo.upd_val)
            else:
                pkcol = ToSlicePkColorQuad(self.brush, tuoy_top, Anchor(
                    0, .48, 0.5, 1) if half else Anchor(0, .48, 0, 1), draw)  # PkColorQuad

            def di_slc(data, wpos, wsize, fpos, fsize, value):
                SetLineSBlend(3.0)
                DiLN((.32, .32, .32, 1), Vector(
                    (fpos.x, fpos.y+5)), Vector((fpos.x, fpos.y-4)))
                RstLineSBlend()
            from . pk_color import cache
            has_cache = 'slices' in cache
            slice_sld_min_x = SldHandle(pkcol.slices.min, 'x', 0, 1 if has_cache else (
                pkcol.slices.max, 'x', -.1), 0.001, True)
            slice_sld_min_x.snap_to_teg(pkcol, BOTTOM, OUTER, 10)
            slice_sld_min_x.stdibucalba(di_slc)
            slice_sld_min_x.onechanval(pkcol.enable_slicing)
            slice_sld_min_x.onestval(pkcol.disable_slicing)
            slice_sld_max_x = SldHandle(pkcol.slices.max, 'x', 0.00001 if has_cache else (
                pkcol.slices.min, 'x', .1), 1, 0.001, True)
            slice_sld_max_x.snap_to_teg(pkcol, BOTTOM, OUTER, 10)
            slice_sld_max_x.stdibucalba(di_slc)
            slice_sld_max_x.onechanval(pkcol.enable_slicing)
            slice_sld_max_x.onestval(pkcol.disable_slicing)

            def di_slc(data, wpos, wsize, fpos, fsize, value):
                SetLineSBlend(3.0)
                DiLN((.32, .32, .32, 1), Vector(
                    (fpos.x+4, fpos.y)), Vector((fpos.x-5, fpos.y)))
                RstLineSBlend()
            slice_sld_min_y = SldHandle(pkcol.slices.min, 'y', 0, 1 if has_cache else (
                pkcol.slices.max, 'y', -.1), 0.001, True, 1)
            slice_sld_min_y.snap_to_teg(pkcol, RIGHT, OUTER, 10)
            slice_sld_min_y.stdibucalba(di_slc)
            slice_sld_min_y.onechanval(pkcol.enable_slicing)
            slice_sld_min_y.onestval(pkcol.disable_slicing)
            slice_sld_max_y = SldHandle(pkcol.slices.max, 'y', 0.00001 if has_cache else (
                pkcol.slices.min, 'y', .1), 1, 0.001, True, 1)
            slice_sld_max_y.snap_to_teg(pkcol, RIGHT, OUTER, 10)
            slice_sld_max_y.stdibucalba(di_slc)
            slice_sld_max_y.onechanval(pkcol.enable_slicing)
            slice_sld_max_y.onestval(pkcol.disable_slicing)
        else:
            def draw(c, r, handle, co):
                DiCCROMA(c, r, co.v)
                DiCFS(handle, 6, (pow(co[0], 2.2), pow(
                    co[1], 2.2), pow(co[2], 2.2), 1))  # COLOR OK!
                DiCLS(handle, 6, 10, 1.2, (1, 1, 1, 1))
            pkcol = PkColorCircle(self.brush, tuoy_top, Anchor(
                0, .48, 0.5, 1) if half else Anchor(0, .48, 0, 1), draw)
        # .5 + (.88-.5) / 2 * 1 + 0.04
        hsv_slds = Subtuoya(tuoy_top, Anchor(.5, 1, 0.70, .88)
                            if half else Anchor(.5, 1, .39, .75))
        height_fac = 1.0 / 3.0

        def draw_box(self):
            DiRCT(*self.get_pos_size(), RGBA(Color.BLACK, .95))

        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5,
                      wpos.y + TEXT_S11_DIM_Y/2, "H", 11)
            DiBARCromaH(wpos+wsize/2, wsize.x/2, data.s,
                        data.v, wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        hue_sld_box = Subtuoya(hsv_slds, Anchor(0, 1, 1 - height_fac, 1))
        hue_sld_box.stdibucalba(draw_box)
        hue_sld_box.set_pad(TEXT_S11_DIM_X + 10, 4, 2, 2)
        hue_sld = SldGraphic(self.brush.color, 'h', 0, 1, 0.001, True)
        hue_sld.set_anchor(Anchor(0, 1, 0, 1))
        hue_sld.set_tuoy(hue_sld_box)
        hue_sld.stdibucalba(draw)
        if self.picker_type == 'HS_CIRC':
            hue_sld.onechanval(pkcol.upd_vals)

        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5,
                      wpos.y + TEXT_S11_DIM_Y/2, "S", 11)
            DiBARCromaS(wpos+wsize/2, wsize.x/2, data.h,
                        data.v, wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        sat_sld_box = Subtuoya(hsv_slds, Anchor(
            0, 1, height_fac, 1 - height_fac))
        sat_sld_box.stdibucalba(draw_box)
        sat_sld_box.set_pad(TEXT_S11_DIM_X + 10, 4, 2, 2)
        sat_sld = SldGraphic(self.brush.color, 's', 0.00001, 1, 0.001, True)
        sat_sld.set_anchor(Anchor(0, 1, 0, 1))
        sat_sld.set_tuoy(sat_sld_box)
        sat_sld.stdibucalba(draw)
        pkcol.onechanval_x(sat_sld.upd_val)
        sat_sld.onechanval(pkcol.upd_vals)

        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5,
                      wpos.y + TEXT_S11_DIM_Y/2, "V", 11)
            DiBARCromaV(wpos+wsize/2, wsize.x/2, data.h,
                        data.s, wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        val_sld_box = Subtuoya(hsv_slds, Anchor(0, 1, 0, height_fac))
        val_sld_box.stdibucalba(draw_box)
        val_sld_box.set_pad(TEXT_S11_DIM_X + 10, 4, 2, 2)
        val_sld = SldGraphic(self.brush.color, 'v', 0.00001, 1, 0.001, True)
        val_sld.set_anchor(Anchor(0, 1, 0, 1))
        val_sld.set_tuoy(val_sld_box)
        val_sld.stdibucalba(draw)
        pkcol.onechanval_x(val_sld.upd_val)
        val_sld.onechanval(pkcol.upd_vals)
        # .5 + (.88-.5) / 2 * 1 + 0.04
        rgb_slds = Subtuoya(tuoy_top, Anchor(.5, 1, 0.5, 0.68)
                            if half else Anchor(.5, 1, 0, .36))

        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5,
                      wpos.y + TEXT_S11_DIM_Y/2, "R", 11)
            DiBARCromaR(wpos+wsize/2, wsize.x/2,
                        (data.r, data.g, data.b), wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        # height_fac * 2, 1 - height_fac * 3
        red_sld_box = Subtuoya(rgb_slds, Anchor(0, 1, 1 - height_fac, 1))
        red_sld_box.stdibucalba(draw_box)
        red_sld_box.set_pad(TEXT_S11_DIM_X + 10, 4, 2, 2)
        red_sld = SldGraphic(self.brush.color, 'r', 0, 1, 0.001, True)
        red_sld.set_anchor(Anchor(0, 1, 0, 1))
        red_sld.set_tuoy(red_sld_box)
        red_sld.stdibucalba(draw)
        hue_sld.onechanval(red_sld.upd_val)
        sat_sld.onechanval(red_sld.upd_val)
        val_sld.onechanval(red_sld.upd_val)
        red_sld.onechanval(hue_sld.upd_val)
        red_sld.onechanval(sat_sld.upd_val)
        red_sld.onechanval(val_sld.upd_val)
        pkcol.onechanval_x(red_sld.upd_val)
        red_sld.onechanval(pkcol.upd_vals)

        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5,
                      wpos.y + TEXT_S11_DIM_Y/2, "G", 11)
            DiBARCromaG(wpos+wsize/2, wsize.x/2,
                        (data.r, data.g, data.b), wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+2))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        # height_fac, 1 - height_fac * 4
        green_sld_box = Subtuoya(rgb_slds, Anchor(
            0, 1, height_fac, 1 - height_fac))
        green_sld_box.stdibucalba(draw_box)
        green_sld_box.set_pad(TEXT_S11_DIM_X + 10, 4, 2, 2)
        green_sld = SldGraphic(self.brush.color, 'g', 0, 1, 0.001, True)
        green_sld.set_anchor(Anchor(0, 1, 0, 1))
        green_sld.set_tuoy(green_sld_box)
        green_sld.stdibucalba(draw)
        hue_sld.onechanval(green_sld.upd_val)
        sat_sld.onechanval(green_sld.upd_val)
        val_sld.onechanval(green_sld.upd_val)
        green_sld.onechanval(hue_sld.upd_val)
        green_sld.onechanval(sat_sld.upd_val)
        green_sld.onechanval(val_sld.upd_val)
        pkcol.onechanval_x(green_sld.upd_val)
        green_sld.onechanval(pkcol.upd_vals)

        def draw(data, wpos, wsize, fpos, fsize, value):
            Draw_Text(wpos.x - TEXT_S11_DIM_X - 5,
                      wpos.y + TEXT_S11_DIM_Y/2, "B", 11)
            DiBARCromaB(wpos+wsize/2, wsize.x/2,
                        (data.r, data.g, data.b), wsize.y / wsize.x)
            SetLineSBlend(4)
            DiLN((.1, .1, .1, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            SetLineSBlend(1.3)
            DiLN((.8, .8, .8, 1), (fpos.x, wpos.y-1), (fpos.x, wpos.y+wsize.y+1))
            RstLineSBlend()
            DiMARCRCT(wpos, wsize, (.21, .21, .21, .5))
        blue_sld_box = Subtuoya(rgb_slds, Anchor(
            0, 1, 0, height_fac))  # 0, 1 - height_fac * 5
        blue_sld_box.stdibucalba(draw_box)
        blue_sld_box.set_pad(TEXT_S11_DIM_X + 10, 4, 2, 2)
        blue_sld = SldGraphic(self.brush.color, 'b', 0, 1, 0.001, True)
        blue_sld.set_anchor(Anchor(0, 1, 0, 1))
        blue_sld.set_tuoy(blue_sld_box)
        blue_sld.stdibucalba(draw)
        hue_sld.onechanval(blue_sld.upd_val)
        sat_sld.onechanval(blue_sld.upd_val)
        val_sld.onechanval(blue_sld.upd_val)
        blue_sld.onechanval(hue_sld.upd_val)
        blue_sld.onechanval(sat_sld.upd_val)
        blue_sld.onechanval(val_sld.upd_val)
        pkcol.onechanval_x(blue_sld.upd_val)
        blue_sld.onechanval(pkcol.upd_vals)
        colors_box = Subtuoya(tuoy_top, Anchor(.5, 1, .9, 1)
                              if half else Anchor(.5, 1, .78, 1))
        colors_box.stdibucalba(draw_box)
        colors_box.set_unified_padding(4)

        def draw(pos, size, color, new_color):
            half_height = size.y/2
            DiRCT(pos+Vector((0, half_height)),
                  (size.x, half_height), (*color, 1))
            DiRCT(pos, (size.x, half_height), (*new_color, 1))
            DiMARCRCT(pos, size, (.7, .7, .7, 1))
        preview_diff = ColPrevDiff(
            colors_box, Anchor(0, 0.08, 0, 1), draw, self.brush)
        hue_sld.onestval(preview_diff.confirm_new_color)
        sat_sld.onestval(preview_diff.confirm_new_color)
        val_sld.onestval(preview_diff.confirm_new_color)
        red_sld.onestval(preview_diff.confirm_new_color)
        green_sld.onestval(preview_diff.confirm_new_color)
        blue_sld.onestval(preview_diff.confirm_new_color)
        pkcol.onestval(preview_diff.confirm_new_color)
        if self.prefs.show_hex:
            def draw(pos, size, hex):
                Draw_Text(*pos, hex, 10)
            dim = SetFontSizeGetDim(0, 10, self.dpi, '#000000')
            preview_hex = ColPrevHex(tuoy_top, Anchor(1, dim[0]+5*self.dpi/72, .48, dim[1]) if half else Anchor(
                1, dim[0]+5*self.dpi/72, -0.05, dim[1]), draw, self.brush)

        def draw(slots, size, data, hov_idx):
            n = len(slots) - 1
            for i, co in enumerate(reversed(data)):
                if i >= n:
                    break
                DiRCT(slots[i], size, (*co, 1))
            if hov_idx != -1:
                DiMARCRCT(slots[hov_idx], size, (1, 1, 1, 1))
        colrec_teg = ColRec(colors_box, Anchor(.1, 1, 0, 1),
                            draw, 2, 12, 2, self.brush, 'color', 0, True, 'ColRec')
        hue_sld.onestval(colrec_teg.learn)
        sat_sld.onestval(colrec_teg.learn)
        val_sld.onestval(colrec_teg.learn)
        red_sld.onestval(colrec_teg.learn)
        green_sld.onestval(colrec_teg.learn)
        blue_sld.onestval(colrec_teg.learn)
        pkcol.onestval(colrec_teg.learn)
        colrec_teg.set_act_back(hue_sld.upd_val)
        colrec_teg.set_act_back(sat_sld.upd_val)
        colrec_teg.set_act_back(val_sld.upd_val)
        colrec_teg.set_act_back(red_sld.upd_val)
        colrec_teg.set_act_back(green_sld.upd_val)
        colrec_teg.set_act_back(blue_sld.upd_val)
        colrec_teg.set_act_back(pkcol.upd_vals)
        colrec_teg.set_act_back(preview_diff.confirm_new_color)
        if self.picker_type == 'SV_H_RECT':
            hue_sld.onechanval(pkanillo.upd_val)
            pkanillo.onestval(hue_sld.upd_val)
            red_sld.onestval(pkanillo.upd_val)
            green_sld.onestval(pkanillo.upd_val)
            blue_sld.onestval(pkanillo.upd_val)
            pkanillo.onestval(red_sld.upd_val)
            pkanillo.onestval(green_sld.upd_val)
            pkanillo.onestval(blue_sld.upd_val)
            colrec_teg.set_act_back(pkanillo.upd_val)
            pkanillo.onestval(colrec_teg.learn)

        # BOT
        #tuoy_bot = Subtuoya(tuoy, Anchor(0, 1, 0, .5))
        #tuoy_bot.set_pad(0, 0, 0, 4)

    def modal(self, context, event):
        if (event.type == self.key and event.value == 'RELEASE' and self.close_at_release) or (event.type == self.key and event.value == 'PRESS' and not self.close_at_release) or event.type == 'ESC' or (event.type == 'LEFTMOUSE' and event.value == 'PRESS' and not self.close_at_release and not point_inside_rect((event.mouse_region_x, event.mouse_region_y), *self.main_tuoy.get_pos_size())):
            self.finish(context if context.area == self.ctx_area else None)
            return {'FINISHED'}
        return self.mod((self, context, event))  # TODO: finish this :-(

    def finish(self, context=None):
        self.mod.stop(context == None)
        self.paint.show_brush = True
        Cursor.set_icon(context, CursorIcon.PAINT_CROSS)
