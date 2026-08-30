# -*- coding: utf-8 -*-
import re
html = open('index.html', encoding='utf-8').read()
# Find the quotation generation function that calls buildItemRowHtml
i = html.find('buildItemRowHtml(i + 1, item)')
print('call at', i)
# find enclosing function
start = html.rfind('function ', 0, i)
print(html[start:start+400])
print('...')
# find the rowsHtml context
print(html[i-1500:i+800])
