#!/usr/bin/env python3
"""
render_illustrations.py — vẽ ảnh minh họa cho mọi ô ảnh còn trống (ô xanh PLACEHOLDER)
trên website iViTech. KHÔNG cần API key, không cần mạng: chỉ dùng Pillow + font icon
Font Awesome Free (đi kèm trong tools/fonts/).

Mỗi ảnh là một minh họa phẳng kiểu SaaS theo màu thương hiệu: khung thiết bị, huy hiệu
icon, đường nối, quy trình từng bước… — mỗi ô có bố cục và icon riêng theo nội dung
(xem tools/illustrations.json). Ảnh không có chữ.

Chạy từ thư mục gốc dự án:
  python tools/render_illustrations.py                 # vẽ mọi ô còn là placeholder, rồi nhập + gắn vào HTML
  python tools/render_illustrations.py --only home-layer-1,ivivi-hero
  python tools/render_illustrations.py --force         # vẽ lại tất cả (kể cả ô đã có ảnh)
  python tools/render_illustrations.py --preview       # chỉ vẽ ra tools/_preview/, không đụng vào site
  python tools/render_illustrations.py --list          # xem ô nào sẽ được vẽ

Ảnh vẽ ra được đánh dấu "placeholder: illustration" trong lock: khi sau này có
GEMINI_API_KEY, `python tools/generate_images.py generate` sẽ tự thay chúng bằng ảnh AI.
Muốn GIỮ minh họa vĩnh viễn: thêm  "keep_illustration": true  vào mục ảnh trong manifest.

Cài: pip install pillow
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:
    sys.exit("[lỗi] Thiếu Pillow: pip install pillow")

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
FONT = TOOLS / "fonts" / "fa-solid-900.ttf"
FA_MAP = json.loads((TOOLS / "fonts" / "fa-solid-map.json").read_text(encoding="utf-8"))
SPECS = json.loads((TOOLS / "illustrations.json").read_text(encoding="utf-8"))

sys.path.insert(0, str(TOOLS))
import generate_images as gi  # noqa: E402  (dùng chung manifest/lock/import/inject)

SS = 2          # vẽ ở 2x rồi thu nhỏ để khử răng cưa
BASE_W = 1600   # chiều rộng ảnh gốc

# ----------------------------------------------------------------------------
# Màu thương hiệu (chỉnh trong illustrations.json → "palette")
# ----------------------------------------------------------------------------
PAL = {
    "navy": "#0B2A6B", "blue": "#1F5FE0", "cyan": "#5BC8F5", "green": "#22C55E",
    "amber": "#F59E0B", "bg1": "#F7FAFF", "bg2": "#E6EEFD", "line": "#C9D7F2",
    "muted1": "#9AAAC8", "muted2": "#C7D2E8", "white": "#FFFFFF",
}
PAL.update(SPECS.get("palette", {}))
ACCENTS = {
    "blue": ("blue", "cyan"), "navy": ("navy", "blue"), "cyan": ("cyan", "blue"),
    "green": ("green", "cyan"), "muted": ("muted1", "muted2"),
}


def rgb(name_or_hex: str, a: int = 255) -> tuple:
    h = PAL.get(name_or_hex, name_or_hex).lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


# ----------------------------------------------------------------------------
# Primitive vẽ
# ----------------------------------------------------------------------------
class Canvas:
    def __init__(self, w: int, h: int):
        self.w, self.h = w * SS, h * SS
        self.img = Image.new("RGBA", (self.w, self.h), rgb("white"))
        self.u = min(self.w, self.h) / 100.0  # 1 đơn vị = 1% cạnh ngắn
        self._fonts = {}

    def layer(self):
        return Image.new("RGBA", (self.w, self.h), (0, 0, 0, 0))

    def put(self, lay, blur: float = 0):
        """Ghép lớp vào ảnh; chỉ xử lý vùng có nội dung để chạy nhanh."""
        bb = lay.getbbox()
        if not bb:
            return
        pad = int(blur * 3) + 2
        x0, y0 = max(0, bb[0] - pad), max(0, bb[1] - pad)
        x1, y1 = min(self.w, bb[2] + pad), min(self.h, bb[3] + pad)
        part = lay.crop((x0, y0, x1, y1))
        if blur:
            part = part.filter(ImageFilter.GaussianBlur(blur))
        self.img.alpha_composite(part, (x0, y0))

    def font(self, size: float):
        s = max(8, int(size))
        if s not in self._fonts:
            self._fonts[s] = ImageFont.truetype(str(FONT), s)
        return self._fonts[s]

    # --- nền
    def gradient_bg(self, c1, c2, angle_deg=0):
        g = Image.linear_gradient("L").resize((self.w, self.h))
        if angle_deg:
            g = g.rotate(angle_deg, expand=False, fillcolor=128).resize((self.w, self.h))
        a = Image.new("RGBA", (self.w, self.h), rgb(c1))
        b = Image.new("RGBA", (self.w, self.h), rgb(c2))
        self.img = Image.composite(b, a, g)

    def dots(self, color, alpha=22, step=3.2, r=0.18):
        lay = self.layer()
        d = ImageDraw.Draw(lay)
        st, rr = step * self.u, r * self.u
        y = st / 2
        while y < self.h:
            x = st / 2
            while x < self.w:
                d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=rgb(color, alpha))
                x += st
            y += st
        self.put(lay)

    def blob(self, cx, cy, r, color, alpha=70):
        lay = self.layer()
        ImageDraw.Draw(lay).ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb(color, alpha))
        self.put(lay, blur=r * 0.45)

    # --- khối
    def shadow(self, box, radius, dy=1.6, blur=3.2, alpha=46):
        lay = self.layer()
        x0, y0, x1, y1 = box
        o = dy * self.u
        ImageDraw.Draw(lay).rounded_rectangle((x0, y0 + o, x1, y1 + o), radius, fill=rgb("navy", alpha))
        self.put(lay, blur=blur * self.u)

    def card(self, box, radius=None, fill="white", outline="line", width=0.18, shadow=True, alpha=255):
        radius = radius if radius is not None else 2.4 * self.u
        if shadow:
            self.shadow(box, radius)
        lay = self.layer()
        ImageDraw.Draw(lay).rounded_rectangle(box, radius, fill=rgb(fill, alpha),
                                              outline=rgb(outline) if outline else None,
                                              width=max(1, int(width * self.u)))
        self.put(lay)

    def grad_circle(self, cx, cy, r, c1, c2, ring=True):
        size = int(r * 2)
        g = Image.linear_gradient("L").resize((size, size)).rotate(45, fillcolor=128)
        a = Image.new("RGBA", (size, size), rgb(c1))
        b = Image.new("RGBA", (size, size), rgb(c2))
        disc = Image.composite(b, a, g)
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, size - 1, size - 1), fill=255)
        lay = self.layer()
        if ring:  # quầng nhạt
            rr = r * 1.32
            ImageDraw.Draw(lay).ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=rgb(c2, 46))
        lay.paste(disc, (int(cx - r), int(cy - r)), mask)
        self.shadow((cx - r * 0.8, cy - r * 0.6, cx + r * 0.8, cy + r), r, dy=1.2, blur=2.4, alpha=40)
        self.put(lay)

    def icon(self, name, cx, cy, size, color="white", alpha=255):
        code = FA_MAP.get(name) or FA_MAP.get("circle")
        ch = chr(int(code, 16))
        f = self.font(size)
        lay = self.layer()
        d = ImageDraw.Draw(lay)
        b = d.textbbox((0, 0), ch, font=f)
        d.text((cx - (b[0] + b[2]) / 2, cy - (b[1] + b[3]) / 2), ch, font=f, fill=rgb(color, alpha))
        self.put(lay)

    def badge(self, name, cx, cy, r, accent="blue"):
        c1, c2 = ACCENTS.get(accent, ACCENTS["blue"])
        self.grad_circle(cx, cy, r, c1, c2)
        self.icon(name, cx, cy, r * 0.95, "white")

    def bars(self, x0, y0, w, rows, rng, color="line", h=None, gap=None):
        lay = self.layer()
        d = ImageDraw.Draw(lay)
        h = h or 1.1 * self.u
        gap = gap or 1.1 * self.u
        y = y0
        for i in range(rows):
            ww = w * (rng.uniform(0.55, 1.0) if i else rng.uniform(0.35, 0.6))
            col = rgb("blue", 70) if i == 0 else rgb(color)
            d.rounded_rectangle((x0, y, x0 + ww, y + h), h / 2, fill=col)
            y += h + gap
        self.put(lay)
        return y

    def mini_chart(self, box, rng, accent="blue"):
        x0, y0, x1, y1 = box
        n = 6
        bw = (x1 - x0) / (n * 1.6)
        lay = self.layer()
        d = ImageDraw.Draw(lay)
        c1, c2 = ACCENTS.get(accent, ACCENTS["blue"])
        for i in range(n):
            hh = (y1 - y0) * rng.uniform(0.3, 1.0)
            x = x0 + i * bw * 1.6
            d.rounded_rectangle((x, y1 - hh, x + bw, y1), bw / 3, fill=rgb(c1 if i % 2 else c2, 200))
        self.put(lay)

    def curve(self, p0, p1, color="blue", width=0.35, dash=1.4, gap=1.0, broken=False, bend=0.18, alpha=200):
        (x0, y0), (x1, y1) = p0, p1
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        nx, ny = -(y1 - y0), (x1 - x0)
        cx, cy = mx + nx * bend, my + ny * bend
        pts = []
        steps = 120
        for i in range(steps + 1):
            t = i / steps
            pts.append(((1 - t) ** 2 * x0 + 2 * (1 - t) * t * cx + t * t * x1,
                        (1 - t) ** 2 * y0 + 2 * (1 - t) * t * cy + t * t * y1))
        lay = self.layer()
        d = ImageDraw.Draw(lay)
        acc, on, wpx = 0.0, True, max(2, int(width * self.u))
        seg = [pts[0]]
        dash_px, gap_px = dash * self.u, gap * self.u
        for idx, (a, b) in enumerate(zip(pts, pts[1:])):
            t = idx / steps
            if broken and 0.42 < t < 0.6:  # đứt quãng ở giữa
                seg = [b]
                continue
            acc += math.dist(a, b)
            seg.append(b)
            if acc >= (dash_px if on else gap_px):
                if on and len(seg) > 1:
                    d.line(seg, fill=rgb(color, alpha), width=wpx, joint="curve")
                seg, acc, on = [b], 0.0, not on
        if on and len(seg) > 1:
            d.line(seg, fill=rgb(color, alpha), width=wpx)
        self.put(lay)

    def chevron(self, cx, cy, r, color="blue"):
        lay = self.layer()
        d = ImageDraw.Draw(lay)
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=rgb("white"), outline=rgb("line"), width=max(1, int(0.18 * self.u)))
        self.put(lay)
        self.icon("arrow-right", cx, cy, r * 1.0, color)

    def sparkle(self, cx, cy, s, color="cyan", alpha=220):
        lay = self.layer()
        k = s * 0.22
        ImageDraw.Draw(lay).polygon([(cx, cy - s), (cx + k, cy - k), (cx + s, cy), (cx + k, cy + k),
                                     (cx, cy + s), (cx - k, cy + k), (cx - s, cy), (cx - k, cy - k)],
                                    fill=rgb(color, alpha))
        self.put(lay)

    def device(self, box, icon_name, rng, accent="blue", muted=False, chart=True, header=True):
        x0, y0, x1, y1 = box
        w, h = x1 - x0, y1 - y0
        self.card(box, radius=2.2 * self.u)
        u = self.u
        if header:
            lay = self.layer()
            d = ImageDraw.Draw(lay)
            d.rounded_rectangle((x0, y0, x1, y0 + 4 * u), 2.2 * u, fill=rgb("muted2" if muted else "navy"))
            d.rectangle((x0, y0 + 2.2 * u, x1, y0 + 4 * u), fill=rgb("muted2" if muted else "navy"))
            for i, c in enumerate(("#FF6B6B", "#FBBF24", "#34D399")):
                rr = 0.7 * u
                cx = x0 + 2.4 * u + i * 2.2 * u
                d.ellipse((cx - rr, y0 + 2 * u - rr, cx + rr, y0 + 2 * u + rr),
                          fill=rgb("white", 160) if muted else rgb(c))
            self.put(lay)
            top = y0 + 4 * u
        else:
            top = y0
        br = min(w, h - (top - y0)) * 0.2
        bx, by = x0 + w * 0.27, top + (y1 - top) * 0.42
        self.badge(icon_name, bx, by, br, "muted" if muted else accent)
        self.bars(x0 + w * 0.5, top + (y1 - top) * 0.2, w * 0.4, 4, rng, h=0.95 * u, gap=1.0 * u)
        if chart:
            self.mini_chart((x0 + w * 0.1, y1 - (y1 - top) * 0.28, x1 - w * 0.1, y1 - (y1 - top) * 0.08),
                            rng, "muted" if muted else accent)


# ----------------------------------------------------------------------------
# Bố cục
# ----------------------------------------------------------------------------
def light_bg(c: Canvas, rng, accent):
    c.gradient_bg("bg1", "bg2")
    c.dots("navy", alpha=16)
    a1, a2 = ACCENTS.get(accent, ACCENTS["blue"])
    c.blob(c.w * rng.uniform(0.1, 0.3), c.h * rng.uniform(0.15, 0.4), c.u * 32, a2, 60)
    c.blob(c.w * rng.uniform(0.7, 0.9), c.h * rng.uniform(0.6, 0.85), c.u * 36, a1, 40)


def layout_hub(c: Canvas, spec, rng, broken=False):
    accent = "muted" if broken else spec.get("accent", "blue")
    light_bg(c, rng, "blue" if broken else accent)
    u, W, H = c.u, c.w, c.h
    mw = min(0.44 * W, 0.7 * H * 1.25)
    mh = mw * 0.72
    cx, cy = W * 0.5, H * 0.52
    main = (cx - mw / 2, cy - mh / 2, cx + mw / 2, cy + mh / 2)
    sats = spec.get("satellites", [])
    n = max(1, len(sats))
    rx = max(mw / 2 + 13 * u, 0.38 * W)
    ry = max(mh / 2 + 10 * u, 0.36 * H)
    rx, ry = min(rx, W / 2 - 10.5 * u), min(ry, H / 2 - 10.5 * u)
    start = rng.uniform(-170, -150)
    pos = []
    for i in range(n):
        ang = math.radians(start + i * (300 / max(1, n - 1) if n > 1 else 0))
        jitter = rng.uniform(-0.04, 0.04) if broken else 0
        x = cx + rx * math.cos(ang) * (1 + jitter)
        y = cy + ry * math.sin(ang) * (1 + jitter) + (rng.uniform(-3, 3) * u if broken else 0)
        # đẩy huy hiệu ra ngoài nếu chạm khung thiết bị
        r_s = 8.2 * u
        for _ in range(60):
            if not (main[0] - r_s - 2.5 * u < x < main[2] + r_s + 2.5 * u and
                    main[1] - r_s - 2.5 * u < y < main[3] + r_s + 2.5 * u):
                break
            dx, dy = x - cx, y - cy
            dl = math.hypot(dx, dy) or 1
            x, y = x + dx / dl * 1.5 * u, y + dy / dl * 1.5 * u
        x = min(max(x, r_s + 2 * u), W - r_s - 2 * u)
        y = min(max(y, r_s + 2 * u), H - r_s - 2 * u)
        pos.append((x, y))
    for p in pos:
        c.curve(p, (cx, cy), color="muted1" if broken else "blue", broken=broken,
                bend=rng.uniform(-0.15, 0.15), alpha=150 if broken else 190)
    c.device(main, spec.get("main", "layer-group"), rng, accent=spec.get("accent", "blue"), muted=broken)
    r = 8.2 * u
    for (x, y), name in zip(pos, sats):
        c.badge(name, x, y, r, "muted" if broken else rng.choice(["blue", "navy", "cyan"]))
    if broken:
        c.badge("link-slash", main[2] - 1 * u, main[1] + 1 * u, 3.6 * u, "muted")
    else:
        c.badge("circle-check", main[2] - 1 * u, main[1] + 1 * u, 3.4 * u, "green")
        for _ in range(4):
            c.sparkle(rng.uniform(0.08, 0.92) * W, rng.uniform(0.08, 0.92) * H, rng.uniform(1.0, 1.8) * u, "cyan")


def layout_flow(c: Canvas, spec, rng):
    accent = spec.get("accent", "blue")
    light_bg(c, rng, accent)
    u, W, H = c.u, c.w, c.h
    steps = spec.get("steps", ["file-lines", "database", "robot"])
    n = len(steps)
    margin = 4.5 * u
    gap = max(4.5 * u, 0.045 * W)
    cw = (W - 2 * margin - gap * (n - 1)) / n
    ch = min(cw * 1.45, H * 0.74)
    y0 = (H - ch) / 2 + 2 * u
    centers = []
    for i, name in enumerate(steps):
        x0 = margin + i * (cw + gap)
        box = (x0, y0, x0 + cw, y0 + ch)
        last = i == n - 1
        c.card(box, radius=2.2 * u, outline="green" if last else "line", width=0.3 if last else 0.18)
        r = min(cw, ch) * 0.27
        c.badge(name, x0 + cw / 2, y0 + ch * 0.36, r, "green" if last else ["navy", "blue", "cyan"][i % 3])
        c.bars(x0 + cw * 0.16, y0 + ch * 0.66, cw * 0.68, 3, rng, h=0.9 * u, gap=0.9 * u)
        centers.append((x0 + cw, y0 + ch * 0.36))
    for i in range(n - 1):
        x = centers[i][0] + gap / 2
        c.chevron(x, centers[i][1], min(gap * 0.32, 2.6 * u))
    for _ in range(3):
        c.sparkle(rng.uniform(0.05, 0.95) * W, rng.choice([rng.uniform(0.06, 0.16), rng.uniform(0.86, 0.95)]) * H,
                  rng.uniform(1.0, 1.6) * u)


def layout_scene(c: Canvas, spec, rng):
    accent = spec.get("accent", "blue")
    light_bg(c, rng, accent)
    u, W, H = c.u, c.w, c.h
    # màn hình lớn
    sw = min(0.6 * W, 0.56 * H * 1.6)
    sh = sw * 0.56
    devs = spec.get("devices", ["tablet-screen-button"] * 3)
    k = len(devs)
    dw = min(sw / k * 0.8, 24 * u)
    dh = dw * 0.78
    block = sh + 7 * u + dh
    sx, sy = W / 2 - sw / 2, max(4 * u, (H - block) / 2 - 1 * u)
    c.card((sx - 1.2 * u, sy - 1.2 * u, sx + sw + 1.2 * u, sy + sh + 1.2 * u), radius=2.6 * u, fill="navy", outline=None)
    c.card((sx, sy, sx + sw, sy + sh), radius=1.8 * u, shadow=False)
    c.badge(spec.get("main", "chalkboard-user"), sx + sw * 0.25, sy + sh * 0.48, sh * 0.2, accent)
    c.bars(sx + sw * 0.47, sy + sh * 0.22, sw * 0.42, 3, rng, h=0.9 * u)
    c.mini_chart((sx + sw * 0.47, sy + sh * 0.6, sx + sw * 0.9, sy + sh * 0.86), rng, accent)
    # hàng thiết bị
    gy = min(sy + sh + 7 * u, H - dh - 4 * u)
    total = k * dw + (k - 1) * dw * 0.22
    x = W / 2 - total / 2
    for name in devs:
        box = (x, gy, x + dw, gy + dh)
        c.card(box, radius=1.6 * u)
        c.badge(name, x + dw / 2, gy + dh * 0.45, dh * 0.24, rng.choice(["blue", "cyan", "navy"]))
        c.curve((x + dw / 2, gy), (W / 2, sy + sh), color="blue", bend=0.0, alpha=120, dash=1.0, gap=0.9)
        x += dw * 1.22
    # người hai bên
    ppl = spec.get("people", ["user", "user"])
    row_x0, row_x1 = W / 2 - total / 2, W / 2 + total / 2
    pr = 8.4 * u
    lx = max(pr + 3 * u, min(row_x0 - pr - 6 * u, sx - pr * 0.2))
    rx_ = min(W - pr - 3 * u, max(row_x1 + pr + 6 * u, sx + sw + pr * 0.2))
    py0 = gy + dh / 2
    side = [(lx, py0), (rx_, py0), (lx, py0 - 2.4 * pr), (rx_, py0 - 2.4 * pr)]
    for (px, py), name in zip(side, ppl):
        c.badge(name, px, py, 8.4 * u, rng.choice(["navy", "blue"]))
        c.curve((px, py), (W / 2 + (-1 if px < W / 2 else 1) * sw / 2, sy + sh * 0.6), color="cyan", alpha=170)
    for _ in range(4):
        c.sparkle(rng.uniform(0.05, 0.95) * W, rng.uniform(0.05, 0.95) * H, rng.uniform(1.0, 1.7) * u)


def layout_backdrop(c: Canvas, spec, rng):
    u, W, H = c.u, c.w, c.h
    c.gradient_bg("navy", "#081C4A")
    c.blob(W * 0.2, H * 0.3, 40 * u, "blue", 90)
    c.blob(W * 0.8, H * 0.7, 46 * u, "cyan", 50)
    nodes = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.3, 1.0)) for _ in range(int(70 * W / H))]
    lay = c.layer()
    d = ImageDraw.Draw(lay)
    for i, (x, y, z) in enumerate(nodes):
        near = sorted(nodes, key=lambda n: (n[0] - x) ** 2 + (n[1] - y) ** 2)[1:4]
        for (x2, y2, _) in near:
            d.line((x, y, x2, y2), fill=rgb("cyan", int(40 * z)), width=max(1, int(0.12 * u)))
    for (x, y, z) in nodes:
        r = (0.25 + 0.5 * z) * u
        d.ellipse((x - r, y - r, x + r, y + r), fill=rgb("cyan", int(120 + 120 * z)))
    c.put(lay)
    glow = c.layer()
    for (x, y, z) in rng.sample(nodes, min(12, len(nodes))):
        r = 2.2 * u
        ImageDraw.Draw(glow).ellipse((x - r, y - r, x + r, y + r), fill=rgb("cyan", 140))
    c.put(glow, blur=1.6 * u)


LAYOUTS = {
    "hub": lambda c, s, r: layout_hub(c, s, r, broken=False),
    "broken": lambda c, s, r: layout_hub(c, s, r, broken=True),
    "flow": layout_flow,
    "scene": layout_scene,
    "backdrop": layout_backdrop,
}


def render(img_entry: dict, spec: dict) -> Image.Image:
    rw, rh = (int(x) for x in img_entry["aspect_ratio"].split(":"))
    w, h = BASE_W, round(BASE_W * rh / rw)
    seed = int(hashlib.md5(img_entry["id"].encode()).hexdigest()[:8], 16) + spec.get("seed", 0)
    rng = random.Random(seed)
    c = Canvas(w, h)
    LAYOUTS.get(spec.get("layout", "hub"), LAYOUTS["hub"])(c, spec, rng)
    return c.img.convert("RGB").resize((w, h), Image.LANCZOS)


# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Vẽ minh họa offline cho các ô ảnh còn trống")
    ap.add_argument("--only", help="danh sách id, phân tách bằng dấu phẩy")
    ap.add_argument("--force", action="store_true", help="vẽ lại cả những ô đã có ảnh thật")
    ap.add_argument("--preview", action="store_true", help="chỉ xuất ra tools/_preview/, không gắn vào site")
    ap.add_argument("--list", action="store_true", help="liệt kê ô sẽ được vẽ")
    args = ap.parse_args()

    m = gi.load_manifest()
    lock = gi.load_lock()
    imgs = gi.select(m, args.only, None)
    todo = []
    for e in imgs:
        st = lock.get(e["id"], {})
        empty = (not st) or st.get("placeholder") in (True, "illustration")
        if args.force or args.only or empty:
            todo.append(e)

    if args.list:
        for e in todo:
            sp = SPECS["images"].get(e["id"], {})
            print(f"{e['id']:30} {e['aspect_ratio']:5} {sp.get('layout', 'hub (mặc định)')}")
        print(f"\n{len(todo)} ô.")
        return
    if not todo:
        print("Không còn ô nào trống. Dùng --force để vẽ lại.")
        return

    out_dir = TOOLS / ("_preview" if args.preview else "_incoming")
    out_dir.mkdir(exist_ok=True)
    for e in todo:
        spec = SPECS["images"].get(e["id"], {"layout": "hub", "main": "layer-group",
                                              "satellites": ["database", "robot", "users", "chalkboard-user"]})
        im = render(e, spec)
        p = out_dir / f"{e['id']}.png"
        im.save(p, "PNG", optimize=True)
        print(f"✓ vẽ {e['id']} ({spec.get('layout', 'hub')})")

    if args.preview:
        print(f"\nĐã xuất {len(todo)} ảnh xem trước vào tools/_preview/ (chưa gắn vào site).")
        return

    # nhập + gắn vào HTML bằng pipeline có sẵn
    class A:  # tham số giả cho các hàm của generate_images.py
        only = None; file = None; page = None; keep_alt = False; force = False
        placeholder = False; extra = ""; dry_run = False; model = None; size = None
    gi.cmd_import_dir(A(), m)
    lock = gi.load_lock()
    for e in todo:  # đánh dấu là minh họa → generate (có API key) sẽ được phép thay sau
        if e["id"] in lock and not e.get("keep_illustration"):
            lock[e["id"]]["placeholder"] = "illustration"
            lock[e["id"]]["model"] = "illustration:offline"
    gi.save_lock(lock)
    gi.cmd_inject(A(), m)
    print("\nXong. Mở trang để xem; chạy  python tools/apply_motion.py install --bump  nếu cần xóa cache.")


if __name__ == "__main__":
    main()
