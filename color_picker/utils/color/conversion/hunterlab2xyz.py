'''
//Reference-X, Y and Z refer to specific illuminants and observers.
//Common reference values are available below in this same page.

var_Ka = ( 175.0 / 198.04 ) * ( Reference-Y + Reference-X )
var_Kb = (  70.0 / 218.11 ) * ( Reference-Y + Reference-Z )

Y = ( ( Hunter-L / Reference-Y ) ^ 2 ) * 100.0
X =   ( Hunter-a / var_Ka * sqrt( Y / Reference-Y ) + ( Y / Reference-Y ) ) * Reference-X
Z = - ( Hunter-b / var_Kb * sqrt( Y / Reference-Y ) - ( Y / Reference-Y ) ) * Reference-Z
'''
