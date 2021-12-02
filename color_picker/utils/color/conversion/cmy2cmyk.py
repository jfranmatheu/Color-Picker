'''
//C, M, Y and K range = 0 ÷ 1.0

var_K = 1

if ( C < var_K )   var_K = C
if ( M < var_K )   var_K = M
if ( Y < var_K )   var_K = Y
if ( var_K == 1 ) {
    C = 0          //Black only
    M = 0
    Y = 0
}
else {
    C = ( C - var_K ) / ( 1 - var_K )
    M = ( M - var_K ) / ( 1 - var_K )
    Y = ( Y - var_K ) / ( 1 - var_K )
}
K = var_K
'''
