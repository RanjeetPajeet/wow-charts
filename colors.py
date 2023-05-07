"""
# colors.py

Defines colors used in the charts.

Raw:    LineColors.red
MA4:    LineColors.green
MA12:   LineColors.purple
MA24:   LineColors.blue
MA48:   LineColors.orange
"""
from collections import namedtuple


Gradient = namedtuple("Gradient", ['top', 'bottom'])

LineColors = namedtuple("LineColors", 
    ['blue',         'orange',         'green',         'red',         'purple',         'pink',
     'dark_blue',    'dark_orange',    'dark_green',    'dark_red',    'dark_purple',    'dark_pink',
     'light_blue',   'light_orange',   'light_green',   'light_red',   'light_purple',   'light_pink',
     'lighter_blue', 'lighter_orange', 'lighter_green', 'lighter_red', 'lighter_purple', 'lighter_pink']
)

GradientColors = namedtuple("GradientColors",
    ['blue', 'orange', 'green', 'red', 'purple', 'pink']
)




LineColors = LineColors(
    '#3AA9FF', '#FF7F0E', '#3DDC3D', '#FF3C3D', '#9467BD', '#E377C2',
    '#2B7EBF', '#CF670B', '#31B231', '#BF2D2D', '#6F4D8D', '#AA5991',
    '#6BBEFF', '#FF9F4A', '#6DE46D', '#FF6C6D', '#AE8DCD', '#EA99D1',
    '#90CEFF', '#FFB777', '#91EA91', '#FF9091', '#C2A9D9', '#EFB2DC',
)

# GradientColors = GradientColors(
#     Gradient('#2B7EBF','#3AA9FF'),      # blue.top,    blue.bottom
#     Gradient('#CF670B','#FF7F0E'),      # orange.top,  orange.bottom
#     Gradient('#31B231','#3DDC3D'),      # green.top,   green.bottom
#     Gradient('#BF2D2D','#FF3C3D'),      # red.top,     red.bottom
#     Gradient('#6F4D8D','#9467BD'),      # purple.top,  purple.bottom
#     Gradient('#AA5991','#E377C2'),      # pink.top,    pink.bottom
# )

GradientColors = GradientColors(
    Gradient(LineColors.dark_blue,   LineColors.light_blue),        # blue.top,    blue.bottom
    Gradient(LineColors.dark_orange, LineColors.light_orange),      # orange.top,  orange.bottom
    Gradient(LineColors.dark_green,  LineColors.light_green),       # green.top,   green.bottom
    Gradient(LineColors.dark_red,    LineColors.light_red),         # red.top,     red.bottom
    Gradient(LineColors.dark_purple, LineColors.light_purple),      # purple.top,  purple.bottom
    Gradient(LineColors.dark_pink,   LineColors.light_pink),        # pink.top,    pink.bottom
)














### OLD COLORS

# OGLineColors = namedtuple("OGLineColors", ['blue', 'green', 'purple', 'red', 'yellow'])
# OGGradientColors = namedtuple("OGGradientColors", ['blue', 'green', 'purple', 'red', 'yellow'])


# og_line_colors = OGLineColors(
#     '#3AA9FF',      # og_line_colors.blue
#     '#0CE550',      # og_line_colors.green
#     '#6029C1',      # og_line_colors.purple
#     '#BA191C',      # og_line_colors.red
#     '#F5C500',      # og_line_colors.yellow
# )

# og_gradient_colors = OGGradientColors(
#     Gradient('#0068C9','#83C9FF'),      # og_gradient_colors.blue.top,   og_gradient_colors.blue.bottom
#     Gradient('#29B09D','#7DEFA1'),      # og_gradient_colors.green.top,  og_gradient_colors.green.bottom
#     Gradient('#5728AE','#9670DC'),      # og_gradient_colors.purple.top, og_gradient_colors.purple.bottom
#     Gradient('#D71B35','#FF5169'),      # og_gradient_colors.red.top,    og_gradient_colors.red.bottom
#     Gradient('#E3B600','#FCD32A'),      # og_gradient_colors.yellow.top, og_gradient_colors.yellow.bottom
# )

# og_comparison_line_colors = OGLineColors(       # lighter versions of the og line colors
#     '#83C9FF',      # og_comparison_line_colors.blue
#     '#7DEFA1',      # og_comparison_line_colors.green
#     '#9670DC',      # og_comparison_line_colors.purple
#     '#FF5169',      # og_comparison_line_colors.red
#     '#FFE060',      # og_comparison_line_colors.yellow
# )

