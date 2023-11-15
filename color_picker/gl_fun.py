# ALERT! DEPRECATED!
from gpu import state
from blf import *
from gpu_extras.batch import batch_for_shader as bat
from . gpu_sh import ShaderType as SType, ShaderGeom as SGeom
def SetPoint(ps):state.point_size_set(ps)
def RstPoint():state.point_size_set(4.0)
def SetPointBlend(ps):state.point_size_set(ps);SetBlend()
def RstPointBlend():state.point_size_set(4.0);RstBlend()
def SetLineSBlend(lt):SetBlend();state.line_width_set(lt)
def RstLineSBlend():RstBlend();state.line_width_set(1.0)
def SetBlend():state.blend_set('ALPHA')
def RstBlend():state.blend_set('NONE')
def SetFontColor(id,co=(1,1,1,1)):color(id,*co)
def GetFontDim(id,_txt)->tuple:return dimensions(id,_txt)
def SetFontShadow(id,off_x=-1,off_y=-2,lvl=3,co=(0,0,0,1)):enable(id,SHADOW);shadow(id,lvl,*co);shadow_offset(id,off_x,off_y)
def RstFontShadow(id):disable(id,SHADOW)
def SetFontWW(id,width):enable(id,WORD_WRAP);word_wrap(id,width)
def RstFontWW(id):disable(id,WORD_WRAP)
def SetFontClip(id,xi,xf,yi,yf):enable(id,CLIPPING);clipping(id,xi,xf,yi,yf)
def RstFontCLip(id):disable(id,CLIPPING)
def SetFontRot(id,a):enable(id,ROTATION);rotation(id,a)
def RstFontRot(id):disable(id,ROTATION)
def SetFontSize(id,_size):size(id,_size)
def SetFontSizeGetDim(id,_size,_txt)->tuple:SetFontSize(id,_size);return GetFontDim(id,_txt)
def DrawBlend(b, s):SetBlend();b.draw(s);RstBlend()
def Draw(b, s):b.draw(s)
def Bind(s):s.bind()
def SetFloat(s,a,b):s.uniform_float(a, b)
def SetFloats(sh,**kwargs):
    for a,b in kwargs.items():
        SetFloat(sh, a, b)
def SetV4(s,a,b):s.uniform_float(a, b)
def SetV4s(sh,**kwargs):
    for a,b in kwargs.items():
        SetV4(sh, a, b)
def BindSetSingleFloat(s,a,b):Bind(s);SetFloat(s, a, b)
def NewGeoBat(s,g,i):return bat(s,SType.TRIS(),g,indices=i)
def NewImBat(i,s,g):BindTex(s,i); return bat(s,SType.TRIFAN(),g)
def NewPrimilineBat(s,g):return bat(s,SType.LINES(),g)
def NewDotBat(c,s):return bat(s,SType.POINTS(),SGeom.CIR(c))
def DrawBlendDot(r,b,s):SetPointBlend(r*2);Draw(b,s);RstPointBlend()
def BindTex(s,i): s.uniform_sample('texture', i)
def DrawTxt(id,_x,_y,_txt):position(id,_x,_y,0);draw(id,_txt)
def DrawSRGB(b,s):Draw(b,s)
def DrawBlendDotSRGB(_c,_r,s):SetPointBlend(_r*2);DrawSRGB(NewDotBat(_c,s),s);RstPointBlend()