/* Draws Excalidraw JSON as a hand-drawn SVG, using rough.js when it is loaded.
   Usage in a page:
     <svg class="sketch" data-sketch="sk"></svg>
     <script type="application/json" id="sk" data-sketch-src="diagrams/x.excalidraw">{...}</script>
   Supports what the generator and ordinary Excalidraw editing produce:
   rectangle, ellipse, diamond, line, arrow, text and freedraw. */
(function () {
  var NS = "http://www.w3.org/2000/svg";
  var FONT = {
    1: "'Patrick Hand','Comic Sans MS',cursive",
    5: "'Patrick Hand','Comic Sans MS',cursive",
    2: "'IBM Plex Sans',system-ui,sans-serif",
    3: "'IBM Plex Mono',ui-monospace,monospace"
  };

  function mk(name, attrs) {
    var n = document.createElementNS(NS, name);
    for (var k in attrs) if (attrs[k] !== undefined && attrs[k] !== null) n.setAttribute(k, attrs[k]);
    return n;
  }

  function dash(e) {
    if (e.strokeStyle === "dashed") return [8, 6];
    if (e.strokeStyle === "dotted") return [2, 5];
    return undefined;
  }

  function absPoints(e) {
    return (e.points || []).map(function (p) { return [e.x + p[0], e.y + p[1]]; });
  }

  function bounds(els) {
    var b = { x0: Infinity, y0: Infinity, x1: -Infinity, y1: -Infinity };
    els.forEach(function (e) {
      var pts = (e.points && e.points.length) ? absPoints(e) : [[e.x, e.y], [e.x + e.width, e.y + e.height]];
      pts.forEach(function (p) {
        b.x0 = Math.min(b.x0, p[0]); b.y0 = Math.min(b.y0, p[1]);
        b.x1 = Math.max(b.x1, p[0]); b.y1 = Math.max(b.y1, p[1]);
      });
      if (e.type === "text") b.x1 = Math.max(b.x1, e.x + e.width * 1.15); // widths are estimates
    });
    return b;
  }

  function roundedRect(x, y, w, h, r) {
    return "M" + (x + r) + " " + y + "H" + (x + w - r) + "Q" + (x + w) + " " + y + " " + (x + w) + " " + (y + r) +
      "V" + (y + h - r) + "Q" + (x + w) + " " + (y + h) + " " + (x + w - r) + " " + (y + h) +
      "H" + (x + r) + "Q" + x + " " + (y + h) + " " + x + " " + (y + h - r) +
      "V" + (y + r) + "Q" + x + " " + y + " " + (x + r) + " " + y + "Z";
  }

  function head(parent, a, b, color, width) {
    var ang = Math.atan2(b[1] - a[1], b[0] - a[0]);
    var L = 12, W = 6;
    var p1 = [b[0] - L * Math.cos(ang) + W * Math.sin(ang), b[1] - L * Math.sin(ang) - W * Math.cos(ang)];
    var p2 = [b[0] - L * Math.cos(ang) - W * Math.sin(ang), b[1] - L * Math.sin(ang) + W * Math.cos(ang)];
    parent.appendChild(mk("polyline", {
      points: p1.join(",") + " " + b.join(",") + " " + p2.join(","),
      fill: "none", stroke: color, "stroke-width": width, "stroke-linecap": "round", "stroke-linejoin": "round"
    }));
  }

  function text(parent, e) {
    var size = e.fontSize || 16;
    var lh = size * (e.lineHeight || 1.25);
    var x = e.x, anchor = "start";
    if (e.textAlign === "center") { x = e.x + e.width / 2; anchor = "middle"; }
    else if (e.textAlign === "right") { x = e.x + e.width; anchor = "end"; }
    var t = mk("text", {
      x: x, y: e.y, "font-size": size, fill: e.strokeColor || "#1e1e1e", "text-anchor": anchor,
      "dominant-baseline": "hanging", "font-family": FONT[e.fontFamily] || FONT[5]
    });
    String(e.text).split("\n").forEach(function (line, i) {
      var ts = mk("tspan", { x: x, dy: i === 0 ? 0 : lh });
      ts.textContent = line;
      t.appendChild(ts);
    });
    parent.appendChild(t);
  }

  function render(svg, doc) {
    var els = (doc.elements || []).filter(function (e) { return !e.isDeleted; });
    var b = bounds(els), pad = 24;
    svg.setAttribute("viewBox", [b.x0 - pad, b.y0 - pad, b.x1 - b.x0 + 2 * pad, b.y1 - b.y0 + 2 * pad].join(" "));
    var rc = window.rough ? rough.svg(svg) : null;

    els.forEach(function (e) {
      var g = mk("g", { opacity: (e.opacity === undefined ? 100 : e.opacity) / 100 });
      var color = e.strokeColor || "#1e1e1e";
      var width = (e.strokeWidth || 2) * 0.8;
      var fill = e.backgroundColor && e.backgroundColor !== "transparent" ? e.backgroundColor : undefined;
      var opts = {
        stroke: color, strokeWidth: width, roughness: e.roughness === undefined ? 1.1 : e.roughness * 1.1,
        bowing: 1, seed: e.seed || 1, fill: fill, fillStyle: e.fillStyle || "hachure",
        hachureGap: 5, fillWeight: 1, strokeLineDash: dash(e)
      };
      var plain = { fill: fill || "none", stroke: color, "stroke-width": width, "stroke-dasharray": dash(e) ? dash(e).join(" ") : null };

      if (e.type === "rectangle") {
        var r = e.roundness ? Math.min(32, Math.min(e.width, e.height) * 0.25) : 0;
        if (rc) g.appendChild(r ? rc.path(roundedRect(e.x, e.y, e.width, e.height, r), opts) : rc.rectangle(e.x, e.y, e.width, e.height, opts));
        else g.appendChild(mk("rect", Object.assign({ x: e.x, y: e.y, width: e.width, height: e.height, rx: r }, plain)));
      } else if (e.type === "ellipse") {
        var cx = e.x + e.width / 2, cy = e.y + e.height / 2;
        if (rc) g.appendChild(rc.ellipse(cx, cy, e.width, e.height, opts));
        else g.appendChild(mk("ellipse", Object.assign({ cx: cx, cy: cy, rx: e.width / 2, ry: e.height / 2 }, plain)));
      } else if (e.type === "diamond") {
        var pts = [[e.x + e.width / 2, e.y], [e.x + e.width, e.y + e.height / 2], [e.x + e.width / 2, e.y + e.height], [e.x, e.y + e.height / 2]];
        if (rc) g.appendChild(rc.polygon(pts, opts));
        else g.appendChild(mk("polygon", Object.assign({ points: pts.map(function (p) { return p.join(","); }).join(" ") }, plain)));
      } else if (e.type === "line" || e.type === "arrow" || e.type === "freedraw") {
        var ap = absPoints(e);
        if (ap.length < 2) return;
        var lineOpts = Object.assign({}, opts, { fill: undefined, roughness: e.type === "freedraw" ? 0 : 0.8, bowing: 0.6 });
        if (rc) g.appendChild(e.roundness && ap.length > 2 ? rc.curve(ap, lineOpts) : rc.linearPath(ap, lineOpts));
        else g.appendChild(mk("polyline", Object.assign({ points: ap.map(function (p) { return p.join(","); }).join(" ") }, plain, { fill: "none" })));
        if (e.type === "arrow") {
          if (e.endArrowhead) head(g, ap[ap.length - 2], ap[ap.length - 1], color, width);
          if (e.startArrowhead) head(g, ap[1], ap[0], color, width);
        }
      } else if (e.type === "text") {
        text(g, e);
      }
      svg.appendChild(g);
    });
  }

  function boot() {
    Array.prototype.forEach.call(document.querySelectorAll("svg[data-sketch]"), function (svg) {
      var tag = document.getElementById(svg.getAttribute("data-sketch"));
      if (!tag || !tag.textContent.trim()) return;
      try { render(svg, JSON.parse(tag.textContent)); } catch (err) { console.error("sketch:", err); }
    });
    Array.prototype.forEach.call(document.querySelectorAll("[data-zoom]"), function (btn) {
      btn.addEventListener("click", function () {
        var paper = btn.closest(".paper");
        var on = paper.classList.toggle("zoom");
        document.body.classList.toggle("no-scroll", on);
        btn.textContent = on ? "✕ Close" : "⤢ Full size";
      });
    });
    document.addEventListener("keydown", function (ev) {
      if (ev.key !== "Escape") return;
      var open = document.querySelector(".paper.zoom");
      if (open) open.querySelector("[data-zoom]").click();
    });
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
})();
