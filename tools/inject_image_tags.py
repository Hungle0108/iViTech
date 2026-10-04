#!/usr/bin/env python3
"""
inject_image_tags.py — Đặt các thẻ <img data-img="..."> vào đúng các vị trí theo manifest P1-1.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent

def update_index_html():
    path = ROOT / "index.html"
    text = path.read_text(encoding="utf-8")

    # 1. Challenges (4 cards)
    challenges_mapping = [
        ("home-challenge-data", r'(<div class="observation-card">\s*)(<span class="obs-num">01</span>)'),
        ("home-challenge-tech", r'(<div class="observation-card">\s*)(<span class="obs-num">02</span>)'),
        ("home-challenge-tools", r'(<div class="observation-card">\s*)(<span class="obs-num">03</span>)'),
        ("home-challenge-devices", r'(<div class="observation-card">\s*)(<span class="obs-num">04</span>)'),
    ]
    for img_id, pat in challenges_mapping:
        if f'data-img="{img_id}"' not in text:
            repl = rf'\1<figure class="media media--4x3"><img data-img="{img_id}" class="media__img" alt=""></figure>\n          \2'
            text = re.sub(pat, repl, text, count=1)

    # 2. Roadmap by Role (3 images)
    # Check if roadmap-panel-split already exists
    if 'data-img="home-role-gov"' not in text:
        roadmap_pattern = re.compile(
            r'(<div class="roadmap-grid">)(.*?)(<div style="background: #f8fafc; border: 1px solid var\(--border-light\); border-radius: 12px; padding: 28px;">)',
            re.DOTALL
        )
        def repl_roadmap(m):
            col_left = m.group(2)
            return (
                '<div class="roadmap-grid roadmap-panel-split">\n'
                f'{col_left}\n'
                '          <div>\n'
                '            <div class="roadmap-role-media-wrap" style="position: relative; margin-bottom: 20px;">\n'
                '              <figure class="media media--4x3 roadmap-role-media" data-role-img="gov">\n'
                '                <img data-img="home-role-gov" class="media__img" alt="">\n'
                '              </figure>\n'
                '              <figure class="media media--4x3 roadmap-role-media" data-role-img="business" style="display: none;">\n'
                '                <img data-img="home-role-business" class="media__img" alt="">\n'
                '              </figure>\n'
                '              <figure class="media media--4x3 roadmap-role-media" data-role-img="school" style="display: none;">\n'
                '                <img data-img="home-role-school" class="media__img" alt="">\n'
                '              </figure>\n'
                '            </div>\n'
                '            <div style="background: #f8fafc; border: 1px solid var(--border-light); border-radius: 12px; padding: 20px;">'
            )
        text = roadmap_pattern.sub(repl_roadmap, text, count=1)

    # 3. Ecosystem (4 layers)
    for i in range(1, 5):
        layer_img = f"home-layer-{i}"
        pane_id = f"ecoPane-layer-{i}"
        if f'data-img="{layer_img}"' not in text:
            pat = re.compile(rf'(<div class="eco-pane[^"]*"\s+id="{pane_id}"[^>]*>\s*)(<span class="eyebrow-pill)', re.IGNORECASE)
            repl = rf'\1<figure class="media media--16x9" style="margin-bottom: 20px;"><img data-img="{layer_img}" class="media__img" alt=""></figure>\n            \2'
            text = pat.sub(repl, text, count=1)

    # 4. Case Studies (3 cards)
    case_mapping = [
        ("home-case-public", r'(<!-- Case 1: Gov -->.*?<div class="case-card">\s*)(<div>)'),
        ("home-case-business", r'(<!-- Case 2: Business -->.*?<div class="case-card">\s*)(<div>)'),
        ("home-case-school", r'(<!-- Case 3: School -->.*?<div class="case-card">\s*)(<div>)'),
    ]
    for img_id, pat in case_mapping:
        if f'data-img="{img_id}"' not in text:
            repl = rf'\1<figure class="media media--3x2"><img data-img="{img_id}" class="media__img" alt=""><span class="media__tag">Ảnh minh họa</span></figure>\n          \2'
            text = re.sub(pat, repl, text, count=1, flags=re.DOTALL)

    # 5. About (1 image)
    if 'data-img="home-about"' not in text:
        about_pat = re.compile(
            r'(<section id="about"[^>]*>.*?<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 60px; align-items: center; margin-bottom: 50px;">\s*)(<div>)',
            re.DOTALL
        )
        def repl_about(m):
            return (
                f'{m.group(1)}<div>\n'
                '          <figure class="media media--4x3" style="box-shadow: var(--shadow-lg); border: 1px solid var(--border-light);">\n'
                '            <img data-img="home-about" class="media__img" alt="">\n'
                '          </figure>\n'
                '        </div>\n'
                '        <div>'
            )
        text = about_pat.sub(repl_about, text, count=1)

    path.write_text(text, encoding="utf-8")
    print("✓ Đã gắn data-img vào index.html")


def update_product_pages():
    slugs = {
        "product-digitization.html": "digitization",
        "product-smart-ivier.html": "smart-ivier",
        "product-ivihrm.html": "ivihrm",
        "product-smart-study-2.html": "smart-study-2",
        "product-interactive-displays.html": "interactive-displays",
        "product-nexta.html": "nexta",
        "product-ivivi.html": "ivivi"
    }

    for filename, slug in slugs.items():
        path = ROOT / filename
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")

        # 1. Hero visual
        hero_img = f"{slug}-hero"
        if f'data-img="{hero_img}"' not in text:
            hero_pat = re.compile(
                r'(<!-- Right: (?:Stat Card|Visual) -->\s*)<div class="product-hero-card">',
                re.IGNORECASE
            )
            repl_hero = (
                r'\1<div class="product-hero__visual">\n'
                f'          <figure class="media media--4x3">\n'
                f'            <img data-img="{hero_img}" class="media__img" alt="">\n'
                f'          </figure>\n'
                r'          <div class="product-hero-card">'
            )
            text = hero_pat.sub(repl_hero, text, count=1)
            # đóng thẻ </div> cho .product-hero__visual
            # Tìm phần kết thúc thẻ hero card: </div>\s*</div>\s*</div>\s*</section>
            text = re.sub(
                r'(</div>\s*</div>\s*</div>\s*</section>)',
                r'</div>\n      \1',
                text,
                count=1
            )

        # 2. Overview visual (đặt trước </section> của audience-section)
        overview_img = f"{slug}-overview"
        if f'data-img="{overview_img}"' not in text:
            # Chèn trước </section> kết thúc audience-section
            overview_pat = re.compile(
                r'(</div>\s*</div>\s*</section>\s*<!-- ===================== FEATURES)',
                re.IGNORECASE
            )
            repl_ov = (
                f'        <!-- Overview Visual Pipeline (P1-1) -->\n'
                f'        <figure class="media media--16x9" style="margin-top: 40px;">\n'
                f'          <img data-img="{overview_img}" class="media__img" alt="">\n'
                f'        </figure>\n'
                r'      \1'
            )
            text = overview_pat.sub(repl_ov, text, count=1)

        path.write_text(text, encoding="utf-8")
        print(f"✓ Đã gắn data-img vào {filename}")


if __name__ == "__main__":
    update_index_html()
    update_product_pages()
