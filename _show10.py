# -*- coding: utf-8 -*-
import re
html = open('index.html', encoding='utf-8').read()

# Print raw chunk of buildItemRowHtml
i = html.find('function buildItemRowHtml')
print(html[i:i+2400])
