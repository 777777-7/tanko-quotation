# -*- coding: utf-8 -*-
"""
增强产品规格 v4：修复 Size 重复检测，合并换行，正确选择尺寸。
"""
import json, re, sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', errors='replace', buffering=1)

variants = json.load(open(r'data\tanko_variants.json', encoding='utf-8'))
site_products = json.load(open(r'data\products.json', encoding='utf-8'))
site_sku_map = {p['sku']: p for p in site_products}

all_variants = {}
for fam in variants:
    ss = fam.get('static_specs', {}) or {}
    raw = (ss.get('raw_snippet', '') or '').replace('\r', '')
    for v in fam.get('variants', []):
        sku = v.get('sku_id') or v.get('model_no')
        if sku:
            all_variants[sku] = {
                'family': fam.get('family', ''),
                'combo_labels': v.get('combo_labels', {}),
                'static_specs': ss,
                'raw_snippet': raw,
            }

def has_keyword(text, keywords):
    """检查文本是否包含任一关键词（不区分大小写）。"""
    low = text.lower()
    return any(k in low for k in keywords)

def get_dimension(raw, ss, site_p, combo):
    """获取最佳尺寸，返回 None 或标准化字符串。"""
    # 1. static_specs.dimensions
    dim = (ss.get('dimensions') or '').strip()
    if dim and re.search(r'[hw]\d', dim, re.I):
        return dim
    
    # 2. site products.json
    if site_p:
        d = (site_p.get('dimensions') or '').strip()
        if d and re.search(r'[hw]\d', d, re.I):
            return d
    
    # 3. 从 raw_snippet 的 Width/Depth/Height 表
    cabinet = (combo.get('Cabinet') or combo.get('Cabinet (slide system)') or '').strip()
    
    # 找 Cabinet 选项列表和索引
    cab_idx = 0
    cab_match = re.search(r'Cabinet\s*[：:]\s*\n((?:[^\n]+\n?)+)', raw)
    if cab_match and cabinet:
        cabs = [l.strip() for l in cab_match.group(1).strip().split('\n') if l.strip()]
        for i, c in enumerate(cabs):
            if cabinet.lower() in c.lower() or c.lower() in cabinet.lower():
                cab_idx = i
                break
    
    def extract_values(pattern):
        m = re.search(pattern, raw)
        if not m:
            return []
        return re.findall(r'([\d.]+)\s*mm', m.group(1))
    
    widths = extract_values(r'Width\s*\n((?:\s*[\d.]+\s*mm\s*\n?)+)')
    depths = extract_values(r'Depth\s*\n((?:\s*[\d.]+\s*mm\s*\n?)+)')
    heights = extract_values(r'Height\s*\n((?:\s*[\d.]+\s*mm\s*\n?)+)')
    
    if widths or depths or heights:
        idx = min(cab_idx, max(len(widths), len(depths), len(heights)) - 1)
        parts = []
        if widths: parts.append(f'W{widths[min(idx, len(widths)-1)]}')
        if depths: parts.append(f'D{depths[min(idx, len(depths)-1)]}')
        if heights: parts.append(f'H{heights[min(idx, len(heights)-1)]}')
        if parts:
            return ' x '.join(parts) + 'mm'
    
    return None

def get_loads(raw, ss, site_p):
    """提取承重列表，去重。"""
    loads = []
    lc = (ss.get('load_capacity') or '').strip()
    if lc:
        loads.append(lc)
    if site_p and site_p.get('load_capacity'):
        loads.append(site_p['load_capacity'])
    
    # "100kg load capacity per drawer"
    for m in re.finditer(r'(\d+)\s*kg\s+load\s+capacity\s+per\s+(\w+)', raw, re.I):
        loads.append(f'{m.group(2).capitalize()} = {m.group(1)}kg/each')
    # "1000kg load capacity" (not followed by per)
    for m in re.finditer(r'(\d+)\s*kg\s+load\s+capacity(?!\s+per)', raw, re.I):
        loads.append(f'Cabinet = {m.group(1)}kg')
    # "200kg / shelf"
    for m in re.finditer(r'(\d+)\s*kg\s*/\s*(\w+)', raw, re.I):
        loads.append(f'{m.group(2).capitalize()} = {m.group(1)}kg')
    
    seen = set()
    unique = []
    for l in loads:
        key = re.sub(r'[\s,/=.]', '', l.lower())
        if key not in seen:
            seen.add(key)
            unique.append(l)
    return unique

def get_colour(raw, ss, site_p):
    if site_p and site_p.get('color'):
        return site_p['color']
    for pat in [r'Colour\s*[:：]\s*\n?\s*([^\n]+)', r'Color\s*[:：]\s*\n?\s*([^\n]+)']:
        m = re.search(pat, raw, re.I)
        if m:
            c = m.group(1).strip()
            if c and len(c) < 50 and not c.startswith('Request'):
                return c
    return None

def get_material(raw, ss, site_p):
    if ss.get('material'):
        return ss['material']
    if site_p and site_p.get('material'):
        return site_p['material']
    return None

def get_accessories(raw, combo):
    """提取配件列表，去重（包含关系去重）。"""
    accessories = []
    patterns = [
        (r'(\d+"x\d+"\s*PU\s*castors?)', None),
        (r'(\d+"\s*PU\s*castors?)', None),
        (r'(Central\s+Key\s+Lock)', 'Central Key Lock'),
        (r'(Safety[- ]?system)', 'Safety-system'),
        (r'(Safety[- ]?bar)', 'Safety-bar'),
        (r'(With\s+lock)', 'With lock'),
        (r'(Full\s+length\s+aluminum\s+handles?(?:\s*(?:and|&)\s*labels?)?)', 'Full length aluminum handles & labels'),
        (r'(Drawer\s+latch)', 'Drawer latch'),
        (r'(Division\s+boxes?)', 'Division boxes'),
        (r'(Adjustable\s+dividers?)', 'Adjustable dividers'),
        (r'(Perforated\s+(?:back\s+)?panel)', 'Perforated back panel'),
        (r'(Leveler\s+screws?)', 'Leveler screws'),
        (r'(Standard\s+drawer\s+\d+%\s+extention)', lambda m: m.group(1).replace('\n', ' ')),
        (r'(Epoxy\s+powder\s+coating)', 'Epoxy powder coating'),
    ]
    for pat, repl in patterns:
        m = re.search(pat, raw, re.I)
        if m:
            if callable(repl):
                val = repl(m)
            elif repl:
                val = repl
            else:
                val = m.group(1)
            val = re.sub(r'\s+', ' ', val).strip()
            accessories.append(val)
    
    # 包含关系去重
    unique = []
    for a in accessories:
        a_low = a.lower().replace(' ', '')
        found = False
        for i, u in enumerate(unique):
            u_low = u.lower().replace(' ', '')
            if a_low == u_low:
                found = True
                break
            if a_low in u_low:
                found = True  # a 是 u 的子串，保留 u
                break
            if u_low in a_low:
                unique[i] = a  # u 是 a 的子串，替换为 a
                found = True
                break
        if not found:
            unique.append(a)
    return unique

def enhance_spec(sku, quo_name, variant_data, site_p):
    """以 quo_name 为基础，补充缺失的规格。"""
    if not variant_data:
        return None
    
    raw = variant_data['raw_snippet']
    ss = variant_data['static_specs']
    combo = variant_data['combo_labels']
    
    lines = [l.strip() for l in quo_name.split('\n') if l.strip()]
    quo_text = quo_name.lower()
    
    # 检查已有信息
    has_size = has_keyword(quo_name, ['size:', 'size（', 'w', 'd', 'h']) and re.search(r'[hw]\d+', quo_name, re.I)
    has_cw = has_keyword(quo_name, ['c/w', 'c/w:'])
    has_load = has_keyword(quo_name, ['weight hold', 'load cap', 'load capacity', 'kg/'])
    has_colour = has_keyword(quo_name, ['colour:', 'color:'])
    has_material = has_keyword(quo_name, ['stainless steel', 'epoxy powder'])
    
    added = []
    
    # 补充 Size
    if not has_size:
        dim = get_dimension(raw, ss, site_p, combo)
        if dim:
            added.append(f'Size: {dim}')
    
    # 补充 C/w 配件
    accessories = get_accessories(raw, combo)
    new_acc = [a for a in accessories if a.lower().replace(' ', '') not in quo_text]
    if new_acc:
        if has_cw:
            for i, line in enumerate(lines):
                if line.lower().startswith('c/w'):
                    lines[i] = line + ', ' + ', '.join(new_acc)
                    break
        else:
            added.append('C/w: ' + ', '.join(new_acc))
    
    # 补充 Load capacity
    if not has_load:
        loads = get_loads(raw, ss, site_p)
        if loads:
            added.append('Load cap.: ' + ', '.join(loads))
    
    # 补充 Colour
    if not has_colour:
        colour = get_colour(raw, ss, site_p)
        if colour and colour.lower() not in quo_text:
            added.append(f'Colour: {colour}')
    
    # 补充 Material
    if not has_material:
        material = get_material(raw, ss, site_p)
        if material and material.lower() not in quo_text:
            added.append(f'Material: {material}')
    
    if not added:
        return None
    
    return '\n'.join(lines + added)

# 主流程
html = open('index.html', encoding='utf-8').read()
matches = re.findall(r'\{ sku: "([^"]+)", name: "([^"]+)", base_price: ([\d.]+) \}', html)

enhanced = {}
for sku, name, bp in matches:
    # JS string literals use \n as two chars; convert to real newlines.
    name = name.replace('\\n', '\n')
    variant_data = all_variants.get(sku)
    site_p = site_sku_map.get(sku)
    if variant_data:
        result = enhance_spec(sku, name, variant_data, site_p)
        if result:
            enhanced[sku] = result

print(f'生成增强规格的 SKU 数: {len(enhanced)}/{len(matches)}')

with open('data/enhanced_products.json', 'w', encoding='utf-8') as f:
    json.dump(enhanced, f, ensure_ascii=False, indent=2)

print('已保存到 data/enhanced_products.json')

print('\n=== 示例 ===')
for sku in ['EB-7051M', 'ELS-274MA', 'EA-7041', 'RY-01SA', 'WA-57TG7A']:
    quo = next((n for s, n, _ in matches if s == sku), 'N/A')
    print(f'\n--- {sku} ---')
    print(f'原始: {repr(quo)}')
    if sku in enhanced:
        print(f'增强: {repr(enhanced[sku])}')
    else:
        print('增强: (无补充)')
