from pygments.style import Style

from .helpers import Base16Colors, get_styles_from_base16_colors


class TokyoNightMoonStyle(Style):
    name = 'Tokyo Night Moon'
    author = 'Ólafur Bjarki Bogason'

    base16_colors = Base16Colors(
        base00='#222436',
        base01='#1e2030',
        base02='#2d3f76',
        base03='#636da6',
        base04='#828bb8',
        base05='#3b4261',
        base06='#828bb8',
        base07='#c8d3f5',
        base08='#ff757f',
        base09='#ffc777',
        base0A='#ffc777',
        base0B='#c3e88d',
        base0C='#86e1fc',
        base0D='#82aaff',
        base0E='#fca7ea',
        base0F='#c53b53',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)
