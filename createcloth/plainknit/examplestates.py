from .state import rowstate, \
                linetype_identifier_simple, \
                linetype_identifier_oneside_decrease, \
                linetype_identifier_oneside_increase, \
                linetype_identifier_fourborderstitches

start: rowstate = rowstate( "start", linetype_identifier_simple( "yarnover" ) )
"""Startrow with only  yarnover"""

end: rowstate = rowstate( "end", linetype_identifier_simple( "bindoff" ) )
"""endrow with only bindoff"""

enddecrease: rowstate = rowstate.with_static_updowndifference( "enddecrease", \
                linetype_identifier_fourborderstitches( "bindoff", \
                ["bindoff", "bind2off", "bindoff", "bindoff" ] ), -2)
"""endrow wizh left and right 3rd position bind2off and else only bindoff"""

lefteaves: rowstate = rowstate.with_variabledifference( "lefteaves", \
                linetype_identifier_oneside_increase( "knit", "yarnover", \
                right=False ), updowndifference_positive=True,\
                valid_sides=("left",))
"""row with mainly knit but on zje left side yarnover for increase"""

righteaves: rowstate = rowstate.with_variabledifference( "righteaves", \
                linetype_identifier_oneside_increase( "knit", "yarnover", \
                right=True ), updowndifference_positive=True ,\
                valid_sides=("right",))
"""row with mainly knit but on the right side yarnover for increase"""

leftplane: rowstate = rowstate.with_variabledifference( "leftplane", \
                linetype_identifier_oneside_decrease( "knit", "bindoff", \
                right=False ), updowndifference_positive=False, \
                valid_sides=("left",))
"""row with mainly knit but on the left side bindoff for decrease"""

rightplane: rowstate = rowstate.with_variabledifference( "rightplane", \
                linetype_identifier_oneside_decrease( "knit", "bindoff", \
                right=True ), updowndifference_positive=False,\
                valid_sides=("right",))
"""row with mainly knit but on the right side bindoff for decrease"""

plain: rowstate = rowstate( "plain", linetype_identifier_simple( "knit" ) )
"""row with only knit"""

increase: rowstate = rowstate.with_static_updowndifference( "increase",
                linetype_identifier_fourborderstitches( "knit", \
                ["knit", "yarnover", "knit", "knit" ] ), 2)
"""row with left and right 3rd position yarnover and else only knits. 
yarnover is for increase.
"""

decrease: rowstate = rowstate.with_static_updowndifference( "decrease",
                linetype_identifier_fourborderstitches( "knit", \
                ["knit", "k2tog", "knit", "knit" ] ), -2)
"""row with left and right 3rd position k2tog and else only knits. 
k2tog is for decrease.
"""
