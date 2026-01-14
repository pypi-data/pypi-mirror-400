from pygments.style import Style

from .helpers import Base16Colors, get_styles_from_base16_colors


# From https://github.com/mohd-akram/base16-pygments/blob/master/pygments_base16/base16-material.py
class MaterialNewStyle(Style):
    name = 'Material New'

    base16_colors = Base16Colors(
        base00='#263238',
        base01='#2E3C43',
        base02='#314549',
        base03='#546E7A',
        base04='#B2CCD6',
        base05='#EEFFFF',
        base06='#EEFFFF',
        base07='#FFFFFF',
        base08='#F07178',
        base09='#F78C6C',
        base0A='#FFCB6B',
        base0B='#C3E88D',
        base0C='#89DDFF',
        base0D='#82AAFF',
        base0E='#C792EA',
        base0F='#FF5370',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)
