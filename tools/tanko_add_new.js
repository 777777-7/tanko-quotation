// Add Tanko models that are on the website but not yet in index.html:
// builds PRODUCT_DATA / DETAILED_SPECS / PRODUCT_IMAGES entries, downloads
// each model's main photo into assets/product/, and patches index.html.
// Usage: node tools/tanko_add_new.js <site.json> <diff.json> [--dry]
const fs = require("fs");
const path = require("path");
const [siteFile, diffFile, flag] = process.argv.slice(2);
const DRY = flag === "--dry";
const site = JSON.parse(fs.readFileSync(siteFile, "utf8"));
const diff = JSON.parse(fs.readFileSync(diffFile, "utf8"));
const bySlug = Object.fromEntries(site.map((f) => [f.slug, f]));
const norm = (s) => String(s).toUpperCase().replace(/\s+/g, "").replace(/[()]/g, "");
const clean = (s) => String(s).replace(/\s+/g, " ").replace(/\s*：\s*/g, ": ").trim();

// Value after "Label：" in token i, or in token i+1 when the token is just the label.
function valueAt(body, i) {
  const t = body[i];
  const m = t.match(/^[^：:]+[：:]\s*(.*)$/);
  if (m && m[1].trim()) return m[1].trim();
  return (body[i + 1] || "").trim();
}

// Find the spec block for a model in the page's spec table.
function findSpecs(f, model) {
  const body = f.body;
  const base = model.split("+")[0].trim();
  const nb = norm(base);
  const candidates = [nb, nb.replace(/G$/, "")];
  const hit = (t) => candidates.includes(norm(t)) || norm(t) === nb.replace(/G$/, "") + "G";
  // codes are sometimes split over two tokens on the page ("FD" | "A-309(G)")
  let at = body.findIndex((t, k) => hit(t) || hit(t + (body[k + 1] || "")));
  if (at < 0 && /M$/.test(nb)) {
    // "Mobile" variants are often listed under a "(Mobile)" heading with the base code.
    const mob = body.findIndex((t) => /mobile/i.test(t) && body.indexOf("Specification") < body.indexOf(t));
    if (mob >= 0) at = mob;
  }
  if (at < 0) at = body.indexOf("Specification");
  const out = { dimension: "", material: "", loading: [], items: [] };
  for (let k = at + 1; k < Math.min(body.length, at + 40); k++) {
    const t = body[k];
    if (t === "Model No." && k > at + 1 && out.dimension) break;
    if (/^Dimensions?\s*[：:]/i.test(t) && !out.dimension) out.dimension = valueAt(body, k).replace(/\s+/g, "");
    else if (/^Material\s*[：:]/i.test(t) && !out.material) out.material = valueAt(body, k);
    else if (/^Load(ing)?\s*[：:]/i.test(t)) out.loading.push(clean(valueAt(body, k)));
    else if (/^Items included\s*[：:]/i.test(t)) out.items.push(clean(valueAt(body, k)));
  }
  return out;
}

const fileFor = (sku, url) => sku.replace(/[^A-Za-z0-9.+-]/g, "_") + path.extname(new URL(url).pathname).toLowerCase();

(async () => {
  const products = [], specs = {}, images = {};
  for (const m of diff.newModels) {
    const f = bySlug[m.slug];
    const sku = m.model.replace(/\s*\+\s*/g, " + ");
    const sp = findSpecs(f, m.model);
    const lines = [f.familyName];
    if (f.subcategory && f.subcategory !== f.familyName) lines.push(f.subcategory);
    m.labels.forEach((v, i) => {
      const lab = f.levelLabels[i];
      if (!lab || !v) return;
      if (/^dimensions?$/i.test(lab)) { if (!sp.dimension) sp.dimension = v; return; }
      lines.push(lab + ": " + v);
    });
    if (sp.material) lines.push("Material: " + sp.material);
    if (sp.dimension) lines.push("Size: " + sp.dimension);
    products.push({ sku, name: lines.join("\n") });
    specs[sku] = { model_no: sku, dimension: sp.dimension, material: sp.material, handle: "", colour: null, loading: sp.loading, items_included: sp.items, source: f.url };
    const img = (m.images || [])[0];
    if (img) {
      const file = fileFor(sku, img);
      const dest = path.join("assets/product", file);
      if (!DRY && !fs.existsSync(dest)) {
        const r = await fetch(img, { headers: { "User-Agent": "Mozilla/5.0" } });
        if (r.ok) fs.writeFileSync(dest, Buffer.from(await r.arrayBuffer()));
      }
      if (DRY || fs.existsSync(dest)) images[sku] = file;
    }
  }
  if (DRY) { products.slice(0, 200).forEach((p) => console.log(p.sku, "=>", p.name.replace(/\n/g, " / "))); return; }

  let html = fs.readFileSync("index.html", "utf8");
  const esc = (s) => JSON.stringify(s);
  const pd = products.map((p) => "  { sku: " + esc(p.sku) + ", name: " + esc(p.name) + ", base_price: 0.0 },").join("\n");
  const marker = "  // Priced directly in RM (no USD mark-up conversion).";
  if (!html.includes(marker)) throw new Error("PRODUCT_DATA end marker not found");
  html = html.replace(marker, "  // Added from tanko.com.tw (" + new Date().toISOString().slice(0, 10) + ")\n" + pd + "\n" + marker);
  const imgLines = Object.entries(images).map(([k, v]) => "  " + esc(k) + ": " + esc(v) + ",").join("\n");
  html = html.replace("const PRODUCT_IMAGES = {\n", "const PRODUCT_IMAGES = {\n" + imgLines + "\n");
  const specStr = Object.entries(specs).map(([k, v]) => { const { source, ...rest } = v; return esc(k) + ": " + JSON.stringify(rest); }).join(", ");
  html = html.replace("const DETAILED_SPECS = {", "const DETAILED_SPECS = {" + specStr + ", ");
  fs.writeFileSync("index.html", html);
  console.log("added products", products.length, "images", Object.keys(images).length);
})();
