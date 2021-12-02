from enum import Enum
from mathutils import Color as C
from colorsys import rgb_to_hsv, hsv_to_rgb


class Color(Enum):
    BLACK = (0, 0, 0),
    WHITE = (1, 1, 1),
    RED = (1, 0, 0),
    YELLOW = (1, 1, 0),
    GREEN = (0, 1, 0),
    PURPLE = (1, 0, 1),
    BLUE = (0, 0, 1),
    CYAN = (0, 1, 1),
    DEF_BLUE = (.337, .502, .761),
    DEF_BLUE_HIGHLIGHT = (.518, .722, 1),
    DEF_TEXT = (.902, .902, .902),
    
    def __call__(self):
        return C(*self.value)

def RGB(r, g, b):
    return C(r, g, b)

def RGBA(color: Color, alpha: float = 1.0) -> tuple:
    return (*color(), alpha)

def complementary_RGB(r, g, b):
   """returns RGB components of complementary color"""
   hsv = rgb_to_hsv(r, g, b)
   return hsv_to_rgb((hsv[0] + 0.5) % 1, hsv[1], hsv[2])

def complementary(co):
    return hsv_to_rgb((co.h + 0.5) % 1, co.s, co.v)

anal_factor = 30.0 / 360.0
def analogous(co):
    #h1 = ((co.h * 360 + 30) % 360) / 360
    #h2 = ((co.h * 360 - 30) % 360) / 360
    h1 = co.h - anal_factor
    if h1 > 1: h1 -= 1
    h2 = co.h + anal_factor
    if h2 > 1: h2 -= 1
    return (
        hsv_to_rgb(h1, co.s, co.s),
        hsv_to_rgb(h2, co.s, co.s)
    )

def triadic(co):
    h1 = ((co.h * 360 + 120) % 360) / 360.0
    h2 = ((co.h * 360 + 240) % 360) / 360.0
    return (
        hsv_to_rgb(h1, co.s, co.s),
        hsv_to_rgb(h2, co.s, co.s)
    )

def split_complementary(co):
    h1 = ((co.h * 360 + 150) % 360) / 360.0
    h2 = ((co.h * 360 + 210) % 360) / 360.0
    return (
        hsv_to_rgb(h1, co.s, co.s),
        hsv_to_rgb(h2, co.s, co.s)
    )

def tetradic(co):
    h1 = ((co.h * 360 + 60) % 360) / 360.0
    h2 = ((co.h * 360 + 180) % 360) / 360.0
    h3 = ((co.h * 360 + 240) % 360) / 360.0
    return (
        hsv_to_rgb(h1, co.s, co.s),
        hsv_to_rgb(h2, co.s, co.s),
        hsv_to_rgb(h3, co.s, co.s)
    )
