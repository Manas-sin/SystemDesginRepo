"""Copies each diagrams/*.excalidraw file into the page that shows it.

    python3 tools/embed_sketches.py

A page declares where a sketch goes with an empty JSON script tag:

    <script type="application/json" id="sk" data-sketch-src="diagrams/20-leader-election.excalidraw"></script>

This script fills the tag with the file's contents, so the page works when
opened straight from disk (no fetch needed) and always matches the file.
Edit a sketch on excalidraw.com, save it back to diagrams/, and re-run."""
import glob, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TAG = re.compile(r'(<script type="application/json" id="[^"]+" data-sketch-src="([^"]+)">)(.*?)(</script>)', re.S)


def embed(page):
    html = open(page).read()

    def fill(m):
        path = os.path.join(ROOT, m.group(2))
        with open(path) as f:
            doc = json.load(f)
        body = json.dumps({"elements": doc["elements"]}, ensure_ascii=False, separators=(",", ":"))
        return m.group(1) + body.replace("</", "<\\/") + m.group(4)

    new, n = TAG.subn(fill, html)
    if n:
        open(page, "w").write(new)
    return n


if __name__ == "__main__":
    pages = glob.glob(os.path.join(ROOT, "*.html")) + glob.glob(os.path.join(ROOT, "notes", "*.html"))
    for p in sorted(pages):
        n = embed(p)
        if n:
            print(f"embedded {n} sketch(es) into {os.path.relpath(p, ROOT)}")
