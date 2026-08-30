# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

old_block = (
    '      <table style="border-collapse:collapse; margin:0;">\n'
    '        <tr><td style="text-align:left; padding:0;">\n'
    '          <p style="font-family:\'Viner Hand ITC\', cursive; font-size:10.1pt; margin:1pt 0 0; color:#000;">Kenny LAI</p>\n'
    '        </td></tr>\n'
    '        <tr><td style="text-align:left; padding:0;">\n'
    '          <p style="margin:0;">_______________</p>\n'
    '        </td></tr>\n'
    '      </table>'
)

new_block = (
    '      <table style="border-collapse:collapse; margin:0;">\n'
    '        <tr><td style="text-align:left; padding:0;">\n'
    '          <p style="font-family:\'Viner Hand ITC\', cursive; font-size:10.1pt; margin:0; line-height:1; color:#000;">Kenny LAI</p>\n'
    '          <p style="margin:0; line-height:1;">_______________</p>\n'
    '        </td></tr>\n'
    '      </table>'
)

assert old_block in html, 'signature block not found'
html = html.replace(old_block, new_block, 1)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done: signature and line merged into one cell, line-height:1, margins 0')
