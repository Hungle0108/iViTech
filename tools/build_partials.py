#!/usr/bin/env python3
"""
build_partials.py — Đồng bộ Header và Footer cho toàn bộ các trang HTML trong iViTech.
Thay thế nội dung giữa marker:
  <!-- @include header --> ... <!-- /@include header -->
  <!-- @include footer --> ... <!-- /@include footer -->
Nếu file chưa có marker, script tự động tìm khối header/footer cũ và chèn marker.
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
HEADER_PATH = ROOT / "partials" / "header.html"
FOOTER_PATH = ROOT / "partials" / "footer.html"

HEADER_RE = re.compile(
    r"<!--\s*@include\s+header\s*-->.*?<!--\s*/@include\s+header\s*-->",
    re.DOTALL | re.IGNORECASE
)
FOOTER_RE = re.compile(
    r"<!--\s*@include\s+footer\s*-->.*?<!--\s*/@include\s+footer\s*-->",
    re.DOTALL | re.IGNORECASE
)

# Regex tìm topbar + header cũ (kể cả có hoặc không có topbar)
OLD_HEADER_RE = re.compile(
    r"(?:<!--\s*Topbar\s*-->\s*<div\s+class=\"topbar\">.*?</div>\s*</div>\s*)?(?:<!--\s*Main\s+Navigation\s+Header\s*-->\s*|<!--\s*Header\s*-->\s*)?<header\b[^>]*>.*?</header>",
    re.DOTALL | re.IGNORECASE
)

# Regex tìm footer cũ
OLD_FOOTER_RE = re.compile(
    r"(?:<!--\s*=+\s*(?:11\.\s*)?FOOTER\s*=+\s*-->\s*)?<footer\b[^>]*>.*?</footer>",
    re.DOTALL | re.IGNORECASE
)

# Các trang cần đồng bộ header & footer (8 trang chính + product-template)
TARGET_PAGES = [
    "index.html",
    "product-digitization.html",
    "product-smart-ivier.html",
    "product-ivihrm.html",
    "product-smart-study-2.html",
    "product-interactive-displays.html",
    "product-nexta.html",
    "product-ivivi.html",
    "product-template.html",
]


def load_partial(path: Path) -> str:
    if not path.exists():
        sys.exit(f"[lỗi] Không tìm thấy partial: {path}")
    return path.read_text(encoding="utf-8").strip()


def build_pages(dry_run: bool = False) -> None:
    header_content = load_partial(HEADER_PATH)
    footer_content = load_partial(FOOTER_PATH)

    wrapped_header = f"<!-- @include header -->\n{header_content}\n  <!-- /@include header -->"
    wrapped_footer = f"<!-- @include footer -->\n{footer_content}\n  <!-- /@include footer -->"

    html_files = [ROOT / name for name in TARGET_PAGES if (ROOT / name).exists()]
    updated_count = 0

    for pf in html_files:
        original_text = pf.read_text(encoding="utf-8")
        text = original_text

        # 1. Header
        if HEADER_RE.search(text):
            text = HEADER_RE.sub(wrapped_header, text, count=1)
        elif OLD_HEADER_RE.search(text):
            text = OLD_HEADER_RE.sub(wrapped_header, text, count=1)
        else:
            print(f"[cảnh báo] Không tìm thấy header trong {pf.name}")

        # 2. Footer
        if FOOTER_RE.search(text):
            text = FOOTER_RE.sub(wrapped_footer, text, count=1)
        elif OLD_FOOTER_RE.search(text):
            text = OLD_FOOTER_RE.sub(wrapped_footer, text, count=1)
        else:
            print(f"[cảnh báo] Không tìm thấy footer trong {pf.name}")

        if text != original_text:
            if not dry_run:
                pf.write_text(text, encoding="utf-8")
            updated_count += 1
            print(f"✓ Cập nhật: {pf.name}")
        else:
            print(f"— Không đổi: {pf.name}")

    print(f"\nHoàn tất: Đã xử lý {updated_count}/{len(html_files)} files HTML.")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    build_pages(dry_run=dry_run)
