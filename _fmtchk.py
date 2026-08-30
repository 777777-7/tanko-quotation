# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

i = html.find('"ME-321":')
print('ENHANCED ME-321 raw:', repr(html[i:i+150]))

j = html.find('"WKT-5102F1+WPK-21":')
print('ENHANCED WKT+ raw:', repr(html[j:j+170]))

k = html.find('"ME-321": {"model_no"')
print('DETAILED ME-321 raw:', repr(html[k:k+180]))

# Verify: no real newline inside the inserted ENHANCED value (should be literal backslash-n)
# Locate the full ENHANCED object, then check chars between "ME-321": and the next comma
import re
m = re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S)
obj = m.group(1)
mm = re.search(r'"ME-321": (".*?")', obj, re.S)
print('ME-321 value has real newline:', '\n' in mm.group(1))
print('ME-321 value has literal \\n:', '\\n' in mm.group(1))
