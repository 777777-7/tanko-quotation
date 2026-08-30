# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

# 1. Add one blank line after "Yours faithfully,"
old_yours = '<p style="margin-top:4pt; font-size:10pt;">Yours faithfully,</p>'
new_yours = '<p style="margin-top:4pt; margin-bottom:11pt; font-size:10pt;">Yours faithfully,</p>'
assert old_yours in html, 'yours faithfully not found'
html = html.replace(old_yours, new_yours, 1)

# 2. Change Primaxs margin-bottom from 22pt to 15pt
old_primax = '<p style="font-size:10pt; font-weight:bold; margin-bottom:22pt;">Primaxs Marketing (M) Sdn. Bhd.</p>'
new_primax = '<p style="font-size:10pt; font-weight:bold; margin-bottom:15pt;">Primaxs Marketing (M) Sdn. Bhd.</p>'
assert old_primax in html, 'primax not found'
html = html.replace(old_primax, new_primax, 1)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done: Yours faithfully +11pt bottom, Primaxs 15pt bottom')
