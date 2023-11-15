from gpu.shader import from_builtin#, code_from_builtin # NOTE: Exposes the internal shader code for query.
from gpu.types import GPUShader as Shader
from . libcode import *
from enum import Enum


class ShaderName2D(Enum):
    IMAGE   = 'IMAGE'
    UNIFORM = 'UNIFORM_COLOR'
    FLAT    = 'FLAT_COLOR'
    SMOOTH  = 'SMOOTH_COLOR'

    def __call__(self):
        return self.value

'''
NOTE:
Shaders that are embedded in the blender internal code.
They all read the uniform ‘mat4 ModelViewProjectionMatrix’, which can be edited by the ‘gpu.matrix’ module.
For more details, you can check the shader code with the function ‘gpu.shader.code_from_builtin’.

https://docs.blender.org/api/blender2.8/gpu.shader.html?highlight=builtin#gpu.shader.code_from_builtin

'''
# Shader References:
# https://docs.blender.org/api/blender2.8/gpu.html#d-image
# https://docs.blender.org/api/blender2.8/gpu.html#d-rectangle
# https://github.com/lewislepton/shadertutorialseries
# https://github.com/dfelinto/blender/tree/master/source/blender/gpu/shaders
# https://medium.com/@pythor/cool-shaders-f071a491245
shader_2d_image         = from_builtin(ShaderName2D.IMAGE())
shader_2d_color_unif    = from_builtin(ShaderName2D.UNIFORM())
shader_2d_color_flat    = from_builtin(ShaderName2D.FLAT())
shader_2d_color_smooth  = from_builtin(ShaderName2D.SMOOTH())

class Shader2D(Enum):
    IMAGE   = shader_2d_image
    UNIFORM = shader_2d_color_unif
    FLAT    = shader_2d_color_flat
    SMOOTH  = shader_2d_color_smooth

    def __call__(self):
        return self.value

class ShaderName3D(Enum):
    UNIFORM = 'UNIFORM_COLOR'
    FLAT    = 'FLAT_COLOR'
    SMOOTH  = 'SMOOTH_COLOR'

    def __call__(self):
        return self.value
from .__lib__ import *
shader_3d_color_unif    = from_builtin(ShaderName3D.UNIFORM())
shader_3d_color_flat    = from_builtin(ShaderName3D.FLAT())
shader_3d_color_smooth  = from_builtin(ShaderName3D.SMOOTH())

class Shader3D(Enum):
    UNIFORM = shader_3d_color_unif
    FLAT    = shader_3d_color_flat
    SMOOTH  = shader_3d_color_smooth

    def __call__(self):
        return self.value

class ShaderType(Enum):
    POINTS      = "POINTS"
    LINES       = "LINES"
    TRIS        = "TRIS"
    LINES_ADJ   = "LINES_ADJ"
    TRIFAN      = "TRI_FAN"

    def __call__(self):
        return self.value

def ShaderLib(shc, lib):
    return Shader(*shc, libcode=lib)

# TODO: Make it beautiful, PLEASE...
class SH(Enum):
    # PLIGHT = Shader(*SHCx504C49474854)
    # CFS_CROPTOP = Shader(*SHCx4346535F43524F50544F50)
    # CFS_CROPBOT = Shader(*SHCx4346535F43524F50424F54)
    IMGA = Shader(*SHCx494D4741) # see image.py for reference.
    IMGA_GAMMA = Shader(*SHCx494D47415F47414D434F) # same as above but with some pow for gamma correcting.
    IMGA_GAMMA_INTENSIFY = Shader(*SHCx494D47415F47414D434F5F424F4F5354) # same as above but multiplied values to make it brighter.
    # RNGS_SPLITANG = Shader(*SHCx524E47535F53504C4954414E47)
    # RNGBLR = Shader(*SHCx524E47424C52)
    IMGA_GAMMA_OP = Shader(*SHCx494D47415F47414D4D415F4F50) # same as IMGA_GAMMA but multiplied alpha.
    # IMGA_LINE = Shader(*SHCx494D47415F4C494E45)
    BARCROMA_H = Shader(*SHCx42415243524f4d415f48)
    RCROMA_SL = Shader(*SHCx4343524F4D415F534C)
    RCROMA_SL_LIN = Shader(*SHCx5243524f4d415f534c5f4c494e)
    CCROMA_HS = Shader(*SHCx4343524F4D415F4853)
    BARCROMA_V = Shader(*SHCx42415243524f4d415f56)
    BARCROMA_G = Shader(*SHCx42415243524f4d415f47)
    CRCROMA_H = Shader(*SHCx4343524F4D415F48)
    CFS = Shader(*SHCx434653)
    BARCROMA_S = Shader(*SHCx42415243524f4d415f53)
    BARCROMA_R = Shader(*SHCx42415243524f4d415f52)
    RCROMA_SL_NOLIN = Shader(*SHCx5243524f4d415f534c5f4e4f4c494e)
    RCTGRAD_LIN = Shader(*SHCx524354475241445f4c494e)
    RCTGRAD_NOLIN = Shader(*SHCx524354475241445f4e4f4c494e)
    RCTGRADBAR_LIN = Shader(*SHCx524354475241445f4e4f4c494e10)
    RCTGRADBAR_NOLIN = Shader(*SHCx524354475241445f4e4f4c494e11)
    RCROMA_SL_LIN_SLICE = Shader(*SHCx5243524f4d41534c4c494e534c494345)
    RCTDOT_MASK = Shader(*SHCx524354444f545f4d41534b)
    BARCROMA_B = Shader(*SHCx42415243524f4d415f42)
    
    def __call__(self):
        return self.value
