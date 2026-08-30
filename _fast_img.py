# -*- coding: utf-8 -*-
html = open('index.html', encoding='utf-8').read()

old_fn = (
    'async function resolveImageForDoc(relPath) {\n'
    '  if (!relPath) return null;\n'
    '  try {\n'
    '    const dataUri = await urlToDataUri(relPath);\n'
    '    if (dataUri) return dataUri;\n'
    '  } catch (e) {\n'
    '    console.warn("fetch failed for", relPath, e);\n'
    '  }\n'
    '  // Fallback: try with cache-busting\n'
    '  try {\n'
    '    const dataUri = await urlToDataUri(relPath + "?t=" + Date.now());\n'
    '    if (dataUri) return dataUri;\n'
    '  } catch (e) {}\n'
    '  // Last resort: absolute URL\n'
    '  return assetAbsoluteUrl(relPath);\n'
    '}'
)

new_fn = (
    'async function resolveImageForDoc(relPath) {\n'
    '  if (!relPath) return null;\n'
    '  // Use direct URL instead of base64 data-URI — much faster to load.\n'
    '  // The document <base href> resolves relative paths correctly.\n'
    '  return assetAbsoluteUrl(relPath);\n'
    '}'
)

assert old_fn in html, 'resolveImageForDoc not found'
html = html.replace(old_fn, new_fn, 1)

open('index.html', 'w', encoding='utf-8').write(html)
print('Done: resolveImageForDoc now returns direct URL (no base64 conversion)')
