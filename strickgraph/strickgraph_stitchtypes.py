"""
OBSOLETE
replaced via load_stitchinfo
"""
stitchtypes=[
    "knit",
    "yarn_over",
    "purl",
    "k2tog",
    "bindof",
    ]

knit_info={ "in":[ "up", "next" ], "out":[ "up", "next"] }
yarnover_info={ "in":[ "next" ], "out":[ "up", "next"] }
purl_info={ "in":[ "up", "next" ], "out":[ "up", "next"] }
k2tog_info={ "in":[ "up", "next" ], "out":[ "next"] }
bindof_info={ "in":[ "up", "next" ], "out":["up", "next"] }
stitch_infos={
        "knit":knit_info,
        "yarnover":yarnover_info,
        "purl":purl_info,
        "k2tog":k2tog_info,
        "bindof":bindof_info,
        }
