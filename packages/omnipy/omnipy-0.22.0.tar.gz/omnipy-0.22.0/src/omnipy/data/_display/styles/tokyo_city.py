# The following classes are based on the Base16 Tokyo City theme by Michaël Ball, available at
# https://git.michaelball.name/gid/base16-tokyo-city-scheme/about/, under the following License:
#
# MIT License
#
# Copyright (c) 2019 Michaël Ball
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
# The Base16 Tokyo City theme is based on the Tokyo City VSCode theme by Huy Tran, available at
# https://github.com/huytd/vscode-tokyo-city, under the following License:
#
# MIT License
#
# Copyright Huy Tran
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
# The Tokyo City VSCode theme is based on the Tokyo Night VSCode theme by enkia, available
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
#
# The Tokyo City VSCode theme is also partly based on the City Lights theme by Yummygum, available
# at https://github.com/Yummygum/city-lights-syntax-vsc. However, due to the restrictiveness of
# the City Lights theme's license, Attribution-NonCommercial-NoDerivatives 4.0 International
# [CC BY-NC-ND 4.0](https://creativecommons.org/licenses/by-nc-nd/4.0/), the "Tokyo City Terminal
# Dark" style has been removed here, and other colors originally from the City Lights theme have
# been replaced in the other three variants.

from pygments.style import Style

from .helpers import Base16Colors, get_styles_from_base16_colors

#
# class TokyoCityDarkStyle(Style):
#     name = 'Tokyo City Dark'
#     author = 'Michaël Ball'
#
#     base16_colors = Base16Colors(
#         base00='#171D23',  #
#         base01='#1D252C',  #
#         base02='#28323A',
#         base03='#526270',
#         base04='#B7C5D3',  #
#         base05='#D8E2EC',
#         base06='#F6F6F8',
#         base07='#FBFBFD',
#         base08='#F7768E',
#         base09='#FF9E64',
#         base0A='#B7C5D3',  #
#         base0B='#9ECE6A',
#         base0C='#89DDFF',
#         base0D='#7AA2F7',
#         base0E='#BB9AF7',
#         base0F='#BB9AF7',
#     )
#
#     default_style = ''
#
#     background_color = base16_colors.base00
#     highlight_color = base16_colors.base02
#
#     styles = get_styles_from_base16_colors(base16_colors)
#
#
# class TokyoCityLightStyle(Style):
#     name = 'Tokyo City Light'
#     author = 'Michaël Ball'
#
#     base16_colors = Base16Colors(
#         base00='#FBFBFD',
#         base01='#F6F6F8',
#         base02='#EDEFF6',
#         base03='#9699A3',
#         base04='#4c505e',
#         base05='#343B59',
#         base06='#1D252C',  #
#         base07='#171D23',  #
#         base08='#8C4351',
#         base09='#965027',
#         base0A='#4C505E',
#         base0B='#485E30',
#         base0C='#4C505E',
#         base0D='#34548a',
#         base0E='#5A4A78',
#         base0F='#5A4A78',
#     )
#
#     default_style = ''
#
#     background_color = base16_colors.base00
#     highlight_color = base16_colors.base02
#
#     styles = get_styles_from_base16_colors(base16_colors)
#
#
# class TokyoCityTerminalDarkStyle(Style):
#     name = 'Tokyo City Terminal Dark'
#     author = 'Michaël Ball'
#
#     base16_colors = Base16Colors(
#         base00='#171D23',  #
#         base01='#1D252C',  #
#         base02='#28323A',
#         base03='#526270',
#         base04='#B7C5D3',  #
#         base05='#D8E2EC',
#         base06='#F6F6F8',
#         base07='#FBFBFD',
#         base08='#D95468',  #
#         base09='#FF9E64',
#         base0A='#EBBF83',  #
#         base0B='#8BD49C',  #
#         base0C='#70E1E8',  #
#         base0D='#539AFC',  #
#         base0E='#B62D65',  #
#         base0F='#DD9D82',
#     )
#
#     default_style = ''
#
#     background_color = base16_colors.base00
#     highlight_color = base16_colors.base02
#
#     styles = get_styles_from_base16_colors(base16_colors)
#


# Comments
class OmnipyTokyoCityTerminalLightStyle(Style):
    """
    Documentation
    """
    name = 'Tokyo City Terminal Light'
    author = 'Michaël Ball'

    def __init__(self, a: int = 0) -> None:
        super().__init__()
        self.a = a

    base16_colors = Base16Colors(
        base00='#FBFBFD',
        base01='#F6F6F8',
        base02='#D8E2EC',
        base03='#B7C5D3',  #
        base04='#526270',
        base05='#28323A',
        base06='#1D252C',  #
        base07='#171D23',  #
        base08='#8C4351',
        base09='#965027',
        base0A='#8f5E15',
        base0B='#33635C',
        base0C='#0F4B6E',
        base0D='#34548A',
        base0E='#5A4A78',
        base0F='#7E5140')

    default_style = ''

    background_color = base16_colors.base00
    highlight_color = base16_colors.base02

    styles = get_styles_from_base16_colors(base16_colors)
