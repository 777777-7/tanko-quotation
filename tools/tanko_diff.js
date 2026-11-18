// Compare a tanko_scrape.js result with PRODUCT_DATA / PRODUCT_IMAGES in index.html.
// Usage: node tools/tanko_diff.js <site.json> <out.json>
// Writes { siteModels: [{model, slug, family, labels, images}], newModels, missingOnSite, imageMap }.
const fs = require("fs");
const [siteFile, outFile] = process.argv.slice(2);
const site = JSON.parse(fs.readFileSync(siteFile, "utf8"));
const html = fs.readFileSync("index.html", "utf8");

const norm = (s) => String(s).toUpperCase().replace(/\s+/g, "").replace(/[()]/g, "");
const skus = [...html.matchAll(/\{ sku: "([^"]+)"/g)].map((m) => m[1]);
const skuByNorm = new Map(skus.map((k) => [norm(k), k]));
const a = html.indexOf("const PRODUCT_IMAGES = {");
const imgs = Object.fromEntries([...html.slice(a, html.indexOf("};", a)).matchAll(/"([^"]+)": "([^"]+)"/g)].map((m) => [m[1], m[2]]));

const siteModels = new Map();
for (const f of site) {
  for (const c of f.combos || []) {
    const i = c.note.indexOf("Model No.");
    const model = i >= 0 ? c.note.slice(i + 1).join(" ").trim() : "";
    if (!model) continue;
    const k = norm(model);
    if (!siteModels.has(k)) siteModels.set(k, { model, slug: f.slug, family: f.familyName, sub: f.subcategory, cat: f.category, levelLabels: f.levelLabels, labels: c.labels, images: c.images, note: c.note });
  }
  // single-model families with no option combos
  if (!(f.combos || []).length && f.familyCode) {
    const k = norm(f.familyCode);
    if (!siteModels.has(k)) siteModels.set(k, { model: f.familyCode, slug: f.slug, family: f.familyName, sub: f.subcategory, cat: f.category, levelLabels: [], labels: [], images: f.pageImages.filter((u) => /catalog_package_b|catalog_products_b/.test(u)), note: [], single: true });
  }
}
const list = [...siteModels.values()];
const newModels = list.filter((m) => !skuByNorm.has(norm(m.model)));
const siteNorm = new Set(siteModels.keys());
const missingOnSite = skus.filter((k) => !siteNorm.has(norm(k)));
const matched = list.filter((m) => skuByNorm.has(norm(m.model))).map((m) => ({ sku: skuByNorm.get(norm(m.model)), localImage: imgs[skuByNorm.get(norm(m.model))] || null, siteImage: m.images[0] || null }));
fs.writeFileSync(outFile, JSON.stringify({ siteModels: list, newModels, missingOnSite, matched }, null, 1));
console.log("site models", list.length, "matched", matched.length, "new", newModels.length, "ours not on site", missingOnSite.length);
