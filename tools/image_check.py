"""Compare each SKU's local photo with the photo tanko.com.tw shows for it.

Usage: py -I tools/image_check.py <diff.json> <thumb_dir> <out.json>
Downloads the site's small thumbnails (catalog_package_s) into thumb_dir,
then scores shape (difference hash) and colour (mean RGB) distance.
"""
import json, os, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

diff_file, thumb_dir, out_file = sys.argv[1:4]
os.makedirs(thumb_dir, exist_ok=True)
matched = [m for m in json.load(open(diff_file, encoding="utf-8"))["matched"] if m["siteImage"] and m["localImage"]]


def thumb_url(u):
    return u.replace("/catalog_package_b/", "/catalog_package_s/")


def fetch(m):
    dest = os.path.join(thumb_dir, os.path.basename(m["siteImage"]))
    if not os.path.exists(dest):
        for url in (thumb_url(m["siteImage"]), m["siteImage"]):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                data = urllib.request.urlopen(req, timeout=30).read()
                open(dest, "wb").write(data)
                break
            except Exception:
                continue
    return dest


def load(path):
    im = Image.open(path)
    im.load()
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGBA", im.size, (255, 255, 255, 255))
        im = Image.alpha_composite(bg, im)
    im = im.convert("RGB")
    # crop to content (non-white) so padding differences don't matter
    gray = im.convert("L").point(lambda v: 255 if v < 245 else 0)
    box = gray.getbbox()
    return im.crop(box) if box else im


def dhash(im, n=8):
    g = im.convert("L").resize((n + 1, n), Image.LANCZOS)
    px = list(g.getdata())
    return [px[r * (n + 1) + c] > px[r * (n + 1) + c + 1] for r in range(n) for c in range(n)]


def mean_rgb(im):
    small = im.resize((32, 32))
    px = [p for p in small.getdata() if sum(p) < 720]  # ignore near-white
    if not px:
        return (255, 255, 255)
    return tuple(sum(c[i] for c in px) / len(px) for i in range(3))


with ThreadPoolExecutor(8) as ex:
    paths = list(ex.map(fetch, matched))

results = []
for m, sp in zip(matched, paths):
    lp = os.path.join("assets", "product", m["localImage"])
    try:
        a, b = load(lp), load(sp)
    except Exception as e:
        results.append({**m, "error": str(e)})
        continue
    ham = sum(x != y for x, y in zip(dhash(a), dhash(b)))
    ca, cb = mean_rgb(a), mean_rgb(b)
    col = sum((ca[i] - cb[i]) ** 2 for i in range(3)) ** 0.5
    ar = (a.width / a.height) / (b.width / b.height)
    results.append({**m, "ham": ham, "col": round(col, 1), "aspect": round(ar, 2), "thumb": sp})

json.dump(results, open(out_file, "w", encoding="utf-8"), indent=1)
bad = [r for r in results if r.get("error") or r["ham"] > 20 or r["col"] > 60]
print("checked", len(results), "flagged", len(bad))
