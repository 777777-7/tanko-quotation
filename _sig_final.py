# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

# 1. Add space after "Primaxs Marketing (M) Sdn. Bhd."
old_primax = '<p style="font-size:10pt; font-weight:bold;">Primaxs Marketing (M) Sdn. Bhd.</p>'
new_primax = '<p style="font-size:10pt; font-weight:bold; margin-bottom:10pt;">Primaxs Marketing (M) Sdn. Bhd.</p>'
assert old_primax in html, 'primax not found'
html = html.replace(old_primax, new_primax, 1)

# 2. Change line margin from -3pt to -6pt
old_line = '<p style="margin:-3pt 0 0 0; line-height:1;">_______________</p>'
new_line = '<p style="margin:-6pt 0 0 0; line-height:1;">_______________</p>'
assert old_line in html, 'line not found'
html = html.replace(old_line, new_line, 1)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done: space after Primaxs (10pt), line margin changed to -6pt')
