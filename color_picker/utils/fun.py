from math import pi, sin, asin, cos, radians, atan2, hypot, acos, sqrt
from mathutils import Vector
from os.path import realpath, relpath, abspath, join, basename, dirname, exists, isfile


def dotproduct(v1, v2):
  return sum((a*b) for a, b in zip(v1, v2))

def length(v):
  return sqrt(dotproduct(v, v))

def angle(v1, v2):
  return acos(dotproduct(v1, v2) / (length(v1) * length(v2)))

def distance_between(_p1, _p2):
    return hypot(_p1[0] - _p2[0], _p1[1] - _p2[1])
    #return math.sqrt((_p1[1] - _p1[0])**2 + (_p2[1] - _p2[0])**2)

def direction_from_to(_p1, _p2, _norm=True):
    if _norm:
        return (_p1 - _p2).normalized()
    else:
        return _p1 - _p2

def point_inside_circle(_p, _c, _r):
    return distance_between(_p, _c) < _r

def point_inside_rect(_p, _pos, _size):
    return ((_pos[0] + _size[0]) > _p[0] > _pos[0]) and ((_pos[1] + _size[1]) > _p[1] > _pos[1])

def clear_image(image):
    image.gl_free()  # free opengl image memory
    image.buffers_free()
    image.user_clear()

def remove_image(image):
    # delete image
    # print(image)
    bpy.data.images.remove(image, do_unlink=True, do_id_user=True, do_ui_user=True)

def load_image(image_name, ext='.png', from_path="images"):
    path = join(dirname(__file__), from_path, image_name+ext)
    if not isfile(path):
        return None
    return bpy.data.images.load(path, check_existing=True)

def load_image_from_file_dir(file, image_name, ext='.png', from_path="images"):
    path = join(dirname(file), from_path, image_name+ext)
    if not isfile(path):
        return None
    return bpy.data.images.load(path, check_existing=True)

def load_image_from_filepath(filepath):
    if not isfile(filepath):
        return None
    return bpy.data.images.load(filepath, check_existing=True)

def swap(a, b):
    temp = a
    a = b
    b = a
    return a, b

def lerp(start, end, t):
    return start * (1-t) + end * t

def clamp(min_value, max_value, value):
    return max(min(value, max_value), min_value)

def point_inside_ring(_p, _c, _r1, _r2):
    d = distance_between(_p, _c)
    return d > _r1 and d < _r2

def rotate(o, p, a):
    qx = o.x + cos(a) * (p.x - o.x) - sin(a) * (p.y - o.y)
    qy = o.y + sin(a) * (p.x - o.x) + cos(a) * (p.y - o.y)
    return Vector((qx, qy))

def fit_rect_rect(outer, inner):
    w1, h1 = outer
    w2, h2 = inner
    vert_scale = h2/h1
    horiz_scale = w2/w1
    scale = min(horiz_scale, vert_scale)
    return Vector((scale * h1, scale * w1))

def fit_rect(w1, h1, w2, h2):
    vert_scale = h2/h1
    horiz_scale = w2/w1
    scale = min(horiz_scale, vert_scale)
    return Vector((scale * h1, scale * w1))
