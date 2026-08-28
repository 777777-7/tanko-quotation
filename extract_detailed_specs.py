# -*- coding: utf-8 -*-
"""
增强产品规格 v5：从 raw_snippet 末尾提取结构化规格（Model No., Dimensions, Material, Handle, Loading），
并提取 Items Included。生成更详细的增强规格数据。
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

def extract_structured_specs(raw, combo):
    """从 raw_snippet 末尾提取结构化规格。"""
    specs = {}
    
    # 模式1: "Model No.\nVALUE\nDimensions：VALUE\nMaterial：VALUE\nHandle：VALUE\nLoading：VALUE\n..."
    # 找 "Model No." 后面的内容
    model_match = re.search(r'Model\s*No\.?\s*\n((?:[^\n]+\n?)+)', raw)
    if model_match:
        block = model_match.group(1)
        # 在这个 block 里找各个字段
        dim_match = re.search(r'Dimensions?\s*[：:]\s*([^\n]+)', block)
        if dim_match:
            specs['dimensions'] = dim_match.group(1).strip()
        
        mat_match = re.search(r'Material\s*[：:]\s*([^\n]+)', block)
        if mat_match:
            specs['material'] = mat_match.group(1).strip()
        
        handle_match = re.search(r'Handle\s*[：:]\s*([^\n]+)', block)
        if handle_match:
            specs['handle'] = handle_match.group(1).strip()
        
        # Loading 可能有多行
        load_match = re.search(r'Loading\s*[：:]\s*\n?((?:[^\n]+\n?)+)', block)
        if load_match:
            load_lines = [l.strip() for l in load_match.group(1).split('\n') if l.strip()]
            # 只取看起来像承重的行（包含 kg 或数字）
            load_lines = [l for l in load_lines if re.search(r'\d+\s*kg|per\s+\w+', l, re.I)]
            if load_lines:
                specs['loading'] = load_lines
    
    # 如果没找到，尝试从 raw_snippet 其他位置找
    if 'dimensions' not in specs:
        dim_match = re.search(r'Dimensions?\s*[：:]\s*([^\n]+)', raw)
        if dim_match:
            specs['dimensions'] = dim_match.group(1).strip()
    
    if 'material' not in specs:
        mat_match = re.search(r'Material\s*[：:]\s*([^\n]+)', raw)
        if mat_match:
            specs['material'] = mat_match.group(1).strip()
    
    if 'handle' not in specs:
        handle_match = re.search(r'Handle\s*[：:]\s*([^\n]+)', raw)
        if handle_match:
            specs['handle'] = handle_match.group(1).strip()
    
    return specs

def extract_items_included(raw, combo):
    """从 raw_snippet 提取配件/包含物品列表。"""
    items = []
    
    # 常见配件模式
    patterns = [
        (r'(\d+"x\d+"\s*PU\s*castors?)\b', None),
        (r'(\d+"\s*PU\s*castors?)\b', None),
        (r'(Central\s+Key\s+Lock)', 'Central Key Lock'),
        (r'(Safety[- ]?system)', 'Safety-system'),
        (r'(Safety[- ]?bar)', 'Safety-bar'),
        (r'(With\s+lock)', 'With lock'),
        (r'(Full\s+length\s+aluminum\s+handles?(?:\s*(?:and|&)\s*labels?)?)', 'Full length aluminum handles & labels'),
        (r'(Drawer\s+latch)', 'Drawer latch'),
        (r'(Division\s+boxes?)', 'Division boxes'),
        (r'(Adjustable\s+(?:dividers?|partitions?))', 'Adjustable dividers'),
        (r'(Perforated\s+(?:back\s+)?panel)', 'Perforated back panel'),
        (r'(Leveler\s+screws?)', 'Leveler screws'),
        (r'(ABS\s+handle)', 'ABS handle'),
        (r'(Storage\s+cabinet\s+with\s+shelf)', 'Storage cabinet with shelf'),
        (r'(Shelf\s+x\d+)', None),
        (r'(KPQ-[A-Z]\s*x\d+\s*set?)', None),
        (r'(TK-\d+\s*x\d+\s*pcs?)', None),
        (r'(Partition\s+x\d+\s*pcs?)', None),
        (r'(Wall\s+cabinet)', 'Wall cabinet'),
        (r'(Socket\s*\(.*?\))', None),
        (r'(Universal\s+socket)', 'Universal socket'),
        (r'(Stainless\s+steel\s+sink)', 'Stainless steel sink'),
        (r'(Wastebin)', 'Wastebin'),
        (r'(Tool\s+cabinet)', 'Tool cabinet'),
        (r'(Drawer\s+unit)', 'Drawer unit'),
        (r'(Parts\s+cabinet)', 'Parts cabinet'),
        (r'(Light\s+fixture)', 'Light fixture'),
        (r'(Air[- ]supporting\s+hydraulic)', 'Air-supporting hydraulic'),
    ]
    
    for pat, repl in patterns:
        for m in re.finditer(pat, raw, re.I):
            val = repl if repl else m.group(1)
            val = re.sub(r'\s+', ' ', val).strip()
            if val.lower() not in [i.lower() for i in items]:
                items.append(val)
    
    # 从 combo_labels 提取
    for key, val in combo.items():
        kl = key.lower()
        if kl in ['accessories', 'top', 'combination', 'panel']:
            if val and val not in ['None', 'N/A', '']:
                items.append(f'{key}: {val}')
    
    return items

def get_dimension_for_combo(raw, combo, specs):
    """根据 combo_labels 选择正确的尺寸。"""
    # 如果 specs 里已经有 dimensions，直接用
    if specs.get('dimensions'):
        return specs['dimensions']
    
    # 从 Width/Depth/Height 表选择
    cabinet = (combo.get('Cabinet') or combo.get('Cabinet (slide system)') or '').strip()
    
    cab_idx = 0
    cab_match = re.search(r'Cabinet\s*[：:]\s*\n((?:[^\n]+\n?)+)', raw)
    if cab_match and cabinet:
        cabs = [l.strip() for l in cab_match.group(1).strip().split('\n') if l.strip()]
        for i, c in enumerate(cabs):
            if cabinet.lower() in c.lower():
                cab_idx = i
                break
    
    def extract_vals(pattern):
        m = re.search(pattern, raw)
        return re.findall(r'([\d.]+)\s*mm', m.group(1)) if m else []
    
    widths = extract_vals(r'Width\s*\n((?:\s*[\d.]+\s*mm\s*\n?)+)')
    depths = extract_vals(r'Depth\s*\n((?:\s*[\d.]+\s*mm\s*\n?)+)')
    heights = extract_vals(r'Height\s*\n((?:\s*[\d.]+\s*mm\s*\n?)+)')
    
    if widths or depths or heights:
        idx = min(cab_idx, max(len(widths), len(depths), len(heights)) - 1)
        parts = []
        if widths: parts.append(f'W{widths[min(idx, len(widths)-1)]}')
        if depths: parts.append(f'D{depths[min(idx, len(depths)-1)]}')
        if heights: parts.append(f'H{heights[min(idx, len(heights)-1)]}')
        if parts:
            return ' x '.join(parts) + 'mm'
    
    return None

def generate_detailed_spec(sku, quo_name, variant_data, site_p):
    """生成详细的产品规格，用于照片页的规格表。"""
    if not variant_data:
        return None
    
    raw = variant_data['raw_snippet']
    ss = variant_data['static_specs']
    combo = variant_data['combo_labels']
    
    # 提取结构化规格
    specs = extract_structured_specs(raw, combo)
    
    # 尺寸
    dimension = get_dimension_for_combo(raw, combo, specs)
    if not dimension and ss.get('dimensions'):
        dimension = ss['dimensions']
    if not dimension and site_p and site_p.get('dimensions'):
        dimension = site_p['dimensions']
    
    # 材质
    material = specs.get('material') or ss.get('material') or (site_p.get('material') if site_p else None)
    
    # Handle
    handle = specs.get('handle')
    
    # Loading
    loading = specs.get('loading', [])
    if not loading:
        # 从 raw_snippet 提取
        for m in re.finditer(r'(\d+)\s*kg\s+load\s+capacity\s+per\s+(\w+)', raw, re.I):
            loading.append(f'{m.group(1)}kg per {m.group(2)}')
        for m in re.finditer(r'(\d+)\s*kg\s+load\s+capacity(?!\s+per)', raw, re.I):
            loading.append(f'{m.group(1)}kg (cabinet)')
        for m in re.finditer(r'(\d+)\s*kg\s*/\s*(\w+)', raw, re.I):
            loading.append(f'{m.group(1)}kg per {m.group(2)}')
    
    # Items included
    items = extract_items_included(raw, combo)
    
    # 颜色
    colour = None
    if site_p and site_p.get('color'):
        colour = site_p['color']
    else:
        for pat in [r'Colour\s*[:：]\s*\n?\s*([^\n]+)', r'Color\s*[:：]\s*\n?\s*([^\n]+)']:
            m = re.search(pat, raw, re.I)
            if m:
                c = m.group(1).strip()
                if c and len(c) < 50:
                    colour = c
                    break
    
    result = {
        'model_no': sku,
        'dimension': dimension,
        'material': material,
        'handle': handle,
        'loading': loading,
        'items_included': items,
        'colour': colour,
    }
    
    # 只在有至少2个字段有值时才返回
    filled = sum(1 for v in [dimension, material, handle, loading, items] if v)
    if filled < 2:
        return None
    
    return result

# 主流程
html = open('index.html', encoding='utf-8').read()
matches = re.findall(r'\{ sku: "([^"]+)", name: "([^"]+)", base_price: ([\d.]+) \}', html)

detailed = {}
for sku, name, bp in matches:
    name = name.replace('\\n', '\n')
    variant_data = all_variants.get(sku)
    site_p = site_sku_map.get(sku)
    if variant_data:
        result = generate_detailed_spec(sku, name, variant_data, site_p)
        if result:
            detailed[sku] = result

print(f'生成详细规格的 SKU 数: {len(detailed)}/{len(matches)}')

# 统计字段完整度
has_dim = sum(1 for v in detailed.values() if v['dimension'])
has_mat = sum(1 for v in detailed.values() if v['material'])
has_handle = sum(1 for v in detailed.values() if v['handle'])
has_load = sum(1 for v in detailed.values() if v['loading'])
has_items = sum(1 for v in detailed.values() if v['items_included'])
has_colour = sum(1 for v in detailed.values() if v['colour'])
print(f'字段完整度: dimension={has_dim}, material={has_mat}, handle={has_handle}, loading={has_load}, items={has_items}, colour={has_colour}')

with open('data/detailed_specs.json', 'w', encoding='utf-8') as f:
    json.dump(detailed, f, ensure_ascii=False, indent=2)

print('已保存到 data/detailed_specs.json')

print('\n=== 示例 ===')
for sku in ['ELS-274MA', 'EB-7051M', 'EA-7041', 'RY-01SA', 'WA-57TG7A']:
    if sku in detailed:
        print(f'\n{sku}:')
        print(json.dumps(detailed[sku], ensure_ascii=False, indent=2))
    else:
        print(f'\n{sku}: (无详细规格)')
