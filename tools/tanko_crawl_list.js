// Crawl tanko.com.tw/en product listings (every category, subcategory and
// page) and write the unique products-detail slugs to the given JSON file.
// Usage: node tools/tanko_crawl_list.js <out.json>
const BASE = "https://www.tanko.com.tw/en/";
const UA = { "User-Agent": "Mozilla/5.0" };
const out = process.argv[2] || "tanko_slugs.json";

async function get(url) {
  const r = await fetch(url, { headers: UA });
  return r.ok ? r.text() : "";
}

(async () => {
  const seenPages = new Set();
  const queue = [BASE + "products/"];
  const slugs = new Map(); // slug -> first listing url seen
  while (queue.length) {
    const url = queue.shift();
    if (seenPages.has(url)) continue;
    seenPages.add(url);
    const html = await get(url);
    for (const m of html.matchAll(/href="https:\/\/www\.tanko\.com\.tw\/en\/products-detail\/([^"\/']+)\/"/g)) {
      if (!slugs.has(m[1])) slugs.set(m[1], url);
    }
    for (const m of html.matchAll(/href="(https:\/\/www\.tanko\.com\.tw\/en\/products\/[A-Za-z0-9_-]+\/(?:[A-Za-z0-9_-]+\/)?)"/g)) {
      if (!/\/(act|compare|all)\//.test(m[1])) queue.push(m[1]);
    }
    const base = url.split("?")[0];
    for (const m of html.matchAll(/href="\?page=(\d+)"/g)) queue.push(base + "?page=" + m[1]);
  }
  const list = [...slugs].map(([slug, from]) => ({ slug, from }));
  require("fs").writeFileSync(out, JSON.stringify(list, null, 1));
  console.log("pages", seenPages.size, "slugs", list.length);
})();
