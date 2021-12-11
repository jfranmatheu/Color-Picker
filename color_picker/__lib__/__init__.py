
# ATTENTION!! DEPRECATED!!!!!!
from ..import __package__ as __main__
from enum import Enum
from mathutils import Vector
shader_2d_area_border_frag = '''
uniform vec4 color;
uniform float scale;

in vec2 uv;

out vec4 fragColor;

void main()
{
  /* Should be 0.8 but minimize the AA on the edges. */
  float dist = (length(uv) - 0.78) * scale;

  fragColor = color;
  fragColor.a *= smoothstep(-0.09, 1.09, dist);
}
'''
shader_2d_area_border_vert = '''
uniform mat4 ModelViewProjectionMatrix;

uniform vec4 rect;
uniform int cornerLen;
uniform float scale;

in vec2 pos;

out vec2 uv;

void main()
{
  int corner_id = (gl_VertexID / cornerLen) % 4;

  vec2 final_pos = pos * scale;

  if (corner_id == 0) {
    uv = pos + vec2(1.0, 1.0);
    final_pos += rect.yw; /* top right */
  }
  else if (corner_id == 1) {
    uv = pos + vec2(-1.0, 1.0);
    final_pos += rect.xw; /* top left */
  }
  else if (corner_id == 2) {
    uv = pos + vec2(-1.0, -1.0);
    final_pos += rect.xz; /* bottom left */
  }
  else {
    uv = pos + vec2(1.0, -1.0);
    final_pos += rect.yz; /* bottom right */
  }

  gl_Position = (ModelViewProjectionMatrix * vec4(final_pos, 0.0, 1.0));
}

'''
shader_2d_flat_color_vert = '''
uniform mat4 ModelViewProjectionMatrix;

in vec2 pos;
in vec4 color;

flat out vec4 finalColor;

void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
  finalColor = color;
}

'''
shader_2d_image_rect_vert = '''
/**
 * Simple shader that just draw one icon at the specified location
 * does not need any vertex input (producing less call to immBegin/End)
 */

uniform mat4 ModelViewProjectionMatrix;
uniform vec4 rect_icon;
uniform vec4 rect_geom;

out vec2 texCoord_interp;

void main()
{
  vec2 uv;
  vec2 co;
  if (gl_VertexID == 0) {
    co = rect_geom.xw;
    uv = rect_icon.xw;
  }
  else if (gl_VertexID == 1) {
    co = rect_geom.xy;
    uv = rect_icon.xy;
  }
  else if (gl_VertexID == 2) {
    co = rect_geom.zw;
    uv = rect_icon.zw;
  }
  else {
    co = rect_geom.zy;
    uv = rect_icon.zy;
  }

  gl_Position = ModelViewProjectionMatrix * vec4(co, 0.0f, 1.0f);
  texCoord_interp = uv;
}
'''
shader_2d_image_vert = '''
uniform mat4 ModelViewProjectionMatrix;

/* Keep in sync with intern/opencolorio/gpu_shader_display_transform_vertex.glsl */
in vec2 texCoord;
in vec2 pos;
out vec2 texCoord_interp;

void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(pos.xy, 0.0f, 1.0f);
  gl_Position.z = 1.0;
  texCoord_interp = texCoord;
}

'''
shader_2d_point_uniform_size_aa_vert = '''
uniform mat4 ModelViewProjectionMatrix;
uniform float size;

in vec2 pos;
out vec2 radii;

void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
  gl_PointSize = size;

  // calculate concentric radii in pixels
  float radius = 0.5 * size;

  // start at the outside and progress toward the center
  radii[0] = radius;
  radii[1] = radius - 1.0;

  // convert to PointCoord units
  radii /= size;
}

'''
shader_2d_point_uniform_size_outline_aa_vert = '''
uniform mat4 ModelViewProjectionMatrix;
uniform float size;
uniform float outlineWidth;

in vec2 pos;
out vec4 radii;

void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
  gl_PointSize = size;

  // calculate concentric radii in pixels
  float radius = 0.5 * size;

  // start at the outside and progress toward the center
  radii[0] = radius;
  radii[1] = radius - 1.0;
  radii[2] = radius - outlineWidth;
  radii[3] = radius - outlineWidth - 1.0;

  // convert to PointCoord units
  radii /= size;
}

'''
shader_2d_smooth_color_frag = '''
noperspective in vec4 finalColor;
out vec4 fragColor;

void main()
{
  fragColor = finalColor;
  fragColor = blender_srgb_to_framebuffer_space(fragColor);
}

'''
shader_2d_smooth_color_vert = '''
uniform mat4 ModelViewProjectionMatrix;

in vec2 pos;
in vec4 color;

noperspective out vec4 finalColor;

void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
  finalColor = color;
}
'''
shader_2d_vert = '''
uniform mat4 ModelViewProjectionMatrix;

#ifdef UV_POS
in vec2 u;
#  define pos u
#else
in vec2 pos;
#endif

void main()
{
  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
}
'''
shader_2d_teg_base_frag = '''
uniform vec3 checkerColorAndSize;

noperspective in vec2 uvInterp;
noperspective in float butCo;
flat in float discardFac;
flat in float shadeTri;
flat in vec2 outRectSize;
flat in vec4 outRoundCorners;
noperspective in vec4 innerColor;
flat in vec4 borderColor;
flat in vec4 embossColor;
flat in float lineWidth;

out vec4 fragColor;

vec3 compute_masks(vec2 uv)
{
  bool upper_half = uv.y > outRectSize.y * 0.5;
  bool right_half = uv.x > outRectSize.x * 0.5;
  float corner_rad;

  /* Correct aspect ratio for 2D views not using uniform scalling.
   * uv is already in pixel space so a uniform scale should give us a ratio of 1. */
  float ratio = (butCo != -2.0) ? (dFdy(uv.y) / dFdx(uv.x)) : 1.0;
  vec2 uv_sdf = uv;
  uv_sdf.x *= ratio;

  if (right_half) {
    uv_sdf.x = outRectSize.x * ratio - uv_sdf.x;
  }
  if (upper_half) {
    uv_sdf.y = outRectSize.y - uv_sdf.y;
    corner_rad = right_half ? outRoundCorners.z : outRoundCorners.w;
  }
  else {
    corner_rad = right_half ? outRoundCorners.y : outRoundCorners.x;
  }

  /* Signed distance field from the corner (in pixel).
   * inner_sdf is sharp and outer_sdf is rounded. */
  uv_sdf -= corner_rad;
  float inner_sdf = max(0.0, min(uv_sdf.x, uv_sdf.y));
  float outer_sdf = -length(min(uv_sdf, 0.0));
  float sdf = inner_sdf + outer_sdf + corner_rad;

  /* Fade emboss at the border. */
  float emboss_size = clamp((upper_half) ? 0.0 : (uv.x / corner_rad), 0.0, 1.0);

  /* Clamp line width to be at least 1px wide. This can happen if the projection matrix
   * has been scaled (i.e: Node editor)... */
  float line_width = (lineWidth > 0.0) ? max(fwidth(uv.y), lineWidth) : 0.0;

  const float aa_radius = 0.5;
  vec3 masks;
  masks.x = smoothstep(-aa_radius, aa_radius, sdf);
  masks.y = smoothstep(-aa_radius, aa_radius, sdf - line_width);
  masks.z = smoothstep(-aa_radius, aa_radius, sdf + line_width * emboss_size);

  /* Compose masks together to avoid having too much alpha. */
  masks.zx = max(vec2(0.0), masks.zx - masks.xy);

  return masks;
}

vec4 do_checkerboard()
{
  float size = checkerColorAndSize.z;
  vec2 phase = mod(gl_FragCoord.xy, size * 2.0);

  if ((phase.x > size && phase.y < size) || (phase.x < size && phase.y > size)) {
    return vec4(checkerColorAndSize.xxx, 1.0);
  }
  else {
    return vec4(checkerColorAndSize.yyy, 1.0);
  }
}

void main()
{
  if (min(1.0, -butCo) > discardFac) {
    discard;
  }

  vec3 masks = compute_masks(uvInterp);

  if (butCo > 0.0) {
    /* Alpha checker teg. */
    if (butCo > 0.5) {
      vec4 checker = do_checkerboard();
      fragColor = mix(checker, innerColor, innerColor.a);
    }
    else {
      /* Set alpha to 1.0. */
      fragColor = innerColor;
    }
    fragColor.a = 1.0;
  }
  else {
    /* Premultiply here. */
    fragColor = innerColor * vec4(innerColor.aaa, 1.0);
  }
  fragColor *= masks.y;
  fragColor += masks.x * borderColor;
  fragColor += masks.z * embossColor;

  /* Un-premult because the blend equation is already doing the mult. */
  if (fragColor.a > 0.0) {
    fragColor.rgb /= fragColor.a;
  }

  fragColor = blender_srgb_to_framebuffer_space(fragColor);
}
'''
shader_2d_teg_base_vert = '''

uniform mat4 ModelViewProjectionMatrix;

#define MAX_PARAM 12
#ifdef USE_INSTANCE
#  define MAX_INSTANCE 6
uniform vec4 parameters[MAX_PARAM * MAX_INSTANCE];
#else
uniform vec4 parameters[MAX_PARAM];
#endif

/* gl_InstanceID is supposed to be 0 if not drawing instances, but this seems
 * to be violated in some drivers. For example, macOS 10.15.4 and Intel Iris
 * causes T78307 when using gl_InstanceID outside of instance. */
#ifdef USE_INSTANCE
#  define tegID gl_InstanceID
#else
#  define tegID 0
#endif

#define recti parameters[tegID * MAX_PARAM + 0]
#define rect parameters[tegID * MAX_PARAM + 1]
#define radsi parameters[tegID * MAX_PARAM + 2].x
#define rads parameters[tegID * MAX_PARAM + 2].y
#define faci parameters[tegID * MAX_PARAM + 2].zw
#define roundCorners parameters[tegID * MAX_PARAM + 3]
#define colorInner1 parameters[tegID * MAX_PARAM + 4]
#define colorInner2 parameters[tegID * MAX_PARAM + 5]
#define colorEdge parameters[tegID * MAX_PARAM + 6]
#define colorEmboss parameters[tegID * MAX_PARAM + 7]
#define colorTria parameters[tegID * MAX_PARAM + 8]
#define tria1Center parameters[tegID * MAX_PARAM + 9].xy
#define tria2Center parameters[tegID * MAX_PARAM + 9].zw
#define tria1Size parameters[tegID * MAX_PARAM + 10].x
#define tria2Size parameters[tegID * MAX_PARAM + 10].y
#define shadeDir parameters[tegID * MAX_PARAM + 10].z
#define alphaDiscard parameters[tegID * MAX_PARAM + 10].w
#define triaType parameters[tegID * MAX_PARAM + 11].x

/* We encode alpha check and discard factor together. */
#define doAlphaCheck (alphaDiscard < 0.0)
#define discardFactor abs(alphaDiscard)

noperspective out vec2 uvInterp;
flat out vec2 outRectSize;
flat out vec4 outRoundCorners;
noperspective out vec4 innerColor;
flat out vec4 borderColor;
flat out vec4 embossColor;
flat out float lineWidth;
noperspective out float butCo;
flat out float discardFac;

#ifdef OS_MAC
in float dummy;
#endif

vec2 do_teg(void)
{
  lineWidth = abs(rect.x - recti.x);
  vec2 emboss_ofs = vec2(0.0, -lineWidth);
  vec2 v_pos[4] = vec2[4](rect.xz + emboss_ofs, rect.xw, rect.yz + emboss_ofs, rect.yw);
  vec2 pos = v_pos[gl_VertexID];

  uvInterp = pos - rect.xz;
  outRectSize = rect.yw - rect.xz;
  outRoundCorners = rads * roundCorners;

  vec2 uv = uvInterp / outRectSize;
  float fac = clamp((shadeDir > 0.0) ? uv.y : uv.x, 0.0, 1.0);
  /* Note innerColor is premultiplied inside the fragment shader. */
  if (doAlphaCheck) {
    innerColor = colorInner1;
    butCo = uv.x;
  }
  else {
    innerColor = mix(colorInner2, colorInner1, fac);
    butCo = -abs(uv.x);
  }

  /* We need premultiplied color for transparency. */
  borderColor = colorEdge * vec4(colorEdge.aaa, 1.0);
  embossColor = colorEmboss * vec4(colorEmboss.aaa, 1.0);

  return pos;
}

vec2 do_tria()
{
  int vidx = gl_VertexID % 4;
  bool tria2 = gl_VertexID > 7;

  vec2 pos;
  float size = (tria2) ? -tria2Size : tria1Size;
  vec2 center = (tria2) ? tria2Center : tria1Center;

  vec2 arrow_pos[4] = vec2[4](vec2(0.0, 0.6), vec2(0.6, 0.0), vec2(-0.6, 0.0), vec2(0.0, -0.6));
  /* Rotated uv space by 45deg and mirrored. */
  vec2 arrow_uvs[4] = vec2[4](vec2(0.0, 0.85), vec2(0.85, 0.85), vec2(0.0, 0.0), vec2(0.0, 0.85));

  vec2 point_pos[4] = vec2[4](vec2(-1.0, -1.0), vec2(-1.0, 1.0), vec2(1.0, -1.0), vec2(1.0, 1.0));
  vec2 point_uvs[4] = vec2[4](vec2(0.0, 0.0), vec2(0.0, 1.0), vec2(1.0, 0.0), vec2(1.0, 1.0));

  /* We reuse the SDF roundbox rendering of teg to render the tria shapes.
   * This means we do clever tricks to position the rectangle the way we want using
   * the 2 triangles uvs. */
  if (triaType == 0.0) {
    /* ROUNDBOX_TRIA_NONE */
    outRectSize = uvInterp = pos = vec2(0);
    outRoundCorners = vec4(0.01);
  }
  else if (triaType == 1.0) {
    /* ROUNDBOX_TRIA_ARROWS */
    pos = arrow_pos[vidx];
    uvInterp = arrow_uvs[vidx];
    uvInterp -= vec2(0.05, 0.63); /* Translate */
    outRectSize = vec2(0.74, 0.17);
    outRoundCorners = vec4(0.08);
  }
  else if (triaType == 2.0) {
    /* ROUNDBOX_TRIA_SCROLL */
    pos = point_pos[vidx];
    uvInterp = point_uvs[vidx];
    outRectSize = vec2(1.0);
    outRoundCorners = vec4(0.5);
  }
  else if (triaType == 3.0) {
    /* ROUNDBOX_TRIA_MENU */
    pos = tria2 ? vec2(0.0) : arrow_pos[vidx]; /* Solo tria */
    pos = vec2(pos.y, -pos.x);                 /* Rotate */
    pos += vec2(-0.05, 0.0);                   /* Translate */
    size *= 0.8;                               /* Scale */
    uvInterp = arrow_uvs[vidx];
    uvInterp -= vec2(0.05, 0.63); /* Translate */
    outRectSize = vec2(0.74, 0.17);
    outRoundCorners = vec4(0.01);
  }
  else if (triaType == 4.0) {
    /* ROUNDBOX_TRIA_CHECK */
    /* A bit more hacky: We use the two trias joined together to render
     * both sides of the checkmark with different length. */
    pos = arrow_pos[min(vidx, 2)];                                    /* Only keep 1 triangle. */
    pos.y = tria2 ? -pos.y : pos.y;                                   /* Mirror along X */
    pos = pos.x * vec2(0.0872, -0.996) + pos.y * vec2(0.996, 0.0872); /* Rotate (85deg) */
    pos += vec2(-0.1, 0.2);                                           /* Translate */
    center = tria1Center;
    size = tria1Size * 1.7; /* Scale */
    uvInterp = arrow_uvs[vidx];
    uvInterp -= tria2 ? vec2(0.4, 0.65) : vec2(0.08, 0.65); /* Translate */
    outRectSize = vec2(0.74, 0.14);
    outRoundCorners = vec4(0.01);
  }
  else {
    /* ROUNDBOX_TRIA_HOLD_ACTION_ARROW */
    /* We use a single triangle to cut the round rect in half. The edge will not be Antialiased. */
    pos = tria2 ? vec2(0.0) : arrow_pos[min(vidx, 2)];              /* Only keep 1 triangle. */
    pos = pos.x * vec2(0.707, 0.707) + pos.y * vec2(-0.707, 0.707); /* Rotate (45deg) */
    pos += vec2(-1.7, 2.4); /* Translate  (hardcoded, might want to remove) */
    size *= 0.4;            /* Scale */
    uvInterp = arrow_uvs[vidx];
    uvInterp -= vec2(0.05, 0.05); /* Translate */
    outRectSize = vec2(0.75);
    outRoundCorners = vec4(0.01);
  }

  uvInterp *= abs(size);
  outRectSize *= abs(size);
  outRoundCorners *= abs(size);

  pos = pos * size + center;

  innerColor = colorTria * vec4(colorTria.aaa, 1.0);

  lineWidth = 0.0;
  borderColor = vec4(0.0);
  embossColor = vec4(0.0);

  butCo = -2.0;

  return pos;
}

void main()
{
  discardFac = discardFactor;
  bool is_tria = (gl_VertexID > 3);
  vec2 pos = (is_tria) ? do_tria() : do_teg();

  gl_Position = ModelViewProjectionMatrix * vec4(pos, 0.0, 1.0);
}
'''
shader_2d_teg_shadow_frag = '''
in float shadowFalloff;

out vec4 fragColor;

uniform float alpha;

void main()
{
  fragColor = vec4(0.0);
  /* Manual curve fit of the falloff curve of previous drawing method. */
  fragColor.a = alpha * (shadowFalloff * shadowFalloff * 0.722 + shadowFalloff * 0.277);
}
'''
shader_2d_teg_shadow_vert = '''
#define BIT_RANGE(x) uint((1 << x) - 1)

/* 2 bits for corner */
/* Attention! Not the same order as in UI_interface.h!
 * Ordered by drawing order. */
#define BOTTOM_LEFT 0u
#define BOTTOM_RIGHT 1u
#define TOP_RIGHT 2u
#define TOP_LEFT 3u
#define CNR_FLAG_RANGE BIT_RANGE(2)

/* 4bits for corner id */
#define CORNER_VEC_OFS 2u
#define CORNER_VEC_RANGE BIT_RANGE(4)
const vec2 cornervec[36] = vec2[36](vec2(0.0, 1.0),
                                    vec2(0.02, 0.805),
                                    vec2(0.067, 0.617),
                                    vec2(0.169, 0.45),
                                    vec2(0.293, 0.293),
                                    vec2(0.45, 0.169),
                                    vec2(0.617, 0.076),
                                    vec2(0.805, 0.02),
                                    vec2(1.0, 0.0),
                                    vec2(-1.0, 0.0),
                                    vec2(-0.805, 0.02),
                                    vec2(-0.617, 0.067),
                                    vec2(-0.45, 0.169),
                                    vec2(-0.293, 0.293),
                                    vec2(-0.169, 0.45),
                                    vec2(-0.076, 0.617),
                                    vec2(-0.02, 0.805),
                                    vec2(0.0, 1.0),
                                    vec2(0.0, -1.0),
                                    vec2(-0.02, -0.805),
                                    vec2(-0.067, -0.617),
                                    vec2(-0.169, -0.45),
                                    vec2(-0.293, -0.293),
                                    vec2(-0.45, -0.169),
                                    vec2(-0.617, -0.076),
                                    vec2(-0.805, -0.02),
                                    vec2(-1.0, 0.0),
                                    vec2(1.0, 0.0),
                                    vec2(0.805, -0.02),
                                    vec2(0.617, -0.067),
                                    vec2(0.45, -0.169),
                                    vec2(0.293, -0.293),
                                    vec2(0.169, -0.45),
                                    vec2(0.076, -0.617),
                                    vec2(0.02, -0.805),
                                    vec2(0.0, -1.0));

#define INNER_FLAG uint(1 << 10) /* is inner vert */

uniform mat4 ModelViewProjectionMatrix;

uniform vec4 parameters[4];
/* radi and rad per corner */
#define recti parameters[0]
#define rect parameters[1]
#define radsi parameters[2].x
#define rads parameters[2].y
#define roundCorners parameters[3]

in uint vflag;

out float shadowFalloff;

void main()
{
  uint cflag = vflag & CNR_FLAG_RANGE;
  uint vofs = (vflag >> CORNER_VEC_OFS) & CORNER_VEC_RANGE;

  vec2 v = cornervec[cflag * 9u + vofs];

  bool is_inner = (vflag & INNER_FLAG) != 0u;

  shadowFalloff = (is_inner) ? 1.0 : 0.0;

  /* Scale by corner radius */
  v *= roundCorners[cflag] * ((is_inner) ? radsi : rads);

  /* Position to corner */
  vec4 rct = (is_inner) ? recti : rect;
  if (cflag == BOTTOM_LEFT) {
    v += rct.xz;
  }
  else if (cflag == BOTTOM_RIGHT) {
    v += rct.yz;
  }
  else if (cflag == TOP_RIGHT) {
    v += rct.yw;
  }
  else /* (cflag == TOP_LEFT) */ {
    v += rct.xw;
  }

  gl_Position = ModelViewProjectionMatrix * vec4(v, 0.0, 1.0);
}
'''
shader_2d_checker_frag = '''
uniform vec4 color1;
uniform vec4 color2;
uniform int size;

out vec4 fragColor;

void main()
{
  vec2 phase = mod(gl_FragCoord.xy, (size * 2));

  if ((phase.x > size && phase.y < size) || (phase.x < size && phase.y > size)) {
    fragColor = color1;
  }
  else {
    fragColor = color2;
  }
}
'''
shader_2d_image_frag = '''
in vec2 texCoord_interp;
out vec4 fragColor;

uniform sampler2D image;

void main()
{
  fragColor = texture(image, texCoord_interp);
}
'''
if __main__ == 'color_picker':
    IMG_VS = '''
      uniform mat4 ModelViewProjectionMatrix;
      in vec2 texco;
      in vec2 p;
      out vec2 texco_interp;
      void main()
      {
gl_Position = ModelViewProjectionMatrix * vec4(p, 1.0f, 1.0f);
texco_interp = texco;
      }
  '''
    IMGA_FS = '''
      in vec2 texco_interp;
      out vec4 fragColor;
      uniform sampler2D image;
      void main()
      {
vec4 texColor = texture(image, texco_interp);
if(texColor.a < 0.05)
 discard;
fragColor = texColor;
      }
  '''
    IMGA_GAMMCORR_FS = '''
    in vec2 texco_interp;
    out vec4 fragColor;
    uniform sampler2D image;
    void main()
    {
      vec4 texColor = texture(image, texco_interp);
      if(texColor.a < 0.05)
discard;
      fragColor.rgb = pow(texColor.rgb, vec3(.454545));
      fragColor.a = texColor.a;
    }
  '''
    IMGA_GAMMA_OP = '''
    in vec2 texco_interp;
    out vec4 fragColor;
    uniform sampler2D image;
    uniform float o;
    void main()
    {
      vec4 texColor = texture(image, texco_interp);
      if(texColor.a < 0.05)
discard;
      fragColor.rgb = pow(texColor.rgb, vec3(.454545));
      fragColor.a = texColor.a * o;
    }
  '''
    IMGA_GAMMCORR_BOOST_FS = """
    in vec2 texco_interp;
    out vec4 fragColor;
    uniform sampler2D image;
    uniform float boost;
    vec3 rgb2hsv(vec3 c)
    {
      vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
      vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
      vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));
      float d = q.x - min(q.w, q.y);
      float e = 1.0e-10;
      return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
    }
    vec3 hsv2rgb(vec3 c)
    {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
    }
    void main()
    {
      vec4 texColor = texture(image, texco_interp);
      if(texColor.a < 0.05)
discard;
      texColor = vec4(pow(texColor.rgb, vec3(.454545)), texColor.a);
      texColor.rgb = rgb2hsv(texColor.rgb);
      texColor.gb *= boost;
      fragColor.rgb = hsv2rgb(texColor.rgb);
      fragColor.a = texColor.a;
    }
  """
    CF_VS = """
  uniform mat4 ModelViewProjectionMatrix;
  uniform float size;
  in vec2 p;
  void main()
  {
    gl_Position = ModelViewProjectionMatrix * vec4(p, 1.0, 1.0);
    gl_PointSize = size;
  }
  """
    SHCx494D4741 = (IMG_VS, IMGA_FS)
    SHCx494D47415F47414D434F = (IMG_VS, IMGA_GAMMCORR_FS)
    SHCx494D47415F47414D434F5F424F4F5354 = (IMG_VS, IMGA_GAMMCORR_BOOST_FS)
    SHCx494D47415F47414D4D415F4F50 = (IMG_VS, IMGA_GAMMA_OP)
    CCROMA_HS_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  #define TWO_PI 6.28318530718
  uniform float v;
  out vec4 fragColor;
  vec3 hsb2rgb(in vec3 c){
    vec3 rgb = clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),
    6.0)-3.0)-1.0,
0.0,
1.0 );
    rgb = rgb*rgb*(3.0-2.0*rgb);
    return c.z * mix( vec3(1.0), rgb, c.y); // * value; // OLD
  }
  void main()
  {
    float r = 0.0, delta = 0.0, alpha = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);
    delta = fwidth(r);
    alpha = 1.0 - smoothstep(1.0 - delta, 1.0 + delta, r);
    if (alpha < 0.08) // threshold
      discard;
    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    float angle = atan(toCenter.y,toCenter.x);
    float radius = length(toCenter)*2.0;
    vec3 co = hsb2rgb(vec3((angle/TWO_PI)+0.5, radius, v));
    fragColor.rgb = pow(co,vec3(2.2));
    fragColor.a = alpha;
  }
  """
    CRCROMA_H_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  #define TWO_PI 6.28318530718
  uniform float s;
  uniform float v;
  out vec4 fragColor;
  vec3 hsb2rgb(in vec3 c){
    vec3 rgb = clamp(abs(mod(c.x*6.0+vec3(0.0,4.0,2.0),
    6.0)-3.0)-1.0,
0.0,
1.0 );
    rgb = rgb*rgb*(3.0-2.0*rgb);
    return c.z * mix( vec3(1.0), rgb, c.y); // * value // OLD
  }
  void main()
  {
    float r1 = 1.0;
    float r2 = .5;
    float r = 0.0, delta = 0.0, alpha = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);
    delta = fwidth(r);
    alpha = 1.0 - smoothstep(1.0 - delta, 1.0 + delta, r);
    if (alpha < 0.05) // threshold
      discard;
    vec2 toCenter = vec2(0.5)-gl_PointCoord.xy;
    float angle = atan(toCenter.y,toCenter.x);
    float radius = length(toCenter)*2.0;
    if (radius < .82)
      discard;
    if (radius >= .82 && radius < .85)
      alpha = smoothstep(.82, .85, radius);
    vec3 co = hsb2rgb(vec3((angle/TWO_PI)+0.5, s, v));
    fragColor.rgb = pow(co, vec3(2.2));
    fragColor.a = alpha;
  }
  """
    RCROMA_SL_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  float PI_4 = 0.785398;
  uniform float h;
  out vec4 fragColor;
  float roundedFrame (float d, float thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
  }
  vec3 hsv2rgb(vec3 c)
  {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    //float r = 0.0;
    //vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    //r = dot(cxy, cxy);
    //float s = roundedFrame(r, 9.5);
    float factor_inc_x = gl_PointCoord.x*cos(6.3*gl_PointCoord.x) / 7 + .9;
    float S = pow(gl_PointCoord.x, factor_inc_x);
    float V = 1 - pow(gl_PointCoord.y, tan(.32*PI_4)-sin(gl_PointCoord.y)/5);
    fragColor.rgb = hsv2rgb(vec3(h, S, V));
    fragColor.a = 1.0;
  }
  """
    RCROMA_SL_LIN_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  float PI_4 = 0.785398;
  uniform float h;
  out vec4 fragColor;
  vec3 hsv2rgb(vec3 c)
  {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    float S = mix(0, 1, gl_PointCoord.x);
    float V = mix(1, 0, gl_PointCoord.y);
    fragColor.rgb = pow(hsv2rgb(vec3(h, S, V)), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    RCROMA_SL_NOLIN_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform float h;
  out vec4 fragColor;
  vec3 hsv2rgb(vec3 c)
  {
    vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
    vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
    return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    float S = pow(mix(0, 1, gl_PointCoord.x), .45454545454);// * 0.963; // 0.0001
    float V = pow(mix(1, 0, gl_PointCoord.y), 2.2);// * 0.9924; // 0.0001
    fragColor.rgb = hsv2rgb(vec3(h, S, V));
    fragColor.a = 1.0;
  }
  """
    RCROMA_SL_LIN_SLICE_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  float PI_4 = 0.785398;
  uniform float h;
  uniform float xi;
  uniform float xf;
  uniform float yi;
  uniform float yf;
  out vec4 fragColor;
  vec3 hsv2rgb(vec3 c)
  {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    float S = mix(xi, xf, gl_PointCoord.x);
    float V = mix(yi, yf, gl_PointCoord.y);
    fragColor.rgb = pow(hsv2rgb(vec3(h, S, V)), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    BARCROMA_H_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform float f;
  uniform float s;
  uniform float v;
  out vec4 fragColor;
  vec3 hsv2rgb(vec3 c)
  {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    fragColor.rgb = pow(hsv2rgb(vec3(gl_PointCoord.x, s, v)), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    BARCROMA_S_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform float f;
  uniform float h;
  uniform float v;
  out vec4 fragColor;
  vec3 hsv2rgb(vec3 c)
  {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    fragColor.rgb = pow(hsv2rgb(vec3(h, gl_PointCoord.x, v)), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    BARCROMA_V_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform float f;
  uniform float h;
  uniform float s;
  //uniform vec3 co;
  out vec4 fragColor;
  vec3 hsv2rgb(vec3 c)
  {
      vec4 K = vec4(1.0, 2.0 / 3.0, 1.0 / 3.0, 3.0);
      vec3 p = abs(fract(c.xxx + K.xyz) * 6.0 - K.www);
      return c.z * mix(K.xxx, clamp(p - K.xxx, 0.0, 1.0), c.y);
  }
  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    // Should be white at left when saturation is 0, then lerp with color
    fragColor.rgb = pow(mix(vec3(0, 0, 0), hsv2rgb(vec3(h, s, 1)), gl_PointCoord.x), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    SHCx4343524F4D415F48 = (CF_VS, CRCROMA_H_FS)
    SHCx4343524F4D415F4853 = (CF_VS, CCROMA_HS_FS)
    SHCx4343524F4D415F534C = (CF_VS, RCROMA_SL_FS)
    SHCx42415243524f4d415f48 = (CF_VS, BARCROMA_H_FS)
    SHCx42415243524f4d415f53 = (CF_VS, BARCROMA_S_FS)
    SHCx42415243524f4d415f56 = (CF_VS, BARCROMA_V_FS)
    SHCx5243524f4d415f534c5f4c494e = (CF_VS, RCROMA_SL_LIN_FS)
    SHCx5243524f4d415f534c5f4e4f4c494e = (CF_VS, RCROMA_SL_NOLIN_FS)
    SHCx5243524f4d41534c4c494e534c494345 = (CF_VS, RCROMA_SL_LIN_SLICE_FS)
    CFS2_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform vec4 co;
  float roundedFrame (float d, float thickness)
  {
    return smoothstep(0.55, 0.45, abs(d / thickness) * 5.0);
  }
  out vec4 fragColor;
  void main()
  {
    float r = 0.0;
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    r = dot(cxy, cxy);
    float s = roundedFrame(r, 9.5);
    if (s < 0.05)
      discard;
    fragColor = co;
    fragColor.a *= s;
  }
  """
    SHCx434653 = (CF_VS, CFS2_FS)
    RCTGRAD_LIN_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform vec4 co1;
  uniform vec4 co2;
  uniform float dir;
  out vec4 fragColor;
  void main()
  {
    if (dir == 0)
      fragColor = pow(mix(co1, co2, gl_PointCoord.x), vec4(2.2));
    else
      fragColor = pow(mix(co1, co2, gl_PointCoord.y), vec4(2.2));
  }
  """
    RCTGRAD_NOLIN_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform vec4 co1;
  uniform vec4 co2;
  uniform float dir;
  out vec4 fragColor;

  void main()
  {
    //vec4 c1 = vec4(pow(co1.r, .454545), pow(co1.g, .454545), pow(co1.b, .454545), co1.a); // vec4(pow(co1.rgb, vec3(.454545)), co1.a);
    //vec4 c2 = vec4(pow(co2.r, .454545), pow(co2.g, .454545), pow(co2.b, .454545), co2.a); // vec4(pow(co2.rgb, vec3(.454545)), co2.a);
    //if (dir == 0)
    //  fragColor = mix(c1, c2, gl_PointCoord.x);
    //else
    //  fragColor = mix(c1, c2, gl_PointCoord.y);
    if (dir == 0)
      fragColor = pow(mix(co1, co2, gl_PointCoord.x), vec4(.454545));
    else
      fragColor = pow(mix(co1, co2, gl_PointCoord.y), vec4(.454545));
  }
  """
    RCTGRADBAR_NOLIN_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform vec4 co1;
  uniform vec4 co2;
  uniform float f;
  out vec4 fragColor;

  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    fragColor = pow(mix(co1, co2, gl_PointCoord.x), vec4(.454545));
  }
  """
    RCTGRADBAR_LIN_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform vec4 co1;
  uniform vec4 co2;
  uniform vec4 co3;
  uniform float f;
  out vec4 fragColor;

  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    if (gl_PointCoord.x <= 0.5)
      fragColor = mix(co1, co2, 2 * gl_PointCoord.x);
    // x = 0.0 -> x = 0.0 -> 2 * 0.0 = 0.0
    // x = 0.5 -> x = 1.0 -> 2 * 0.5 = 1.0
    // 2 * x
    else
      fragColor = mix(co2, co3, cxy.x);
    // x = 0.5 -> x = 0.0 -> 2 * 0.5 - 1 = 0.0
    // x = 1.0 -> x = 1.0 -> 2 * 1.0 - 1 = 1.0
    // 2 * x - 1
  }
  """
    SHCx524354475241445f4c494e = (CF_VS, RCTGRAD_LIN_FS)
    SHCx524354475241445f4e4f4c494e = (CF_VS, RCTGRAD_NOLIN_FS)
    SHCx524354475241445f4e4f4c494e10 = (CF_VS, RCTGRADBAR_LIN_FS)
    SHCx524354475241445f4e4f4c494e11 = (CF_VS, RCTGRADBAR_NOLIN_FS)
    RCTDOT_MASK_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform vec4 co;
  uniform float xi;
  uniform float xf;
  uniform float yi;
  uniform float yf;
  out vec4 fragColor;
  void main()
  {
    if (gl_PointCoord.x < xi || gl_PointCoord.x > xf)
      fragColor = co;
    else if (gl_PointCoord.y < 1-yi || gl_PointCoord.y > 1-yf)
      fragColor = co;
    else
      discard;
  }
  """
    SHCx524354444f545f4d41534b = (CF_VS, RCTDOT_MASK_FS)
    BARCROMA_R_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform float f;
  uniform vec3 co;
  out vec4 fragColor;
  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    fragColor.rgb = pow(mix(vec3(0, co.g, co.b), vec3(1, co.g, co.b), gl_PointCoord.x), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    BARCROMA_G_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform float f;
  uniform vec3 co;
  out vec4 fragColor;
  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    fragColor.rgb = pow(mix(vec3(co.r, 0, co.b), vec3(co.r, 1, co.b), gl_PointCoord.x), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    BARCROMA_B_FS = """
  #ifdef GL_ES
  precision mediump float;
  #endif
  uniform float f;
  uniform vec3 co;
  out vec4 fragColor;
  void main()
  {
    vec2 cxy = 2.0 * gl_PointCoord - 1.0;
    if (cxy.y < -f || cxy.y > f)
      discard;
    fragColor.rgb = pow(mix(vec3(co.r, co.g, 0), vec3(co.r, co.g, 1), gl_PointCoord.x), vec3(2.2));
    fragColor.a = 1.0;
  }
  """
    SHCx42415243524f4d415f52 = (CF_VS, BARCROMA_R_FS)
    SHCx42415243524f4d415f47 = (CF_VS, BARCROMA_G_FS)
    SHCx42415243524f4d415f42 = (CF_VS, BARCROMA_B_FS)
    ''' SHADER GEOMETRY '''
    def get_imga_coord(): return ((0, 1), (0, 0), (1, 0), (1, 1))

    def get_imga_verts(*args):
        x, y = args[0]
        w, h = args[1]
        return [[x, y+h], [x, y], [x+w, y], [x+w, y+h]]

    def get_imga_geom(
        *args): return {"p": get_imga_verts(*args), "texco": get_imga_coord()}

    def get_img_coord(): return ((0, 0), (1, 0), (1, 1), (0, 1))

    def get_img_verts(x, y, w, h): return (
        (x, y), (x+w, y), (x+w, y+h), (x, y+h))
    def get_img_geom(
        *args): return {"pos": get_img_verts(*args[0], *args[1]), "texCoord": get_img_coord()}

    def GeoCIR(*args): return {"p": [args[0]]}
    def PtsRCT(x, y, w, h): return [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]
    def PtsRCT_(x, y, w, h): return [(x, y), (x+w, y), (x, y+h), (x+w, y+h)]

    def PtsRCTCENT(x, y, w, h): return [
        (x-w, y-h), (x+w, y-h), (x-w, y+h), (x+w, y+h)]

    def PtsRCTCENT_(x, y, w, h): return [
        (x-w, y-h), (x+w, y-h), (x-w, y+h), (x+w, y+h)]

    def Eval(p0, p1, p2, t=.5): return (1-t)**2 * \
        p0 + 2*t * (1-t) * p1 + t**2 * p2

    def PtsRCTRND(x, y, w, h, r):
        A = Eval(Vector((x, y + r)), Vector((x, y)), Vector((x + r, y)))
        B = Eval(Vector((x + w - r, y)),
                 Vector((x + w, y)), Vector((x + w, y + r)))
        C = Eval(Vector((x + w - r, y + h)),
                 Vector((x + w, y + h)), Vector((x + w, y + h - r)))
        D = Eval(Vector((x, y + h - r)),
                 Vector((x, y + h)), Vector((x + r, y + h)))
        return ((x + w / 2, y + h / 2), (x, y + r), (A[0], A[1]), (x + r, y), (x + w - r, y), (B[0], B[1]), (x + w, y + r), (x + w, y + h - r), (C[0], C[1]), (x + w - r, y + h), (x + r, y + h), (D[0], D[1]), (x, y + h - r))

    def PtsMARCORCTRND(x, y, w, h, r):
        A = Eval(Vector((x, y + r)), Vector((x, y)), Vector((x + r, y)))
        B = Eval(Vector((x + w - r, y)),
                 Vector((x + w, y)), Vector((x + w, y + r)))
        C = Eval(Vector((x + w - r, y + h)),
                 Vector((x + w, y + h)), Vector((x + w, y + h - r)))
        D = Eval(Vector((x, y + h - r)),
                 Vector((x, y + h)), Vector((x + r, y + h)))
        return ((x, y + r), (A[0], A[1]), (A[0], A[1]), (x + r, y), (x + r, y), (x + w - r, y), (x + w - r, y), (B[0], B[1]), (B[0], B[1]), (x + w, y + r), (x + w, y + r), (x + w, y + h - r), (x + w, y + h - r), (C[0], C[1]), (C[0], C[1]), (x + w - r, y + h), (x + w - r, y + h), (x + r, y + h), (x + r, y + h), (D[0], D[1]), (D[0], D[1]), (x, y + h - r), (x, y + h - r), (x, y + r))

    def PtsRCTRNDBOT(x, y, w, h, r):
        A = Eval(Vector((x, y + r)), Vector((x, y)), Vector((x + r, y)))
        B = Eval(Vector((x + w - r, y)),
                 Vector((x + w, y)), Vector((x + w, y + r)))
        return ((x, y + r), (A[0], A[1]), (x + r, y), (x + w - r, y), (B[0], B[1]), (x + w, y + r), (x + w, y + h), (x, y + h))

    def PtsRCTRNDTOP(x, y, w, h, r):
        C = Eval(Vector((x + w - r, y + h)),
                 Vector((x + w, y + h)), Vector((x + w, y + h - r)))
        D = Eval(Vector((x, y + h - r)),
                 Vector((x, y + h)), Vector((x + r, y + h)))
        return ((x+w, y+h-r), (C[0], C[1]), (x+w-r, y+h), (x+r, y+h), (D[0], D[1]), (x, y+h-r), (x, y), (x+w, y))

    def PtsMARCORCT(x, y, w, h): return [
        (x, y), (x+w, y), (x+w, y), (x+w, y+h), (x+w, y+h), (x, y+h), (x, y+h), (x, y)]
    IdxRCT = ((0, 1, 2), (2, 1, 3))
    IdxRCTRND = ((0,  1,  2), (0,  2,  3), (0,  3,  4), (0,  4,  5), (0,  5,  6), (0,  6,  7),
                 (0,  7,  8), (0,  8,  9), (0,  9, 10), (0, 10, 11), (0, 11, 12), (0, 12,  1))
    IdxRCTRNDBOT = ((3,  1,  2), (1,  3,  4), (1,  4,  5),
                    (0,  1,  5), (0,  5,  6), (0,  6,  7))
    IdxRCTRNDTOP = ((6,  7,  0), (0,  6,  5), (0,  5,  1),
                    (1,  5,  4), (4,  2,  1), (2,  4,  3))

    def GeoRCT(_o, _tam): return {"pos": PtsRCT(*_o, *_tam)}
    def GeoRCTCENT(_o, _tam): return {"pos": PtsRCTCENT(*_o, *_tam)}

    def _GeoRCT(_ox, _oy, _tamx, _tamy): return {
        "pos": PtsRCT_(_ox, _oy, _tamx, _tamy)}
    def _GeoRCTCENT(_ox, _oy, _tamx, _tamy): return {
        "pos": PtsRCTCENT_(_ox, _oy, _tamx, _tamy)}

    def GeoRCTRND(_o, _tam, _r): return {"pos": PtsRCTRND(*_o, *_tam, _r)}
    def GeoIdxRCT(): return IdxRCT
    def GeoIdxRCTRND(): return IdxRCTRND

    def GeoRCTRNDTOP(_o, _tam, _r): return {
        "pos": PtsRCTRNDTOP(*_o, *_tam, _r)}
    def GeoRCTRNDBOT(_o, _tam, _r): return {
        "pos": PtsRCTRNDBOT(*_o, *_tam, _r)}

    def GeoIdxRCTRNDTOP(): return IdxRCTRNDTOP
    def GeoIdxRCTRNDBOT(): return IdxRCTRNDBOT
    def GeoMARCORCT(_o, _tam): return {"pos": PtsMARCORCT(*_o, *_tam)}

    def GeoMARCORCTRND(_o, _tam, _r): return {
        "pos": PtsMARCORCTRND(*_o, *_tam, _r)}

    class ShaderGeom(Enum):
        IMG = get_img_geom
        IMGA = get_imga_geom
        IMG_V = get_img_verts
        IMG_TC = get_img_coord
        CIR = GeoCIR
        R_IDXS = GeoIdxRCT
        R = GeoRCT
        R_CENT = GeoRCTCENT
        _R = _GeoRCT
        _R_CENT = _GeoRCTCENT
        R3_IDXS = GeoIdxRCTRND
        MARCOR1 = GeoMARCORCT
        MARCOR3 = GeoMARCORCTRND
        R3 = GeoRCTRND
        R3TOP = GeoRCTRNDTOP
        R3BOT = GeoRCTRNDBOT
        R3TOP_IDXS = GeoIdxRCTRNDTOP
        R3BOT_IDXS = GeoIdxRCTRNDBOT

        def __call__(self, *args):
            if args:
                return self.value(*args[0])
            else:
                return self.value()
