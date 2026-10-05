#!/usr/bin/env python3
"""
apply_motion.py — gắn / gỡ bộ hiệu ứng iViTech Motion Kit vào mọi trang HTML.

Chạy từ thư mục gốc dự án:
  python tools/apply_motion.py install            # gắn vào tất cả *.html (chạy lại nhiều lần vẫn an toàn)
  python tools/apply_motion.py install --bump     # tăng số phiên bản ?v= để trình duyệt / GitHub Pages tải bản mới
  python tools/apply_motion.py remove             # gỡ sạch
  python tools/apply_motion.py status             # xem trang nào đã gắn

Script chèn 3 thứ, đều nằm giữa marker <!-- motion-kit --> … <!-- /motion-kit -->:
  1. <link rel="stylesheet" href="assets/css/motion.css?v=N">  ngay sau css/styles.css
  2. Một đoạn script nhỏ trong <head> thêm class .motion-ready (tránh nháy nội dung) và tự gỡ
     class đó nếu motion.js không tải được trong 2.5 giây → nội dung không bao giờ bị ẩn vĩnh viễn.
  3. <script src="assets/js/motion.js?v=N" defer></script>  trước </body>
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
CSS = "assets/css/motion.css"
JS = "assets/js/motion.js"
VERSION_FILE = Path(__file__).resolve().parent / ".motion-version"

BLOCK_RE = re.compile(r"[ \t]*<!-- motion-kit(?: [a-z]+)? -->.*?<!-- /motion-kit -->[ \t]*\r?\n?", re.S)
GUARD = (
    "<script>(function(d){try{if(d.getAttribute('data-motion')==='off'||"
    "matchMedia('(prefers-reduced-motion: reduce)').matches)return;d.classList.add('motion-ready');"
    "setTimeout(function(){if(!window.__ivMotion)d.classList.remove('motion-ready')},2500)}catch(e){}})"
    "(document.documentElement)</script>"
)


def version(bump: bool) -> int:
    v = int(VERSION_FILE.read_text().strip()) if VERSION_FILE.exists() else 1
    if bump:
        v += 1
    VERSION_FILE.write_text(str(v))
    return v


def pages() -> list[Path]:
    return sorted(p for p in ROOT.glob("*.html"))


def strip(src: str) -> str:
    return BLOCK_RE.sub("", src)


def install_one(src: str, v: int, nl: str) -> str:
    src = strip(src)
    head_block = (f"<!-- motion-kit head -->{nl}"
                  f'  <link rel="stylesheet" href="{CSS}?v={v}">{nl}'
                  f"  {GUARD}{nl}"
                  f"  <!-- /motion-kit -->{nl}")
    body_block = f'<!-- motion-kit body --><script src="{JS}?v={v}" defer></script><!-- /motion-kit -->{nl}'

    # 1) sau link styles.css; nếu không có thì trước </head>
    m = re.search(r'<link[^>]+href=["\'][^"\']*styles\.css[^"\']*["\'][^>]*>[ \t]*\r?\n?', src, re.I)
    if m:
        src = src[:m.end()] + "  " + head_block + src[m.end():]
    elif re.search(r"</head>", src, re.I):
        src = re.sub(r"</head>", lambda _: "  " + head_block + "</head>", src, count=1, flags=re.I)
    else:
        raise ValueError("không tìm thấy <head>")

    # 2) trước </body>
    if not re.search(r"</body>", src, re.I):
        raise ValueError("không tìm thấy </body>")
    idx = [m.start() for m in re.finditer(r"</body>", src, re.I)][-1]
    src = src[:idx] + body_block + src[idx:]
    return src


def main() -> None:
    ap = argparse.ArgumentParser(description="Gắn / gỡ iViTech Motion Kit")
    ap.add_argument("command", choices=["install", "remove", "status"])
    ap.add_argument("--bump", action="store_true", help="tăng phiên bản ?v= (xóa cache)")
    args = ap.parse_args()

    missing = [p for p in (CSS, JS) if not (ROOT / p).exists()]
    if args.command == "install" and missing:
        sys.exit(f"[lỗi] thiếu file: {', '.join(missing)} — chép thư mục assets/ của Motion Kit vào gốc dự án trước.")

    v = version(args.bump) if args.command == "install" else None
    for p in pages():
        with open(p, encoding="utf-8", newline="") as f:
            src = f.read()
        nl = "\r\n" if "\r\n" in src else "\n"
        if args.command == "status":
            print(f"{'✓' if 'motion-kit head' in src else '·'} {p.name}")
            continue
        try:
            out = install_one(src, v, nl) if args.command == "install" else strip(src)
        except ValueError as e:
            print(f"[bỏ qua] {p.name}: {e}")
            continue
        if out != src:
            with open(p, "w", encoding="utf-8", newline="") as f:
                f.write(out)
            print(f"{'gắn' if args.command == 'install' else 'gỡ'}: {p.name}")
        else:
            print(f"không đổi: {p.name}")
    if v:
        print(f"\nPhiên bản motion: v={v}")


if __name__ == "__main__":
    main()
