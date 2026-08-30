# -*- coding: utf-8 -*-
import re, json

html = open('index.html', encoding='utf-8').read()
ds = json.loads(re.search(r'const DETAILED_SPECS = (\{.*?\});', html, re.S).group(1))
ep = json.loads(re.search(r'const ENHANCED_PRODUCTS = (\{.*?\});', html, re.S).group(1))
skus = sorted(set(re.findall(r'sku:\s*"([^"]+)"', html)))

print('Total unique PRODUCT_DATA SKUs:', len(skus))

# Per-series analysis
import collections
def series(sku):
    m = re.match(r'^([A-Z]+)', sku)
    return m.group(1) if m else '?'

by_series = collections.defaultdict(list)
for s in skus:
    by_series[series(s)].append(s)

print()
print('=== Per-series coverage (series -> total, with-spec, without-spec) ===')
missing_report = []
for ser in sorted(by_series):
    items = by_series[ser]
    has_spec = [s for s in items if s in ds or s in ep]
    no_spec = [s for s in items if s not in ds and s not in ep]
    flag = '  <-- WKT/ME now FIXED' if ser in ('WKT','ME') else ''
    status = 'ALL OK' if not no_spec else 'MISSING %d' % len(no_spec)
    print('%-6s total=%-4d with-spec=%-4d without=%-4d %s%s' % (ser, len(items), len(has_spec), len(no_spec), status, flag))
    if no_spec:
        missing_report.extend(no_spec)

print()
print('=== WKT series coverage ===')
wkt = by_series.get('WKT', [])
for s in sorted(wkt):
    print('  %-22s DETAILED_SPECS=%s ENHANCED=%s' % (s, s in ds, s in ep))

print()
print('=== ME series coverage ===')
me = by_series.get('ME', [])
for s in sorted(me):
    print('  %-22s DETAILED_SPECS=%s ENHANCED=%s' % (s, s in ds, s in ep))

print()
print('=== Products STILL without spec at output (not WKT/ME) ===')
print('count:', len(missing_report) - (len(wkt)+len(me)))
rest = [s for s in missing_report if series(s) not in ('WKT','ME')]
print('remaining:', len(rest))
# group by series
rest_by_series = collections.Counter(series(s) for s in rest)
print('by series:', dict(sorted(rest_by_series.items())))
print('first 60:', rest[:60])
