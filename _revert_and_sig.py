# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

# ---- 1. Revert Download Word button ----
# Remove button HTML
old_btn = ('    <button id="generateDocBtn" type="button" class="btn-generate">Generate Document</button>\n'
           '    <button id="downloadWordBtn" type="button" class="btn-generate" style="margin-left:10px; background:#2b7a3b;">Download Word (.doc)</button>\n'
           '  </section>')
new_btn = '    <button id="generateDocBtn" type="button" class="btn-generate">Generate Document</button>\n  </section>'
assert old_btn in html, 'button HTML not found'
html = html.replace(old_btn, new_btn, 1)

# Remove el reference
old_el = '  generateDocBtn: document.getElementById("generateDocBtn"),\n  downloadWordBtn: document.getElementById("downloadWordBtn"),'
new_el = '  generateDocBtn: document.getElementById("generateDocBtn"),'
assert old_el in html, 'el reference not found'
html = html.replace(old_el, new_el, 1)

# Remove handleDownloadWord function (from "async function handleDownloadWord()" to just before "async function handleGenerateDocument()")
import re
fn_pattern = r'async function handleDownloadWord\(\) \{.*?\n\}\n\n'
m = re.search(fn_pattern, html, re.S)
assert m, 'handleDownloadWord function not found'
html = html[:m.start()] + html[m.end():]

# Remove event listener
old_listener = ('el.generateDocBtn.addEventListener("click", handleGenerateDocument);\n'
                'el.downloadWordBtn.addEventListener("click", handleDownloadWord);')
new_listener = 'el.generateDocBtn.addEventListener("click", handleGenerateDocument);'
assert old_listener in html, 'listener not found'
html = html.replace(old_listener, new_listener, 1)

print('Revert checks:')
print('  downloadWordBtn button removed:', 'downloadWordBtn' not in html)
print('  handleDownloadWord removed:', 'handleDownloadWord' not in html)

# ---- 2. Change signature font to Viner Hand ITC ----
# The signature line in the document template:
# <p style="font-style:italic; font-size:11pt; margin:8pt 0 0;">Kenny LAI</p>
old_sig = '<p style="font-style:italic; font-size:11pt; margin:8pt 0 0;">Kenny LAI</p>'
new_sig = '<p style="font-family:\'Viner Hand ITC\', cursive; font-size:18pt; margin:8pt 0 0; color:#000;">Kenny LAI</p>'
assert old_sig in html, 'signature line not found'
html = html.replace(old_sig, new_sig, 1)

print()
print('Signature font changed:')
print('  Viner Hand ITC present:', 'Viner Hand ITC' in html)

open('index.html', 'w', encoding='utf-8').write(html)
print()
print('Done.')
