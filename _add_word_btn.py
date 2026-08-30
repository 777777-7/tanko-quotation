# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

# 1. Add the button HTML next to Generate Document
old_btn = '    <button id="generateDocBtn" type="button" class="btn-generate">Generate Document</button>\n  </section>'
new_btn = ('    <button id="generateDocBtn" type="button" class="btn-generate">Generate Document</button>\n'
           '    <button id="downloadWordBtn" type="button" class="btn-generate" style="margin-left:10px; background:#2b7a3b;">Download Word (.doc)</button>\n'
           '  </section>')
assert old_btn in html, 'button HTML not found'
html = html.replace(old_btn, new_btn, 1)

# 2. Add button reference to el object
old_el = '  generateDocBtn: document.getElementById("generateDocBtn"),'
new_el = '  generateDocBtn: document.getElementById("generateDocBtn"),\n  downloadWordBtn: document.getElementById("downloadWordBtn"),'
assert old_el in html, 'el.generateDocBtn not found'
html = html.replace(old_el, new_el, 1)

# 3. Add handleDownloadWord function (insert before handleGenerateDocument)
old_fn_start = 'async function handleGenerateDocument() {'
new_fn = ('''async function handleDownloadWord() {
  const customer = {
    name: el.customerName.value.trim(),
    contact: el.customerContact.value.trim(),
    address: el.customerAddress.value.trim(),
    attn: el.customerAttn.value.trim(),
  };

  if (!customer.name) {
    alert("Please enter the customer name before generating the document.");
    return;
  }
  if (quoteItems.length === 0) {
    alert("Add at least one item to the quote first.");
    return;
  }

  const originalLabel = el.downloadWordBtn.textContent;
  el.downloadWordBtn.disabled = true;
  el.downloadWordBtn.textContent = "Generating...";

  try {
    const serial = nextQuotationSerial();
    const delivery = getDeliveryFee();
    const docHtml = await buildQuotationHtml(customer, quoteItems, serial, delivery);

    // Save as .doc (Word-compatible HTML). WPS / Word opens it for editing.
    const blob = new Blob([docHtml], { type: "application/msword" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Quotation_" + serial.replace(/[^a-zA-Z0-9]/g, "_") + ".doc";
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error(error);
    alert("Failed to generate the Word document: " + error.message);
  } finally {
    el.downloadWordBtn.disabled = false;
    el.downloadWordBtn.textContent = originalLabel;
  }
}

''')
assert old_fn_start in html, 'handleGenerateDocument not found'
html = html.replace(old_fn_start, new_fn + old_fn_start, 1)

# 4. Add event listener
old_listener = 'el.generateDocBtn.addEventListener("click", handleGenerateDocument);'
new_listener = ('el.generateDocBtn.addEventListener("click", handleGenerateDocument);\n'
                'el.downloadWordBtn.addEventListener("click", handleDownloadWord);')
assert old_listener in html, 'generateDocBtn listener not found'
html = html.replace(old_listener, new_listener, 1)

open('index.html', 'w', encoding='utf-8').write(html)

print('Done. Added:')
print('  - Download Word (.doc) button')
print('  - handleDownloadWord function')
print('  - event listener')
print()
print('Button present:', 'downloadWordBtn' in html)
print('Function present:', 'handleDownloadWord' in html)
print('Listener present:', 'el.downloadWordBtn.addEventListener' in html)
