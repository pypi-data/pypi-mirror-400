# The following classes are based on the Base16 Tokyo Night theme by Michaël Ball, available at
# https://git.michaelball.name/gid/base16-tokyo-night-scheme/about/, under the following License:
#
# MIT License
#
# Copyright (c) 2021 Michaël Ball
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# The Base16 Tokyo Night theme theme is  based on the Tokyo Night VSCode theme by enkia, available
# at https://github.com/enkia/tokyo-night-vscode-theme, under the following License:
#
# The MIT License (MIT)
#
# Copyright (c) 2018-present Enkia
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from pygments.style import Style

from .helpers import Base16Colors, get_styles_from_base16_colors


class TokyoNightDarkStyle(Style):
    name = 'Tokyo Night Dark'
    author = 'Michaël Ball'

    base16_colors = Base16Colors(
        base00='#1A1B26',
        base01='#16161E',
        base02='#2F3549',
        base03='#444B6A',
        base04='#787C99',
        base05='#A9B1D6',
        base06='#CBCCD1',
        base07='#D5D6DB',
        base08='#C0CAF5',
        base09='#A9B1D6',
        base0A='#0DB9D7',
        base0B='#9ECE6A',
        base0C='#B4F9F8',
        base0D='#2AC3DE',
        base0E='#BB9AF7',
        base0F='#F7768E',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)


class TokyoNightLightStyle(Style):
    name = 'Tokyo Night Light'
    author = 'Michaël Ball'

    base16_colors = Base16Colors(
        base00='#D5D6DB',
        base01='#CBCCD1',
        base02='#DFE0E5',
        base03='#9699A3',
        base04='#4C505E',
        base05='#343B59',
        base06='#1A1B26',
        base07='#1A1B26',
        base08='#343B58',
        base09='#965027',
        base0A='#166775',
        base0B='#485E30',
        base0C='#3E6968',
        base0D='#34548A',
        base0E='#5A4A78',
        base0F='#8C4351',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)


class TokyoNightStormStyle(Style):
    name = 'Tokyo Night Storm'
    author = 'Michaël Ball'

    base16_colors = Base16Colors(
        base00='#24283B',
        base01='#16161E',
        base02='#343A52',
        base03='#444B6A',
        base04='#787C99',
        base05='#A9B1D6',
        base06='#CBCCD1',
        base07='#D5D6DB',
        base08='#C0CAF5',
        base09='#A9B1D6',
        base0A='#0DB9D7',
        base0B='#9ECE6A',
        base0C='#B4F9F8',
        base0D='#2AC3DE',
        base0E='#BB9AF7',
        base0F='#F7768E',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)


class TokyoNightTerminalDarkStyle(Style):
    name = 'Tokyo Night Terminal Dark'
    author = 'Michaël Ball'

    base16_colors = Base16Colors(
        base00='#16161E',
        base01='#1A1B26',
        base02='#2F3549',
        base03='#444B6A',
        base04='#787C99',
        base05='#787C99',
        base06='#CBCCD1',
        base07='#D5D6DB',
        base08='#F7768E',
        base09='#FF9E64',
        base0A='#E0AF68',
        base0B='#41A6B5',
        base0C='#7DCFFF',
        base0D='#7AA2F7',
        base0E='#BB9AF7',
        base0F='#D18616',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)


class TokyoNightTerminalLightStyle(Style):
    name = 'Tokyo Night Terminal Light'
    author = 'Michaël Ball'

    base16_colors = Base16Colors(
        base00='#D5D6DB',
        base01='#CBCCD1',
        base02='#DFE0E5',
        base03='#9699A3',
        base04='#4C505E',
        base05='#4C505E',
        base06='#1A1B26',
        base07='#1A1B26',
        base08='#8C4351',
        base09='#965027',
        base0A='#8F5E15',
        base0B='#33635C',
        base0C='#0F4B6E',
        base0D='#34548A',
        base0E='#5A4A78',
        base0F='#655259',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)


class TokyoNightTerminalStormStyle(Style):
    name = 'Tokyo Night Terminal Storm'
    author = 'Michaël Ball'

    base16_colors = Base16Colors(
        base00='#24283B',
        base01='#1A1B26',
        base02='#343A52',
        base03='#444B6A',
        base04='#787C99',
        base05='#787C99',
        base06='#CBCCD1',
        base07='#D5D6DB',
        base08='#F7768E',
        base09='#FF9E64',
        base0A='#E0AF68',
        base0B='#41A6B5',
        base0C='#7DCFFF',
        base0D='#7AA2F7',
        base0E='#BB9AF7',
        base0F='#D18616',
    )

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)
