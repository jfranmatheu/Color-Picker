'''
var_H = arc_tangent( CIE-b*, CIE-a* )  //Quadrant by signs

if ( var_H > 0 ) var_H = ( var_H / PI ) * 180
else             var_H = 360 - ( abs( var_H ) / PI ) * 180

CIE-L* = CIE-L*
CIE-C* = sqrt( CIE-a* ^ 2 + CIE-b* ^ 2 )
CIE-H° = var_H
'''
