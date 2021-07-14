from .state import rowstate, \
                linetype_identifier_simple, \
                linetype_identifier_oneside_decrease, \
                linetype_identifier_oneside_increase, \
                linetype_identifier_fourborderstitches

start = rowstate( "start", linetype_identifier_simple( "yarnover" ) )
end = rowstate( "end", linetype_identifier_simple( "bindoff" ) )
enddecrease = rowstate.with_static_downupdifference( "enddecrease", \
                linetype_identifier_fourborderstitches( "bindoff", \
                ["bindoff", "bind2off", "bindoff", "bindoff" ] ), -2)
lefteaves = rowstate.with_variabledifference( "lefteaves", \
                linetype_identifier_oneside_increase( "knit", "yarnover", \
                right=False ), downupdifference_positive=True )
righteaves = rowstate.with_variabledifference( "righteaves", \
                linetype_identifier_oneside_increase( "knit", "yarnover", \
                right=True ), downupdifference_positive=True )
leftplane = rowstate.with_variabledifference( "leftplane", \
                linetype_identifier_oneside_decrease( "knit", "bindoff", \
                right=False ), downupdifference_positive=False )
rightplane = rowstate.with_variabledifference( "rightplane", \
                linetype_identifier_oneside_decrease( "knit", "bindoff", \
                right=True ), downupdifference_positive=False )
plain = rowstate( "plain", linetype_identifier_simple( "knit" ) )
increase = rowstate.with_static_downupdifference( "increase",
                linetype_identifier_fourborderstitches( "knit", \
                ["knit", "yarnover", "knit", "knit" ] ), 2)
decrease = rowstate.with_static_downupdifference( "decrease",
                linetype_identifier_fourborderstitches( "knit", \
                ["knit", "k2tog", "knit", "knit" ] ), -2)
