'''
//Reference-X, Y and Z refer to specific illuminants and observers.
//Common reference values are available below in this same page.

var_Y = ( CIE-L* + 16 ) / 116
var_X = CIE-a* / 500 + var_Y
var_Z = var_Y - CIE-b* / 200

if ( var_Y^3  > 0.008856 ) var_Y = var_Y^3
else                       var_Y = ( var_Y - 16 / 116 ) / 7.787
if ( var_X^3  > 0.008856 ) var_X = var_X^3
else                       var_X = ( var_X - 16 / 116 ) / 7.787
if ( var_Z^3  > 0.008856 ) var_Z = var_Z^3
else                       var_Z = ( var_Z - 16 / 116 ) / 7.787

X = var_X * Reference-X
Y = var_Y * Reference-Y
Z = var_Z * Reference-Z
'''

def cielab2xyz(CIE_L, CIE_a, CIE_b, Reference_X=95.047, Reference_Y=100.0, Reference_Z=108.883):
    var_Y = ( CIE_L + 16 ) / 116
    var_X = CIE_a / 500 + var_Y
    var_Z = var_Y - CIE_b / 200

    if ( pow(var_Y, 3)  > 0.008856 ):   var_Y = pow(var_Y, 3)
    else:                               var_Y = ( var_Y - 16 / 116 ) / 7.787
    if ( pow(var_X, 3)  > 0.008856 ):   var_X = pow(var_X, 3)
    else:                               var_X = ( var_X - 16 / 116 ) / 7.787
    if ( pow(var_Z, 3)  > 0.008856 ):   var_Z = pow(var_Z, 3)
    else:                               var_Z = ( var_Z - 16 / 116 ) / 7.787

    X = var_X * Reference_X
    Y = var_Y * Reference_Y
    Z = var_Z * Reference_Z
    
    return (X, Y, Z)
