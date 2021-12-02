K = 1 / 2.4
'''
//X, Y and Z input refer to a D65/2° standard illuminant.
//sR, sG and sB (standard RGB) output range = 0 ÷ 255

var_X = X / 100
var_Y = Y / 100
var_Z = Z / 100

var_R = var_X *  3.2406 + var_Y * -1.5372 + var_Z * -0.4986
var_G = var_X * -0.9689 + var_Y *  1.8758 + var_Z *  0.0415
var_B = var_X *  0.0557 + var_Y * -0.2040 + var_Z *  1.0570

if ( var_R > 0.0031308 ) var_R = 1.055 * ( var_R ^ ( 1 / 2.4 ) ) - 0.055
else                     var_R = 12.92 * var_R
if ( var_G > 0.0031308 ) var_G = 1.055 * ( var_G ^ ( 1 / 2.4 ) ) - 0.055
else                     var_G = 12.92 * var_G
if ( var_B > 0.0031308 ) var_B = 1.055 * ( var_B ^ ( 1 / 2.4 ) ) - 0.055
else                     var_B = 12.92 * var_B

sR = var_R * 255
sG = var_G * 255
sB = var_B * 255
'''

def xyz2srgb_255(X, Y, Z):
    """ X, Y and Z input refer to a D65/2° standard illuminant.
        sR, sG and sB (standard RGB) output range = 0 ÷ 255
    """
    var_X = X / 100
    var_Y = Y / 100
    var_Z = Z / 100

    var_R = var_X *  3.2406 + var_Y * -1.5372 + var_Z * -0.4986
    var_G = var_X * -0.9689 + var_Y *  1.8758 + var_Z *  0.0415
    var_B = var_X *  0.0557 + var_Y * -0.2040 + var_Z *  1.0570
    
    if ( var_R > 0.0031308 ): var_R = 1.055 * pow(var_R, K) - 0.055
    else:                     var_R = 12.92 * var_R
    if ( var_G > 0.0031308 ): var_G = 1.055 * pow(var_G, K) - 0.055
    else:                     var_G = 12.92 * var_G
    if ( var_B > 0.0031308 ): var_B = 1.055 * pow(var_B, K) - 0.055
    else:                     var_B = 12.92 * var_B

    sR = var_R * 255
    sG = var_G * 255
    sB = var_B * 255

    return (sR, sG, sB)

def xyz2srgb(X, Y, Z):
    """ X, Y and Z input refer to a D65/2° standard illuminant.
        sR, sG and sB (standard RGB) output range = 0 ÷ 255
    """
    var_X = X / 100
    var_Y = Y / 100
    var_Z = Z / 100

    var_R = var_X *  3.2406 + var_Y * -1.5372 + var_Z * -0.4986
    var_G = var_X * -0.9689 + var_Y *  1.8758 + var_Z *  0.0415
    var_B = var_X *  0.0557 + var_Y * -0.2040 + var_Z *  1.0570

    k = 1 / 2.4
    
    if ( var_R > 0.0031308 ): var_R = 1.055 * pow(var_R, K) - 0.055
    else:                     var_R = 12.92 * var_R
    if ( var_G > 0.0031308 ): var_G = 1.055 * pow(var_G, K) - 0.055
    else:                     var_G = 12.92 * var_G
    if ( var_B > 0.0031308 ): var_B = 1.055 * pow(var_B, K) - 0.055
    else:                     var_B = 12.92 * var_B

    return (var_R, var_G, var_B)
