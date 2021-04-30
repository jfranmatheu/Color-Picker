'''
//Reference-X, Y and Z refer to specific illuminants and observers.
//Common reference values are available below in this same page.

var_Ka = ( 175.0 / 198.04 ) * ( Reference-Y + Reference-X )
var_Kb = (  70.0 / 218.11 ) * ( Reference-Y + Reference-Z )

Hunter-L = 100.0 * sqrt( Y / Reference-Y )
Hunter-a = var_Ka * ( ( ( X / Reference-X ) - ( Y / Reference-Y ) ) / sqrt( Y / Reference-Y ) )
Hunter-b = var_Kb * ( ( ( Y / Reference-Y ) - ( Z / Reference-Z ) ) / sqrt( Y / Reference-Y ) )
'''

def xyz2hunterlab(X, Y, Z, Reference_X=95.047, Reference_Y=100.0, Reference_Z=108.883):
    """ Reference-X, Y and Z refer to specific illuminants and observers.
        Common reference values are available below in this same page.
    """
    var_Ka = ( 175.0 / 198.04 ) * ( Reference_Y + Reference_X )
    var_Kb = (  70.0 / 218.11 ) * ( Reference_Y + Reference_Z )

    Hunter_L = 100.0 * sqrt( Y / Reference_Y )
    Hunter_a = var_Ka * ( ( ( X / Reference_X ) - ( Y / Reference_Y ) ) / sqrt( Y / Reference_Y ) )
    Hunter_b = var_Kb * ( ( ( Y / Reference_Y ) - ( Z / Reference_Z ) ) / sqrt( Y / Reference_Y ) )
    
    return (Hunter_L, Hunter_a, Hunter_b)
