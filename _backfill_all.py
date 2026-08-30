# -*- coding: utf-8 -*-
"""
Full back-fill of DETAILED_SPECS + ENHANCED_PRODUCTS for all SKUs missing them,
plus layout change: remove forced page break so photos flow naturally,
while keeping each image+spec pair together.
"""
import re, json, shutil

HTML_PATH = 'index.html'
BACKUP_PATH = 'index.html.bak-fullspec'

html = open(HTML_PATH, encoding='utf-8').read()

# ---- Parse current inline objects ----
ds_match = re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S)
ep_match = re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S)
ds = json.loads(ds_match.group(1))
ep = json.loads(ep_match.group(1))

# ---- Parse PRODUCT_DATA (sku -> name) ----
pd_match = re.search(r'const PRODUCT_DATA = \[(.*?)\];', html, re.S)
pd_block = pd_match.group(1)
pd_entries = re.findall(r'\{\s*sku:\s*"([^"]*)",\s*name:\s*"((?:[^"\\]|\\.)*)"', pd_block)
pd_names = {sku: name for sku, name in pd_entries}
print('PRODUCT_DATA parsed:', len(pd_names))

# ---- Load data JSON ----
data_specs = json.load(open('data/detailed_specs.json', encoding='utf-8'))

# ---- Identify SKUs to fill ----
all_skus = sorted(set(pd_names.keys()))
to_fill_ds = [s for s in all_skus if s not in ds and s != '<SKU code>']
to_fill_ep = [s for s in all_skus if s not in ep and s != '<SKU code>']
print('SKUs needing DETAILED_SPECS:', len(to_fill_ds))
print('SKUs needing ENHANCED:', len(to_fill_ep))

# ---- Build new DETAILED_SPECS entries ----
new_ds = {}
missing_data = []
for s in to_fill_ds:
    if s in data_specs:
        new_ds[s] = data_specs[s]
    else:
        missing_data.append(s)
print('DETAILED_SPECS entries to add:', len(new_ds))
print('SKUs with no data in JSON:', missing_data)

# ---- Build new ENHANCED entries (from PRODUCT_DATA name) ----
new_ep = {}
for s in to_fill_ep:
    if s in pd_names:
        # The name in PRODUCT_DATA uses literal \n escapes in the HTML source.
        # json.dumps will preserve them as \n in the output.
        name_raw = pd_names[s]
        # Convert literal \n in the raw string to actual newline for the value,
        # then json.dumps will write it back as \n — matching existing format.
        name_val = name_raw.replace('\\n', '\n')
        new_ep[s] = name_val
print('ENHANCED entries to add:', len(new_ep))

# ---- JSON serialization matching existing inline style ----
def js_obj_ds(entries):
    parts = []
    for k in sorted(entries):
        v = json.dumps(entries[k], ensure_ascii=False, separators=(", ", ": "))
        parts.append('"%s": %s' % (k, v))
    return ",\n".join(parts)

def js_obj_ep(entries):
    parts = []
    for k in sorted(entries):
        v = json.dumps(entries[k], ensure_ascii=False)
        parts.append('"%s": %s' % (k, v))
    return ",\n".join(parts)

# ---- Insert DETAILED_SPECS ----
obj_ds = ds_match.group(1)
new_obj_ds = obj_ds[:-1] + ',\n' + js_obj_ds(new_ds) + '\n}'
html = html[:ds_match.start(1)] + new_obj_ds + html[ds_match.end(1):]

# ---- Insert ENHANCED_PRODUCTS ----
# Re-search since positions shifted
ep_match2 = re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S)
obj_ep = ep_match2.group(1)
new_obj_ep = obj_ep[:-1] + ',\n' + js_obj_ep(new_ep) + '\n}'
html = html[:ep_match2.start(1)] + new_obj_ep + html[ep_match2.end(1):]

# ---- LAYOUT CHANGE 1: Remove forced page break ----
# The exact pattern in the template
old_pagebreak = '      <!-- Page break: product photos start on new page -->\n      <div style="page-break-after: always;"></div>\n'
new_pagebreak = '      <!-- Product photos flow naturally after line items; each image+spec pair stays together -->\n'
assert old_pagebreak in html, 'page break pattern not found'
html = html.replace(old_pagebreak, new_pagebreak, 1)

# ---- LAYOUT CHANGE 2: Add margin-top + page-break-after:avoid to Product Photos heading ----
old_heading = '<p style="margin:0 0 8pt 0; font-size:14pt; font-weight:bold; border-bottom:2pt solid #000; padding-bottom:4pt;">Product Photos</p>'
new_heading = '<p style="margin:14pt 0 8pt 0; font-size:14pt; font-weight:bold; border-bottom:2pt solid #000; padding-bottom:4pt; page-break-after:avoid;">Product Photos</p>'
assert old_heading in html, 'Product Photos heading not found'
html = html.replace(old_heading, new_heading, 1)

# ---- LAYOUT CHANGE 3: Add page-break-inside:avoid to photo cell <td> for extra safety ----
# The buildPhotoCellHtml returns: <td style="width:50%;vertical-align:top;padding:0 10pt 14pt 0;">
old_td = '<td style="width:50%;vertical-align:top;padding:0 10pt 14pt 0;">'
new_td = '<td style="width:50%;vertical-align:top;padding:0 10pt 14pt 0;page-break-inside:avoid;">'
# This appears in buildPhotoCellHtml function (the return statement)
count_td = html.count(old_td)
print('photo cell <td> occurrences:', count_td)
html = html.replace(old_td, new_td, 1)  # only the one in buildPhotoCellHtml

# ---- Backup + write ----
shutil.copyfile(HTML_PATH, BACKUP_PATH)
open(HTML_PATH, 'w', encoding='utf-8').write(html)

print()
print('=== DONE ===')
print('DETAILED_SPECS added:', len(new_ds))
print('ENHANCED added:', len(new_ep))
print('Layout: page break removed, photos heading updated, cell break-inside added')
print('Backup:', BACKUP_PATH)
