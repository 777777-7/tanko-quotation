# -*- coding: utf-8 -*-
"""
Surgical addition of WKT & ME series specs into tanko-quotation/index.html.

Only inserts new entries into the inline `ENHANCED_PRODUCTS` and `DETAILED_SPECS`
objects. Does NOT touch any other content in the file.

Spec data verified against:
  - tanko-quotation/data/detailed_specs.json
  - tanko-website-1-/products.json, product_content.json, product_content_v2.json, built docs pages
  - live tanko.tw product pages (wkt_5102, me)
"""
import json, re, shutil, sys

HTML_PATH = 'index.html'
BACKUP_PATH = 'index.html.bak-specwktme'

# ---- WKT & ME DETAILED_SPECS (format matches other products: model_no, dimension, material, handle, colour, loading, items_included) ----
def wkt_spec(sku, top, shelf=False, tray=False):
    loading = ["Workbench loading: 100kg", "Drawer loading: 35kg", "Roll holder loading: 20kg"]
    items = ["Roll holder", "Tabletop cutter", "Perforated board panel"]
    if shelf:
        loading.append("Shelf loading: 20kg")
        items.append("Shelf")
    if tray:
        items.append("Tray (WPK-21)")
    return {
        "model_no": sku,
        "dimension": "W1500xD755xH965-1165mm",
        "material": top,
        "handle": "",
        "colour": None,
        "loading": loading,
        "items_included": items,
    }

new_ds = {}
# WKT (Laminate F / Wood W) x (base / +shelf / +shelf+tray)
new_ds["WKT-5102F"] = wkt_spec("WKT-5102F", "Laminate(F)")
new_ds["WKT-5102F1"] = wkt_spec("WKT-5102F1", "Laminate(F)", shelf=True)
new_ds["WKT-5102F1+WPK-21"] = wkt_spec("WKT-5102F1+WPK-21", "Laminate(F)", shelf=True, tray=True)
new_ds["WKT-5102W"] = wkt_spec("WKT-5102W", "Wood(W)")
new_ds["WKT-5102W1"] = wkt_spec("WKT-5102W1", "Wood(W)", shelf=True)
new_ds["WKT-5102W1+WPK-21"] = wkt_spec("WKT-5102W1+WPK-21", "Wood(W)", shelf=True, tray=True)
# ME
new_ds["ME-321"] = {
    "model_no": "ME-321",
    "dimension": "W970xD700xH2000mm",
    "material": "Steel",
    "handle": "",
    "colour": None,
    "loading": ["80kg per pull-out shelf"],
    "items_included": ["Pull-out shelf adjustable every 100mm", "Perforated board with hooks", "Configuration: Independent"],
}
new_ds["ME-322"] = {
    "model_no": "ME-322",
    "dimension": "W900xD700xH2000mm",
    "material": "Steel",
    "handle": "",
    "colour": None,
    "loading": ["80kg per pull-out shelf"],
    "items_included": ["Pull-out shelf adjustable every 100mm", "Perforated board with hooks", "Configuration: Linkable"],
}

# ---- WKT & ME ENHANCED_PRODUCTS (multi-line name strings; \n = newline) ----
def wkt_enh(sku, top, acc, load_extra):
    lines = [
        "Packing Station",
        "Top: " + top,
        "Accessories: " + acc,
        "Material: " + top,
        "Size: W1500xD755xH965-1165mm",
    ]
    loads = ["Workbench = 100kg", "Drawer = 35kg", "Roll holder = 20kg"]
    if load_extra:
        loads.append(load_extra)
    lines.append("Load cap.: " + ", ".join(loads))
    return "\n".join(lines)

new_ep = {}
new_ep["WKT-5102F"] = wkt_enh("WKT-5102F", "Laminate(F)", "None", None)
new_ep["WKT-5102F1"] = wkt_enh("WKT-5102F1", "Laminate(F)", "Shelf", "Shelf = 20kg")
new_ep["WKT-5102F1+WPK-21"] = wkt_enh("WKT-5102F1+WPK-21", "Laminate(F)", "Shelf+Tray", "Shelf = 20kg")
new_ep["WKT-5102W"] = wkt_enh("WKT-5102W", "Wood(W)", "None", None)
new_ep["WKT-5102W1"] = wkt_enh("WKT-5102W1", "Wood(W)", "Shelf", "Shelf = 20kg")
new_ep["WKT-5102W1+WPK-21"] = wkt_enh("WKT-5102W1+WPK-21", "Wood(W)", "Shelf+Tray", "Shelf = 20kg")
new_ep["ME-321"] = "Pull-out Rack\nType: A type\nPull-out Rack: Independent\nMaterial: Steel\nSize: W970xD700xH2000mm\nLoad cap.: 80kg per pull-out shelf"
new_ep["ME-322"] = "Pull-out Rack\nType: A type\nPull-out Rack: Linkable\nMaterial: Steel\nSize: W900xD700xH2000mm\nLoad cap.: 80kg per pull-out shelf"

# ---- JSON serialization matching existing inline style ----
def js_obj(entries, is_ds):
    parts = []
    for k in sorted(entries):
        if is_ds:
            v = json.dumps(entries[k], ensure_ascii=False, separators=(", ", ": "))
            parts.append('"%s": %s' % (k, v))
        else:
            v = json.dumps(entries[k], ensure_ascii=False)
            parts.append('"%s": %s' % (k, v))
    return ",\n".join(parts)

html = open(HTML_PATH, encoding='utf-8').read()

# --- Insert into DETAILED_SPECS ---
m_ds = re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S)
assert m_ds, 'DETAILED_SPECS not found'
obj_ds = m_ds.group(1)
ds = json.loads(obj_ds)
assert all(k not in ds for k in new_ds), 'some WKT/ME already present in DETAILED_SPECS'
new_obj_ds = obj_ds[:-1] + ',\n' + js_obj(new_ds, True) + '\n}'
html = html[:m_ds.start(1)] + new_obj_ds + html[m_ds.end(1):]

# --- Insert into ENHANCED_PRODUCTS ---
m_ep = re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S)
assert m_ep, 'ENHANCED_PRODUCTS not found'
obj_ep = m_ep.group(1)
ep = json.loads(obj_ep)
assert all(k not in ep for k in new_ep), 'some WKT/ME already present in ENHANCED_PRODUCTS'
new_obj_ep = obj_ep[:-1] + ',\n' + js_obj(new_ep, False) + '\n}'
html = html[:m_ep.start(1)] + new_obj_ep + html[m_ep.end(1):]

# --- Backup + write ---
shutil.copyfile(HTML_PATH, BACKUP_PATH)
open(HTML_PATH, 'w', encoding='utf-8').write(html)

print('Inserted DETAILED_SPECS entries:', len(new_ds))
print('Inserted ENHANCED_PRODUCTS entries:', len(new_ep))
print('Backup written to', BACKUP_PATH)
