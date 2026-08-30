# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

old = ('      <!-- Product photos flow naturally after line items; each image+spec pair stays together -->\n'
       '\n'
       '      <!-- Page 2: Product Photos with specs -->\n'
       '      <p style="margin:14pt 0 8pt 0; font-size:14pt; font-weight:bold; border-bottom:2pt solid #000; padding-bottom:4pt; page-break-after:avoid;">Product Photos</p>')

new = ('      <!-- Page break: product photos start on new page -->\n'
       '      <div style="page-break-after: always;"></div>\n'
       '\n'
       '      <!-- Page 2: Product Photos with specs -->\n'
       '      <p style="margin:0 0 8pt 0; font-size:14pt; font-weight:bold; border-bottom:2pt solid #000; padding-bottom:4pt;">Product Photos</p>')

if old not in html:
    print('OLD PATTERN NOT FOUND')
    # try to find what's actually there
    i = html.find('Product photos flow naturally')
    print('context:', repr(html[i-50:i+400]))
else:
    html = html.replace(old, new, 1)
    open('index.html', 'w', encoding='utf-8').write(html)
    print('Replaced successfully')
    print('Forced page break div present:', 'page-break-after: always;"></div>' in html)
    print('Flow comment removed:', 'Product photos flow naturally' not in html)
    print('Heading margin reset:', 'margin:0 0 8pt 0;' in html)
