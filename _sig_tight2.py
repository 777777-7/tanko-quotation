# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

old_block = (
    '          <p style="font-family:\'Viner Hand ITC\', cursive; font-size:10.1pt; margin:0; line-height:1; color:#000;">Kenny LAI</p>\n'
    '          <p style="margin:0; line-height:1;">_______________</p>'
)

new_block = (
    '          <p style="font-family:\'Viner Hand ITC\', cursive; font-size:10.1pt; margin:0; line-height:0.7; color:#000;">Kenny LAI</p>\n'
    '          <p style="margin:-3pt 0 0 0; line-height:1;">_______________</p>'
)

assert old_block in html, 'block not found'
html = html.replace(old_block, new_block, 1)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done: signature line-height 0.7, line pulled up with -3pt margin')
