'''
//Reference-X, Y and Z refer to specific illuminants and observers.
//Common reference values are available below in this same page.

var_X = X / Reference-X
var_Y = Y / Reference-Y
var_Z = Z / Reference-Z

if ( var_X > 0.008856 ) var_X = var_X ^ ( 1/3 )
else                    var_X = ( 7.787 * var_X ) + ( 16 / 116 )
if ( var_Y > 0.008856 ) var_Y = var_Y ^ ( 1/3 )
else                    var_Y = ( 7.787 * var_Y ) + ( 16 / 116 )
if ( var_Z > 0.008856 ) var_Z = var_Z ^ ( 1/3 )
else                    var_Z = ( 7.787 * var_Z ) + ( 16 / 116 )

CIE-L* = ( 116 * var_Y ) - 16
CIE-a* = 500 * ( var_X - var_Y )
CIE-b* = 200 * ( var_Y - var_Z )
'''

def xyz2cielab(X, Y, Z, Reference_X=95.047, Reference_Y=100.0, Reference_Z=108.883):
    """ Reference-X, Y and Z refer to specific illuminants and observers.
        Common reference values are available below in this same page.
    """
    # This conversion requires a reference white 
    var_X = X / Reference_X
    var_Y = Y / Reference_Y
    var_Z = Z / Reference_Z

    if ( var_X > 0.008856 ): var_X = var_X ^ ( 1/3 )
    else:                    var_X = ( 7.787 * var_X ) + ( 16 / 116 )
    if ( var_Y > 0.008856 ): var_Y = var_Y ^ ( 1/3 )
    else:                    var_Y = ( 7.787 * var_Y ) + ( 16 / 116 )
    if ( var_Z > 0.008856 ): var_Z = var_Z ^ ( 1/3 )
    else:                    var_Z = ( 7.787 * var_Z ) + ( 16 / 116 )

    CIE_L = ( 116 * var_Y ) - 16
    CIE_a = 500 * ( var_X - var_Y )
    CIE_b = 200 * ( var_Y - var_Z )
    
    return (CIE_L, CIE_a, CIE_b)
