# System design notes

A small static site (served by Vercel from the repo root).

```
index.html        the learning plan
approach.html     how to tackle any question: the 7-step route + the picture to draw
sketches.html     all nine sketches on one page, each with an “Open in Excalidraw” button
notes/            one page per lesson (19–24, 26), each with its own sketch
diagrams/         the sketches as editable .excalidraw files (open at excalidraw.com → menu → Open)
css/notes.css     shared styles for notes, approach and sketches
js/sketch.js      draws an .excalidraw file as a hand-drawn SVG (uses js/vendor/rough.js)
tools/            make_sketches.py builds diagrams/*.excalidraw from Python; embed_sketches.py copies them into the pages
```

Change a sketch:

- quick edit → open the `.excalidraw` file on excalidraw.com, save it back to `diagrams/`, run `python3 tools/embed_sketches.py`
- bigger change → edit the sketch in `tools/make_sketches.py`, run `python3 tools/make_sketches.py` (this also embeds)
