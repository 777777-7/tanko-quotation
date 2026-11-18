// Scrape every tanko.com.tw/en product family: page text (features + spec
// table), spec options, and for every option combo the Model No. and photos.
// Usage: node tools/tanko_scrape.js <slugs.json> <out.json>
const fs = require("fs");
const [slugsFile, outFile] = process.argv.slice(2);
const UA = { "User-Agent": "Mozilla/5.0" };
const EN = "https://www.tanko.com.tw/en/";

async function get(url, tries = 3) {
  for (let i = 0; i < tries; i++) {
    try {
      const r = await fetch(url, { headers: UA });
      if (r.ok) return await r.text();
    } catch (e) { /* retry */ }
    await new Promise((res) => setTimeout(res, 800 * (i + 1)));
  }
  return "";
}

const decode = (s) => s.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&deg;/g, "°")
  .replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
const textLines = (h) => decode(h.replace(/<script[\s\S]*?<\/script>/g, " ").replace(/<style[\s\S]*?<\/style>/g, " ")
  .replace(/<!--[\s\S]*?-->/g, " ").replace(/<[^>]+>/g, "\n")).split("\n").map((s) => s.trim()).filter(Boolean);

function parseLevels(html) {
  const levels = [];
  const specList = (html.match(/class="specList"[\s\S]*?(?=Request A Quote|class="btnBox|<\/ul>\s*<\/div>)/) || [""])[0];
  for (const lv of [1, 2]) {
    const re = new RegExp('<input[^>]*name="data_spec' + lv + '_list\\[\\]"[^>]*data-id="(\\d+)"[^>]*>\\s*<label[^>]*>([\\s\\S]*?)</label>', "g");
    const opts = [...html.matchAll(re)].map((m) => ({ id: m[1], label: decode(m[2].replace(/<[^>]+>/g, "")).trim() }));
    if (!opts.length) {
      // fallback: label may precede input or sit in a wrapping element
      const ids = [...html.matchAll(new RegExp('name="data_spec' + lv + '_list\\[\\]"[^>]*data-id="(\\d+)"', "g"))].map((m) => m[1]);
      ids.forEach((id) => opts.push({ id, label: "" }));
    }
    levels.push(opts);
  }
  return { levels, specList };
}

async function scrapeFamily(slug) {
  const url = EN + "products-detail/" + slug + "/";
  const html = await get(url);
  if (!html) return { slug, url, error: "fetch failed" };
  const indexId = (html.match(/indexId=(\d+)/) || [])[1] || null;
  const title = decode((html.match(/<title>([^<]*)/) || [, ""])[1]).trim();
  const lines = textLines(html);
  const { levels } = parseLevels(html);
  const iq = lines.indexOf("Request A Quote");
  const bread = (html.match(/>HOME<\/a>([\s\S]*?)<!--bread end-->/) || [, ""])[1].replace(/<!--[\s\S]*?-->/g, "");
  const crumbs = [...bread.matchAll(/<a [^>]*>([^<]*)<\/a>/g)].map((m) => decode(m[1]).trim());
  const category = crumbs[1] || "";
  const subcategory = crumbs[2] || "";
  const familyName = decode((html.match(/<h1 class="articleTitle">([\s\S]*?)<\/h1>/) || [, ""])[1].replace(/<[^>]+>/g, "")).trim();
  const familyCode = decode((html.match(/<p class="no">([\s\S]*?)<\/p>/) || [, ""])[1].replace(/<[^>]+>/g, "")).trim();
  const tagline = decode((html.match(/<p class="no">[\s\S]*?<\/p>\s*<div class="Txt">([\s\S]*?)<\/div>/) || [, ""])[1].replace(/<[^>]+>/g, " ")).replace(/\s+/g, " ").trim();
  const iName = lines.lastIndexOf(familyCode, iq);
  const levelLabels = lines.slice(iName + 1, iq).filter((l) => /[：:]$/.test(l)).map((l) => l.replace(/[：:]\s*$/, ""));
  const iEnd = lines.findIndex((l, k) => k > iq && /^(People Also Viewed|Related|You may also like|Back)$/i.test(l));
  const body = lines.slice(iq + 1, iEnd > 0 ? iEnd : iq + 400).filter((l) => l !== "-->" && l !== "SHARE");
  const pageImages = [...new Set([...html.matchAll(/https:\/\/www\.tanko\.com\.tw\/upload\/[^"' )]+\.(?:png|jpe?g|webp)/gi)].map((m) => m[0]))];

  const combos = [];
  const l1 = levels[0].length ? levels[0] : [{ id: "0", label: "" }];
  const l2 = levels[1].length ? levels[1] : [{ id: "0", label: "" }];
  if (indexId && (levels[0].length || levels[1].length)) {
    for (const a of l1) for (const b of l2) combos.push({ p1: a.id, p2: b.id, labels: [a.label, b.label] });
    await pool(combos, 4, async (c) => {
      const q = "indexId=" + indexId + "&package1Id=" + c.p1 + "&package2Id=" + c.p2;
      const [note, album] = await Promise.all([get(EN + "products/act/?act=8&" + q), get(EN + "products-item/?" + q)]);
      c.note = textLines(note);
      c.images = [...new Set([...album.matchAll(/https:\/\/www\.tanko\.com\.tw\/upload\/catalog_package_b\/[^"' )]+/g)].map((m) => m[0]))];
    });
  }
  return { slug, url, indexId, title, category, subcategory, familyName, familyCode, tagline, levelLabels, levels, body, pageImages, combos };
}

async function pool(items, n, fn) {
  let i = 0;
  await Promise.all(Array.from({ length: n }, async () => { while (i < items.length) await fn(items[i++]); }));
}

(async () => {
  const slugs = JSON.parse(fs.readFileSync(slugsFile, "utf8")).map((s) => s.slug || s);
  const out = [];
  let done = 0;
  await pool(slugs, 3, async (slug) => {
    out.push(await scrapeFamily(slug));
    if (++done % 10 === 0) console.log(done + "/" + slugs.length);
  });
  out.sort((a, b) => a.slug.localeCompare(b.slug));
  fs.writeFileSync(outFile, JSON.stringify(out, null, 1));
  console.log("families", out.length, "combos", out.reduce((n, f) => n + (f.combos ? f.combos.length : 0), 0));
})();
