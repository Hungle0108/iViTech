#!/usr/bin/env python3
"""
upgrade_approach_cards.py — thêm ảnh minh họa cho 5 thẻ "5 Yếu tố kết nối iViTech"
(index.html), cùng kiểu với 4 thẻ "Điểm nghẽn thực tế": ảnh 4:3 ở đầu thẻ, rồi nhãn
Bước, tiêu đề, mô tả.

Chạy từ thư mục gốc dự án:
  python tools/upgrade_approach_cards.py                  # làm tất cả
  python tools/upgrade_approach_cards.py --dry-run        # chỉ báo sẽ sửa gì
  python tools/upgrade_approach_cards.py --card5 left     # thẻ 05 chỉ dùng khung "Bộ phận một cửa"

Script làm 5 việc (chạy lại nhiều lần vẫn an toàn):
  1. Cắt 5 ảnh gốc trong tools/approach_sources/ về tỉ lệ 4:3.
     Ảnh 05 là ảnh ghép 3 khung → mặc định ghép lại thành 3 dải dọc trong một khung 4:3
     (--card5 collage), hoặc chỉ lấy một khung: left | middle | right.
  2. Ghi tools/image_manifest.approach.json (id home-approach-01..05).
  3. Nhập ảnh qua generate_images.py → WebP 640/1024/1448 trong assets/img/generated/.
  4. Chèn <figure class="media media--4x3"><img data-img=…></figure> vào đầu mỗi .cap-step-card,
     rồi gọi generate_images.py inject để điền src/srcset/width/height/alt.
  5. Thêm khối CSS (giữa 2 marker approach-cards) vào cuối css/styles.css.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from PIL import Image
except ImportError:
    sys.exit("[lỗi] Thiếu Pillow: pip install pillow")

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
SRC_DIR = TOOLS / "approach_sources"
INCOMING = TOOLS / "_incoming"
PAGE = ROOT / "index.html"
CSS = ROOT / "css" / "styles.css"
MANIFEST = TOOLS / "image_manifest.approach.json"

CARDS = [
    ("home-approach-01", "approach-01.jpg", "Dữ liệu & Tri thức",
     "Cán bộ tra cứu hồ sơ đã số hóa trên hệ thống quản lý tài liệu"),
    ("home-approach-02", "approach-02.jpg", "Phần mềm & AI",
     "Cán bộ dùng trợ lý AI để xử lý và phê duyệt công việc"),
    ("home-approach-03", "approach-03.jpg", "Thiết bị & Môi trường",
     "Lớp học số với màn hình tương tác và máy tính bảng"),
    ("home-approach-04", "approach-04.jpg", "Nội dung & Phương pháp",
     "Học sinh tự lắp ráp, lập trình robot và học kỹ năng công dân số"),
    ("home-approach-05", "approach-05.jpg", "Triển khai & Đồng hành",
     "Chuyên viên iViTech đồng hành cùng cơ quan, doanh nghiệp và nhà trường"),
]

CSS_START = "/* approach-cards:start */"
CSS_END = "/* approach-cards:end */"
CSS_BLOCK = f"""{CSS_START}
/* 5 Yếu tố kết nối: thẻ có ảnh, cùng kiểu với 4 điểm nghẽn (do tools/upgrade_approach_cards.py thêm) */
.capabilities-stepper {{ gap: 20px; }}
.cap-step-card {{
  display: flex;
  flex-direction: column;
  padding: 16px 16px 24px;
  border-radius: var(--radius-md);
}}
.cap-step-card > .media {{
  margin: 0 0 16px;
  border-radius: calc(var(--radius-md) - 4px);
  overflow: hidden;
}}
.cap-step-card .media__img {{ transition: transform .9s cubic-bezier(.16, 1, .3, 1); }}
@media (hover: hover) {{
  .cap-step-card:hover .media__img {{ transform: scale(1.06); }}
}}
.cap-step-card .cap-title {{ line-height: 1.35; }}
/* Tablet: 2 cột, thẻ 05 trải hết hàng cuối để không bị lẻ */
@media (max-width: 1024px) and (min-width: 769px) {{
  .capabilities-stepper > .cap-step-card:last-child {{ grid-column: 1 / -1; }}
  .capabilities-stepper > .cap-step-card:last-child > .media {{ aspect-ratio: 21 / 9; }}
}}
{CSS_END}"""


# ----------------------------------------------------------------------------
def to_4x3(im: Image.Image) -> Image.Image:
    w, h = im.size
    if abs(w / h - 4 / 3) < 0.01:
        return im
    if w / h > 4 / 3:
        nw = round(h * 4 / 3)
        x0 = (w - nw) // 2
        return im.crop((x0, 0, x0 + nw, h))
    nh = round(w * 3 / 4)
    y0 = (h - nh) // 2
    return im.crop((0, y0, w, y0 + nh))


def find_panels(im: Image.Image) -> list[tuple[int, int]]:
    """Tìm các khung trong ảnh ghép dựa vào cột gần trắng ngăn cách."""
    g = im.convert("L")
    w, h = g.size
    px = g.load()
    ys = range(0, h, 4)
    white = [x for x in range(w) if sum(px[x, y] for y in ys) / len(ys) > 235]
    gaps, start, prev = [], None, None
    for x in white:
        if start is None or x != prev + 1:
            if start is not None:
                gaps.append((start, prev))
            start = x
        prev = x
    if start is not None:
        gaps.append((start, prev))
    gaps = [gp for gp in gaps if 3 <= gp[1] - gp[0] <= 40 and 0.1 * w < gp[0] < 0.9 * w]
    edges, x = [], 0
    for a, b in gaps:
        edges.append((x, a))
        x = b + 1
    edges.append((x, w))
    return edges if len(edges) >= 2 else [(0, w)]


def triptych(im: Image.Image, mode: str) -> Image.Image:
    panels = find_panels(im)
    W, H = 1448, 1086
    if mode in ("left", "middle", "right") and len(panels) >= 3:
        a, b = panels[{"left": 0, "middle": 1, "right": 2}[mode]]
        p = im.crop((a, 0, b, im.height))
        nh = round(p.width * 3 / 4)
        y0 = int(p.height * 0.13)  # bỏ phần logo phía trên, giữ biển hiệu + gương mặt
        y0 = min(y0, p.height - nh)
        return p.crop((0, y0, p.width, y0 + nh)).resize((W, H), Image.LANCZOS)
    if len(panels) < 2:
        return to_4x3(im)
    gap = 10
    n = len(panels)
    sw = (W - gap * (n - 1)) // n
    out = Image.new("RGB", (W, H), "white")
    for i, (a, b) in enumerate(panels):
        p = im.crop((a, 0, b, im.height))
        s = H / p.height
        p = p.resize((round(p.width * s), H), Image.LANCZOS)
        x0 = max(0, (p.width - sw) // 2)
        out.paste(p.crop((x0, 0, x0 + sw, H)), (i * (sw + gap), 0))
    return out


def run(cmd: list[str], dry: bool) -> None:
    print("  $ " + " ".join(cmd))
    if not dry:
        subprocess.run([sys.executable, *cmd], cwd=ROOT, check=True)


# ----------------------------------------------------------------------------
def step_images(args) -> None:
    print("1) Chuẩn bị ảnh 4:3")
    INCOMING.mkdir(exist_ok=True)
    for i, (iid, fname, _, _) in enumerate(CARDS):
        src = SRC_DIR / fname
        if not src.exists():
            sys.exit(f"[lỗi] thiếu ảnh gốc {src.relative_to(ROOT)}")
        im = Image.open(src).convert("RGB")
        im = triptych(im, args.card5) if i == 4 else to_4x3(im)
        print(f"   {iid}: {src.name} → {im.width}x{im.height}")
        if not args.dry_run:
            im.save(INCOMING / f"{iid}.png", "PNG", optimize=True)


def step_manifest(args) -> None:
    print("2) Ghi " + MANIFEST.relative_to(ROOT).as_posix())
    data = {
        "_readme": "Ảnh cho 5 thẻ '5 Yếu tố kết nối iViTech' — do iViTech cung cấp, nhập bằng tools/upgrade_approach_cards.py. Không tạo lại bằng AI.",
        "images": [
            {"id": iid, "page": "index.html",
             "section": f"#challenges — tab '5 Yếu tố kết nối', thẻ Bước 0{n + 1} '{title}'",
             "aspect_ratio": "4:3", "style": "photo",
             "prompt": "(ảnh do iViTech cung cấp — không tạo lại)",
             "alt": alt, "keep_illustration": True,
             "sizes": "(min-width: 1025px) 20vw, (min-width: 769px) 50vw, 100vw"}
            for n, (iid, _, title, alt) in enumerate(CARDS)
        ],
    }
    if not args.dry_run:
        MANIFEST.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def step_html(args) -> None:
    print("3) Chèn ảnh vào các thẻ .cap-step-card trong index.html")
    with open(PAGE, encoding="utf-8", newline="") as f:
        html = f.read()
    start = html.find('class="capabilities-stepper"')
    if start < 0:
        sys.exit('[lỗi] không thấy class="capabilities-stepper" trong index.html')
    card_re = re.compile(r'(<div class="cap-step-card"[^>]*>)(\s*)')
    pos, out, changed = start, [], 0
    out.append(html[:start])
    cursor = start
    for n, (iid, _, _, _) in enumerate(CARDS):
        m = card_re.search(html, pos)
        if not m:
            sys.exit(f"[lỗi] chỉ tìm thấy {n} thẻ .cap-step-card (cần 5)")
        nxt = card_re.search(html, m.end())
        body_end = nxt.start() if nxt else len(html)
        out.append(html[cursor:m.end()])
        if f'data-img="{iid}"' not in html[m.end():body_end]:
            indent = m.group(2) if m.group(2).strip() == "" and m.group(2) else "\n            "
            out.append(f'<figure class="media media--4x3"><img data-img="{iid}" class="media__img" alt=""></figure>{indent}')
            changed += 1
        cursor = m.end()
        pos = m.end()
    out.append(html[cursor:])
    new = "".join(out)
    print(f"   thêm ảnh vào {changed}/5 thẻ" + (" (đã có sẵn)" if not changed else ""))
    if changed and not args.dry_run:
        with open(PAGE, "w", encoding="utf-8", newline="") as f:
            f.write(new)


def step_css(args) -> None:
    print("4) Cập nhật CSS")
    with open(CSS, encoding="utf-8", newline="") as f:
        css = f.read()
    nl = "\r\n" if "\r\n" in css else "\n"
    block = CSS_BLOCK.replace("\n", nl)
    if CSS_START in css and CSS_END in css:
        a, b = css.index(CSS_START), css.index(CSS_END) + len(CSS_END)
        new = css[:a] + block + css[b:]
    else:
        new = css.rstrip() + nl + nl + block + nl
    print("   " + ("không đổi" if new == css else "đã ghi khối approach-cards vào css/styles.css"))
    if new != css and not args.dry_run:
        with open(CSS, "w", encoding="utf-8", newline="") as f:
            f.write(new)


def main() -> None:
    ap = argparse.ArgumentParser(description="Thêm ảnh cho 5 thẻ '5 Yếu tố kết nối iViTech'")
    ap.add_argument("--card5", choices=["collage", "left", "middle", "right"], default="collage",
                    help="cách cắt ảnh ghép 3 khung cho thẻ 05 (mặc định: collage)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    step_images(args)
    step_manifest(args)
    print("   nhập ảnh vào assets/img/generated/")
    run(["tools/generate_images.py", "import-dir"], args.dry_run)
    step_html(args)
    run(["tools/generate_images.py", "inject", "--page", "index.html"], args.dry_run)
    step_css(args)
    if (TOOLS / "apply_motion.py").exists():
        run(["tools/apply_motion.py", "install", "--bump"], args.dry_run)
    print("\nXong. Mở index.html → tab '5 Yếu tố kết nối iViTech' để kiểm tra.")


if __name__ == "__main__":
    main()
