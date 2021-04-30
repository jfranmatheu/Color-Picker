'''
//sR, sG and sB (Standard RGB) input range = 0 ÷ 255
//X, Y and Z output refer to a D65/2° standard illuminant.

var_R = ( sR / 255 )
var_G = ( sG / 255 )
var_B = ( sB / 255 )

if ( var_R > 0.04045 ) var_R = ( ( var_R + 0.055 ) / 1.055 ) ^ 2.4
else                   var_R = var_R / 12.92
if ( var_G > 0.04045 ) var_G = ( ( var_G + 0.055 ) / 1.055 ) ^ 2.4
else                   var_G = var_G / 12.92
if ( var_B > 0.04045 ) var_B = ( ( var_B + 0.055 ) / 1.055 ) ^ 2.4
else                   var_B = var_B / 12.92

var_R = var_R * 100
var_G = var_G * 100
var_B = var_B * 100

X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505
'''

def srgb2xyz(sR, sG, sB):
    """ sR, sG and sB (Standard RGB) input range = 0 ÷ 255
        X, Y and Z output refer to a D65/2° standard illuminant.
    """
    
    if ( sR > 0.04045 ):    sR = pow(( ( sR + 0.055 ) / 1.055 ), 2.4)
    else:                   sR = sR / 12.92
    if ( sG > 0.04045 ):    sG = pow(( ( sG + 0.055 ) / 1.055 ), 2.4)
    else:                   sG = sG / 12.92
    if ( sB > 0.04045 ):    sB = pow(( ( sB + 0.055 ) / 1.055 ), 2.4)
    else:                   sB = sB / 12.92

    sR = sR * 100
    sG = sG * 100
    sB = sB * 100

    X = sR * 0.4124 + sG * 0.3576 + sB * 0.1805
    Y = sR * 0.2126 + sG * 0.7152 + sB * 0.0722
    Z = sR * 0.0193 + sG * 0.1192 + sB * 0.9505
    
    return (X, Y, Z)

def srgb2xyz_255(sR, sG, sB):
    """ sR, sG and sB (Standard RGB) input range = 0 ÷ 255
        X, Y and Z output refer to a D65/2° standard illuminant.
    """

    var_R = ( sR / 255 )
    var_G = ( sG / 255 )
    var_B = ( sB / 255 )

    if ( var_R > 0.04045 ): var_R = pow(( ( var_R + 0.055 ) / 1.055 ), 2.4)
    else:                   var_R = var_R / 12.92
    if ( var_G > 0.04045 ): var_G = pow(( ( var_G + 0.055 ) / 1.055 ), 2.4)
    else:                   var_G = var_G / 12.92
    if ( var_B > 0.04045 ): var_B = pow(( ( var_B + 0.055 ) / 1.055 ), 2.4)
    else:                   var_B = var_B / 12.92

    var_R = var_R * 100
    var_G = var_G * 100
    var_B = var_B * 100

    X = var_R * 0.4124 + var_G * 0.3576 + var_B * 0.1805
    Y = var_R * 0.2126 + var_G * 0.7152 + var_B * 0.0722
    Z = var_R * 0.0193 + var_G * 0.1192 + var_B * 0.9505
    
    return (X, Y, Z)
