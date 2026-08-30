# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

# Remove forced page break, add small margin + page-break-after:avoid on heading
old = (
    '      <!-- Page break: product photos start on new page -->\n'
    '      <div style="page-break-after: always;"></div>\n'
    '\n'
    '      <!-- Page 2: Product Photos with specs -->\n'
    '      <p style="margin:0 0 8pt 0; font-size:14pt; font-weight:bold; border-bottom:2pt solid #000; padding-bottom:4pt;">Product Photos</p>'
)

new = (
    '      <!-- Product photos flow naturally: one page if it fits, otherwise continue on next page -->\n'
    '      <p style="margin:14pt 0 8pt 0; font-size:14pt; font-weight:bold; border-bottom:2pt solid #000; padding-bottom:4pt; page-break-after:avoid;">Product Photos</p>'
)

assert old in html, 'page break block not found'
html = html.replace(old, new, 1)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done: forced page break removed, natural flow with page-break-after:avoid on heading')
