from . anchor import Anchor, Vector


class Tsform:
    def set_size(self, _width: int, _height: int) -> None:
        self.size = Vector((_width, _height))

    def set_pos(self, _x: int, _y: int) -> None:
        self.pos = Vector((_x, _y))
        
    def get_pos_size(self) -> (Vector, Vector):
        return self.pos, self.size
    
    def center(self) -> Vector:
        return self.pos + self.size / 2
    
    def top_right(self) -> Vector:
        return self.pos + self.size
    
    def top_left(self) -> Vector:
        return self.pos + Vector((0, self.size.y))
    
    def bottom_left(self) -> Vector:
        return self.pos
    
    def bottom_right(self) -> Vector:
        return self.pos + Vector((self.size.x, 0))
    
    def dot_center_center(self) -> Vector:
        return self.pos - self.size / 2

class TsformAnch(Tsform):
    def set_anchor(self, _anchor: Anchor) -> None:
        self.anchor = _anchor
        if hasattr(self, 'parent') and _anchor:
            self.update()

    def setpar(self, parent) -> None:
        from . tuoya import Basetuoya
        if not isinstance(parent, Basetuoya):
            return
        self.parent = parent
        if hasattr(self, 'anchor') and self.anchor and parent:
            self.update()

    def update(self) -> None:
        if not self.parent:
            return
        ppos, psize = self.parent.get_inner_pos_size()

        xi = ppos.x + psize.x * self.anchor.min.x
        yi = ppos.y + psize.y * self.anchor.min.y

        xf = ppos.x + psize.x * self.anchor.max.x
        yf = ppos.y + psize.y * self.anchor.max.y

        anchor_max = Vector((xf, yf))
        self.set_pos(xi, yi)
        self.set_size(*(anchor_max - self.pos))

    def initUI(self) -> None:
        self.update()

class TsformAnchFixed(TsformAnch):
    def set_anchor(self, _anchor: Anchor) -> None:
        self.fixed_width = (_anchor.min.x <= 1 and _anchor.max.x > 1)
        self.fixed_height = (_anchor.min.y <= 1 and _anchor.max.y > 1)
        super().set_anchor(_anchor)

    def update(self) -> None:
        if not self.parent:
            return
        ppos, psize = self.parent.get_inner_pos_size()

        if hasattr(self, 'fixed_width') and self.fixed_width:
            if self.anchor.min.x == 1:
                xf = ppos.x + psize.x
                xi = xf - self.anchor.max.x
            elif self.anchor.min.x == 0:
                xi = ppos.x
                xf = xi + self.anchor.max.x
            # Minimo es factor persoanlizado.
            elif self.anchor.min.x >= 0 or self.anchor.min.x <= 1:
                if self.anchor.max.x > 0:
                    xi = ppos.x + psize.x * self.anchor.min.x
                    xf = xi + self.anchor.max.x
                else:
                    xf = ppos.x + psize.x * self.anchor.min.x
                    xi = xf - self.anchor.max.x
        else:
            xi = ppos.x + psize.x * self.anchor.min.x
            xf = ppos.x + psize.x * self.anchor.max.x
        if hasattr(self, 'fixed_height') and self.fixed_height:
            if self.anchor.min.y == 1:
                yf = ppos.y + psize.y
                yi = yf - self.anchor.max.y
            elif self.anchor.min.y == 0:
                yi = ppos.y
                yf = yi + self.anchor.max.y
            elif self.anchor.min.y >= 0 or self.anchor.min.y <= 1:
                if self.anchor.max.y > 0:
                    yi = ppos.y + psize.y * self.anchor.min.y
                    yf = yi + self.anchor.max.y
                else:
                    yf = ppos.y + psize.y * self.anchor.min.y
                    yi = yf - self.anchor.max.y
        else:
            yi = ppos.y + psize.y * self.anchor.min.y
            yf = ppos.y + psize.y * self.anchor.max.y

        anchor_max = Vector((xf, yf))
        self.set_pos(xi, yi)
        self.set_size(*(anchor_max - self.pos))

class TsformAdvanced(Tsform):
    def set_size(self, _width: int, _height: int) -> None:
        super().set_size(_width, _height)
        if self.margin:
            self.size -= (self.margin[0] + self.margin[1])
        if self.padding:
            self.inner_size = self.size - (self.padding[0] + self.padding[1])
        else:
            self.inner_size = self.size

    def set_pos(self, _x: int, _y: int) -> None:
        super().set_pos(_x, _y)
        if self.margin:
            self.pos += self.margin[0]
        if self.padding:
            self.inner_pos = self.pos + self.padding[0]
        else:
            self.inner_pos = self.pos

    def set_margin(self, left: int, right: int, bottom: int, top: int):
        self.margin = (
            Vector((left, bottom)),
            Vector((right, top))
        )

    def set_unified_margin(self, margin: int):
        self.margin = (
            Vector((margin, margin)),
            Vector((margin, margin))
        )

    def set_padding(self, left: int, right: int, bottom: int, top: int):
        self.padding = (
            Vector((left, bottom)),
            Vector((right, top))
        )

    def set_unified_padding(self, padding: int):
        self.padding = (
            Vector((padding, padding)),
            Vector((padding, padding))
        )

    def get_inner_pos_size(self) -> (Vector, Vector):
        return self.inner_pos, self.inner_size

class TsformAdvancedAnch(TsformAdvanced, TsformAnch):
    def set_margin(self, left: int, right: int, bottom: int, top: int):
        super().set_margin(left, right, bottom, top)
        self.update()

    def set_unified_margin(self, margin: int):
        super().set_unified_margin(padding)
        self.update()
        return self

    def set_padding(self, left: int, right: int, bottom: int, top: int):
        super().set_padding(left, right, bottom, top)
        self.update()

    def set_unified_padding(self, padding: int):
        super().set_unified_padding(padding)
        self.update()
        return self

class TsformAnchFixedTopBottom(TsformAnchFixed):
    def update(self) -> None:
        super().update()
        self.pos -= self.size

class DynTsformAnchFixedTopBottom(TsformAnchFixedTopBottom):
    def update(self) -> None:
        super().update()
        if self.pos.x + self.size.x > self.parent.pos.x + self.parent.size.x:
            diff = (self.pos.x + self.size.x) - (self.parent.pos.x + self.parent.size.x)
            self.parent.size.x += diff
        if self.pos.y < self.parent.pos.y:
            diff = self.parent.pos.y - self.pos.y
            self.parent.pos.y = self.pos.y
            self.parent.size.y += diff
