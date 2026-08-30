# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

# 1. Bring signature to left + reduce top margin
old_sig_cell = '<td style="width:140px; text-align:center; padding:0;">\n          <p style="font-family:\'Viner Hand ITC\', cursive; font-size:10.1pt; margin:8pt 0 0; color:#000;">Kenny LAI</p>'
new_sig_cell = '<td style="text-align:left; padding:0;">\n          <p style="font-family:\'Viner Hand ITC\', cursive; font-size:10.1pt; margin:1pt 0 0; color:#000;">Kenny LAI</p>'
assert old_sig_cell in html, 'sig cell not found'
html = html.replace(old_sig_cell, new_sig_cell, 1)

# 2. Left-align the signature line too
old_line_cell = '<td style="width:140px; text-align:center; padding:0;">\n          <p style="margin:0;">_______________</p>'
new_line_cell = '<td style="text-align:left; padding:0;">\n          <p style="margin:0;">_______________</p>'
assert old_line_cell in html, 'line cell not found'
html = html.replace(old_line_cell, new_line_cell, 1)

# 3. Reduce space above "Yours faithfully," to bring whole block up
old_yours = '<p style="margin-top:10pt; font-size:10pt;">Yours faithfully,</p>'
new_yours = '<p style="margin-top:4pt; font-size:10pt;">Yours faithfully,</p>'
assert old_yours in html, 'yours faithfully not found'
html = html.replace(old_yours, new_yours, 1)

# 4. Reduce margin-top on printed "Kenny LAI" below line
old_printed = '<p style="font-size:10pt; font-weight:bold; margin-top:4pt;">Kenny LAI</p>'
new_printed = '<p style="font-size:10pt; font-weight:bold; margin-top:1pt;">Kenny LAI</p>'
assert old_printed in html, 'printed name not found'
html = html.replace(old_printed, new_printed, 1)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done: signature left-aligned, top/bottom margins reduced')
