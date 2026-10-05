#!/usr/bin/env python3
"""
generate_images.py — Tạo ảnh minh họa cho website iViTech bằng Gemini (Nano Banana)
rồi tự gắn ảnh vào HTML.

Cách hoạt động
  1. tools/image_manifest.json liệt kê từng ảnh: id, trang, tỉ lệ, prompt, alt.
  2. Trong HTML, đặt  <img data-img="<id>" class="...">  ở đúng chỗ cần ảnh.
  3. `generate` gọi Gemini, lưu ảnh gốc (PNG) vào tools/_image_sources/,
     xuất WebP nhiều kích thước vào assets/img/generated/.
  4. `inject` điền src, srcset, sizes, width, height, alt, loading cho mọi
     <img data-img> và cập nhật <meta property="og:image">.

Lệnh (chạy từ thư mục gốc dự án):
  python tools/generate_images.py list                 # xem trạng thái từng ảnh
  python tools/generate_images.py check                # đối chiếu manifest <-> HTML
  python tools/generate_images.py generate             # tạo ảnh còn thiếu / prompt đã đổi
  python tools/generate_images.py generate --only digitization-hero --force
  python tools/generate_images.py generate --page product-ivivi.html
  python tools/generate_images.py generate --placeholder   # ảnh giả để dựng layout, không cần API key
  python tools/generate_images.py inject
  python tools/generate_images.py all                  # generate + inject
  python tools/generate_images.py import --only <id> --file path/to/anh.png
                                                       # dùng ảnh tạo bằng công cụ khác / ảnh thật
  python tools/generate_images.py prompts              # xuất tools/image_prompts.md (cho công cụ
                                                       # tạo ảnh có sẵn của Antigravity, không cần API key)
  python tools/generate_images.py import-dir           # nhập mọi ảnh trong tools/_incoming/<id>.png|jpg|webp

Manifest phụ: mọi file tools/image_manifest.<tên>.json (trừ .lock.json) được gộp tự động
vào manifest chính — tiện thêm bộ ảnh mới mà không sửa file gốc.

Tuỳ chọn khác: --model, --size (1K|2K|4K), --extra "thêm chỉ dẫn vào prompt", --dry-run

Cài đặt:  pip install -r tools/requirements-images.txt
API key:  đặt biến môi trường GEMINI_API_KEY (hoặc GOOGLE_API_KEY).
"""
from __future__ import annotations

import argparse
import base64
import fnmatch
import hashlib
import html as htmllib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

try:  # Windows console + tiếng Việt
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = Path(__file__).resolve().parent / "image_manifest.json"
LOCK_PATH = Path(__file__).resolve().parent / "image_manifest.lock.json"


# ----------------------------------------------------------------------------
# Manifest & lock
# ----------------------------------------------------------------------------
def load_manifest() -> dict:
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        m = json.load(f)
    for extra in sorted(MANIFEST_PATH.parent.glob("image_manifest.*.json")):
        if extra.name.endswith(".lock.json"):
            continue
        with open(extra, encoding="utf-8") as f:
            add = json.load(f)
        m["styles"].update(add.get("styles", {}))
        m["images"].extend(add.get("images", []))
    ids = [i["id"] for i in m["images"]]
    dup = {x for x in ids if ids.count(x) > 1}
    if dup:
        sys.exit(f"[lỗi] id bị trùng trong manifest: {', '.join(sorted(dup))}")
    for img in m["images"]:
        if img.get("style") not in m["styles"]:
            sys.exit(f"[lỗi] {img['id']}: style '{img.get('style')}' không có trong 'styles'")
    return m


def load_lock() -> dict:
    if LOCK_PATH.exists():
        with open(LOCK_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_lock(lock: dict) -> None:
    with open(LOCK_PATH, "w", encoding="utf-8") as f:
        json.dump(lock, f, ensure_ascii=False, indent=2)


def build_prompt(m: dict, img: dict, extra: str = "") -> str:
    parts = [img["prompt"].strip(), "Style: " + m["styles"][img["style"]].strip()]
    if img.get("crop"):
        parts.append("Keep important subjects away from the top and bottom edges; the image will be cropped.")
    parts.append("Strictly avoid: " + m["negative"].strip())
    if extra:
        parts.append(extra.strip())
    return "\n\n".join(parts)


def prompt_hash(prompt: str, img: dict) -> str:
    key = json.dumps([prompt, img["aspect_ratio"], img.get("crop"), img.get("formats")], ensure_ascii=False)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]


def select(m: dict, only: str | None, page: str | None) -> list[dict]:
    imgs = m["images"]
    if only:
        wanted = {x.strip() for x in only.split(",") if x.strip()}
        unknown = wanted - {i["id"] for i in imgs}
        if unknown:
            sys.exit(f"[lỗi] không có id: {', '.join(sorted(unknown))}")
        imgs = [i for i in imgs if i["id"] in wanted]
    if page:
        imgs = [i for i in imgs if page_match(page, i["page"])]
    return imgs


def page_match(page: str, pattern: str) -> bool:
    """manifest có thể ghi 'page' dạng mẫu, vd 'product-*.html' cho ảnh dùng chung."""
    return page == pattern or fnmatch.fnmatch(page, pattern)


# ----------------------------------------------------------------------------
# Gemini
# ----------------------------------------------------------------------------
def make_client():
    try:
        from google import genai
    except ImportError:
        sys.exit("[lỗi] Thiếu thư viện: pip install -r tools/requirements-images.txt")
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.exit("[lỗi] Chưa đặt GEMINI_API_KEY. Hoặc chạy với --placeholder để dựng layout trước.")
    return genai.Client(api_key=key)


def _to_bytes(data) -> bytes:
    if isinstance(data, (bytes, bytearray)):
        b = bytes(data)
        # Một số SDK trả base64 dạng bytes
        if b[:4] in (b"iVBO", b"/9j/", b"UklG"):
            return base64.b64decode(b)
        return b
    return base64.b64decode(data)


def _via_interactions(client, model: str, prompt: str, aspect: str, size: str) -> bytes:
    inter = client.interactions.create(
        model=model,
        input=prompt,
        response_format={"type": "image", "mime_type": "image/png",
                         "aspect_ratio": aspect, "image_size": size},
    )
    return _to_bytes(inter.output_image.data)


def _via_generate_content(client, model: str, prompt: str, aspect: str, size: str) -> bytes:
    from google.genai import types
    try:
        image_config = types.ImageConfig(aspect_ratio=aspect, image_size=size)
    except Exception:  # SDK cũ không có image_size
        image_config = types.ImageConfig(aspect_ratio=aspect)
    resp = client.models.generate_content(
        model=model,
        contents=prompt,
        config=types.GenerateContentConfig(response_modalities=["IMAGE"], image_config=image_config),
    )
    for cand in resp.candidates or []:
        for part in (cand.content.parts if cand.content else []) or []:
            if getattr(part, "inline_data", None) and part.inline_data.data:
                return _to_bytes(part.inline_data.data)
    raise RuntimeError("Model không trả về ảnh (có thể prompt bị bộ lọc an toàn chặn).")


def call_model(client, model: str, prompt: str, aspect: str, size: str, retries: int = 3) -> bytes:
    last = None
    for attempt in range(1, retries + 1):
        try:
            first_err = None
            if hasattr(client, "interactions"):
                try:
                    return _via_interactions(client, model, prompt, aspect, size)
                except Exception as e:  # SDK/model chưa hỗ trợ Interactions -> thử generate_content
                    first_err = e
            try:
                return _via_generate_content(client, model, prompt, aspect, size)
            except Exception as e:
                raise RuntimeError(f"{e}" + (f" | interactions: {first_err}" if first_err else ""))
        except Exception as e:  # quota, mạng, 5xx...
            last = e
            wait = 4 * attempt
            print(f"    lần {attempt} lỗi: {e}. Thử lại sau {wait}s…")
            time.sleep(wait)
    raise RuntimeError(f"Tạo ảnh thất bại sau {retries} lần: {last}")


# ----------------------------------------------------------------------------
# Xử lý ảnh
# ----------------------------------------------------------------------------
def _pil():
    try:
        from PIL import Image, ImageDraw, ImageOps
        return Image, ImageDraw, ImageOps
    except ImportError:
        sys.exit("[lỗi] Thiếu Pillow: pip install -r tools/requirements-images.txt")


def ratio_tuple(aspect: str) -> tuple[int, int]:
    a, b = aspect.split(":")
    return int(a), int(b)


def make_placeholder(img: dict, width: int = 1600) -> bytes:
    Image, ImageDraw, _ = _pil()
    import io
    rw, rh = ratio_tuple(img["aspect_ratio"])
    h = round(width * rh / rw)
    im = Image.new("RGB", (width, h))
    top, bottom = (11, 42, 107), (31, 95, 224)
    draw = ImageDraw.Draw(im)
    for y in range(h):
        t = y / max(h - 1, 1)
        draw.line([(0, y), (width, y)], fill=tuple(round(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    label = f"PLACEHOLDER  {img['id']}  {img['aspect_ratio']}"
    draw.text((40, 40), label, fill=(255, 255, 255))
    buf = io.BytesIO()
    im.save(buf, "PNG")
    return buf.getvalue()


def export_variants(m: dict, img: dict, src_png: Path) -> dict:
    """Xuất các biến thể đã tối ưu. Trả về thông tin cho lock."""
    Image, _, ImageOps = _pil()
    out_dir = ROOT / m["output_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    mine = re.compile(rf"^{re.escape(img['id'])}(-\d+)?\.(webp|jpg)$")
    for old in out_dir.iterdir():
        if mine.match(old.name):
            old.unlink()

    im = Image.open(src_png)
    im = ImageOps.exif_transpose(im).convert("RGB")
    if img.get("crop"):
        cw, ch = (int(x) for x in img["crop"].lower().split("x"))
        im = ImageOps.fit(im, (cw, ch), method=Image.LANCZOS, centering=(0.5, 0.5))

    formats = img.get("formats", ["webp"])
    files = []
    if img.get("crop"):  # ảnh kích thước cố định (OG)
        for fmt in formats:
            p = out_dir / f"{img['id']}.{fmt}"
            if fmt == "jpg":
                im.save(p, "JPEG", quality=86, optimize=True, progressive=True)
            else:
                im.save(p, "WEBP", quality=m.get("webp_quality", 82), method=6)
            files.append({"path": rel_root(p), "w": im.width, "h": im.height})
    else:
        widths = sorted({w for w in m["widths"] if w <= im.width} or {im.width})
        for w in widths:
            h = round(im.height * w / im.width)
            v = im.resize((w, h), Image.LANCZOS) if w != im.width else im
            for fmt in formats:
                p = out_dir / f"{img['id']}-{w}.{fmt}"
                if fmt == "jpg":
                    v.save(p, "JPEG", quality=84, optimize=True, progressive=True)
                else:
                    v.save(p, "WEBP", quality=m.get("webp_quality", 82), method=6)
                files.append({"path": rel_root(p), "w": w, "h": h})
    return {"files": files}


def rel_root(p: Path) -> str:
    return p.resolve().relative_to(ROOT).as_posix()


# ----------------------------------------------------------------------------
# Lệnh: generate
# ----------------------------------------------------------------------------
def cmd_generate(args, m: dict) -> None:
    lock = load_lock()
    imgs = select(m, args.only, args.page)
    src_dir = ROOT / m["source_dir"]
    src_dir.mkdir(parents=True, exist_ok=True)
    client = None
    model = args.model or os.environ.get("IMAGE_MODEL") or m["default_model"]
    size = args.size or m.get("image_size", "2K")
    made = skipped = failed = 0

    for img in imgs:
        prompt = build_prompt(m, img, args.extra)
        ph = prompt_hash(build_prompt(m, img), img)  # --extra không làm đổi hash
        entry = lock.get(img["id"], {})
        src_png = src_dir / f"{img['id']}.png"
        up_to_date = (src_png.exists() and entry.get("prompt_hash") == ph
                      and (args.placeholder or not entry.get("placeholder")))
        if up_to_date and not args.force:
            skipped += 1
            continue

        print(f"• {img['id']}  ({img['aspect_ratio']}, {img['style']})")
        if args.dry_run:
            print("  --- prompt ---\n  " + prompt.replace("\n", "\n  "))
            continue
        try:
            if args.placeholder:
                data = make_placeholder(img)
            else:
                client = client or make_client()
                data = call_model(client, model, prompt, img["aspect_ratio"], size)
            src_png.write_bytes(data)
            info = export_variants(m, img, src_png)
            lock[img["id"]] = {
                **info,
                "prompt_hash": ph,
                "model": "placeholder" if args.placeholder else model,
                "placeholder": bool(args.placeholder),
                "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            save_lock(lock)
            made += 1
            print(f"  ✓ {len(info['files'])} file → {m['output_dir']}/")
        except Exception as e:
            failed += 1
            print(f"  ✗ {e}")

    print(f"\nXong: tạo {made}, bỏ qua {skipped} (đã có), lỗi {failed}.")
    if made and not args.placeholder:
        print("Nhắc agent: MỞ TỪNG ẢNH MỚI ĐỂ KIỂM TRA (chữ lạ, logo, tay/mặt méo, sai bối cảnh).")
        print("Ảnh chưa đạt → sửa prompt trong manifest hoặc dùng --only <id> --force --extra \"...\".")
    if failed:
        sys.exit(1)


# ----------------------------------------------------------------------------
# Lệnh: import (ảnh từ công cụ khác hoặc ảnh chụp thật)
# ----------------------------------------------------------------------------
def cmd_import(args, m: dict) -> None:
    if not args.only or "," in args.only or not args.file:
        sys.exit("[lỗi] dùng: import --only <một id> --file <đường dẫn ảnh>")
    img = select(m, args.only, None)[0]
    srcf = Path(args.file)
    if not srcf.exists():
        sys.exit(f"[lỗi] không thấy file {srcf}")
    Image, _, _ = _pil()
    src_dir = ROOT / m["source_dir"]
    src_dir.mkdir(parents=True, exist_ok=True)
    src_png = src_dir / f"{img['id']}.png"
    Image.open(srcf).convert("RGB").save(src_png, "PNG")
    info = export_variants(m, img, src_png)
    lock = load_lock()
    lock[img["id"]] = {**info, "prompt_hash": prompt_hash(build_prompt(m, img), img),
                       "model": f"import:{srcf.name}", "placeholder": False,
                       "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    save_lock(lock)
    print(f"✓ {img['id']}: đã nhập {srcf.name} → {len(info['files'])} file. Chạy 'inject' để gắn vào HTML.")
    print("  Lưu ý: ảnh nên đúng tỉ lệ", img["aspect_ratio"], "(CSS object-fit: cover sẽ cắt phần thừa).")


# ----------------------------------------------------------------------------
# Lệnh: prompts / import-dir (dùng công cụ tạo ảnh có sẵn của Antigravity)
# ----------------------------------------------------------------------------
INCOMING = Path(__file__).resolve().parent / "_incoming"


def cmd_prompts(args, m: dict) -> None:
    lock = load_lock()
    out = Path(__file__).resolve().parent / "image_prompts.md"
    rows = []
    todo = [i for i in select(m, args.only, args.page)
            if args.force or not lock.get(i["id"]) or lock[i["id"]].get("placeholder")
            or lock[i["id"]].get("prompt_hash") != prompt_hash(build_prompt(m, i), i)]
    rows.append("# Danh sách ảnh cần tạo\n")
    rows.append("Với MỖI mục: dùng công cụ tạo ảnh, đúng tỉ lệ ghi kèm, prompt nguyên văn, "
                f"lưu thành `tools/_incoming/<id>.png`. Xong hết thì chạy:\n\n"
                "```\npython tools/generate_images.py import-dir\npython tools/generate_images.py inject\n```\n")
    rows.append(f"Tổng: **{len(todo)} ảnh**.\n")
    for i in todo:
        rows.append(f"\n---\n\n## `{i['id']}` · tỉ lệ {i['aspect_ratio']}"
                    + (f" (sẽ cắt {i['crop']})" if i.get("crop") else "")
                    + f"\n\nVị trí: {i.get('section', i['page'])}  \nLưu: `tools/_incoming/{i['id']}.png`\n\n"
                    + "```text\n" + build_prompt(m, i, args.extra) + f"\n\nAspect ratio: {i['aspect_ratio']}.\n```\n")
    out.write_text("\n".join(rows), encoding="utf-8")
    INCOMING.mkdir(exist_ok=True)
    print(f"Đã ghi {out.relative_to(ROOT).as_posix()} ({len(todo)} ảnh). Thư mục lưu ảnh: tools/_incoming/")


def cmd_import_dir(args, m: dict) -> None:
    INCOMING.mkdir(exist_ok=True)
    ids = {i["id"] for i in m["images"]}
    files = [p for p in INCOMING.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    if not files:
        print("tools/_incoming/ đang trống.")
        return
    for f in sorted(files):
        if f.stem not in ids:
            print(f"[bỏ qua] {f.name}: tên file không trùng id nào trong manifest")
            continue
        args.only, args.file = f.stem, str(f)
        cmd_import(args, m)
        done = INCOMING / "_imported"
        done.mkdir(exist_ok=True)
        f.replace(done / f.name)
    print("\nXong. Chạy tiếp: python tools/generate_images.py inject")


# ----------------------------------------------------------------------------
# Lệnh: inject
# ----------------------------------------------------------------------------
IMG_TAG_RE = re.compile(r"<img\b(?P<attrs>[^>]*?)\s*(?P<close>/?)>", re.I | re.S)
ATTR_RE = re.compile(r"""([^\s=/>"']+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+)))?""", re.S)
MANAGED = ("src", "srcset", "sizes", "width", "height", "loading", "decoding", "fetchpriority")


def parse_attrs(s: str) -> list[list]:
    """-> [[name, raw_value_or_None], ...] giữ nguyên thứ tự & giá trị gốc."""
    out = []
    for mt in ATTR_RE.finditer(s):
        name = mt.group(1)
        val = next((g for g in mt.groups()[1:] if g is not None), None)
        out.append([name, val])
    return out


def rel_from_page(page_file: Path, root_rel: str) -> str:
    return Path(os.path.relpath(ROOT / root_rel, page_file.parent)).as_posix()


def build_img_tag(attrs: list[list], updates: dict, close: str) -> str:
    names = [a[0].lower() for a in attrs]
    for k, v in updates.items():
        esc = htmllib.escape(str(v), quote=True)
        if k in names:
            attrs[names.index(k)][1] = esc
        else:
            attrs.append([k, esc])
            names.append(k)
    # bỏ thuộc tính quản lý không còn dùng (vd fetchpriority khi chuyển sang lazy)
    attrs = [a for a in attrs if not (a[0].lower() in MANAGED and a[0].lower() not in updates)]
    body = " ".join(a[0] if a[1] is None else f'{a[0]}="{a[1]}"' for a in attrs)
    return f"<img {body}{' /' if close else ''}>"


def cmd_inject(args, m: dict) -> None:
    lock = load_lock()
    by_id = {i["id"]: i for i in m["images"]}
    pages = sorted({i["page"] for i in m["images"] if "*" not in i["page"]} | set(html_pages()))
    if args.page:
        pages = [args.page]
    total = 0
    for page in pages:
        pf = ROOT / page
        if not pf.exists():
            print(f"[bỏ qua] không thấy {page}")
            continue
        with open(pf, encoding="utf-8", newline="") as f:
            src = f.read()
        changed = 0
        problems = []

        def repl(mt):
            nonlocal changed
            attrs = parse_attrs(mt.group("attrs"))
            amap = {a[0].lower(): a[1] for a in attrs}
            iid = amap.get("data-img")
            if not iid:
                return mt.group(0)
            if iid not in by_id:
                problems.append(f"data-img=\"{iid}\" không có trong manifest")
                return mt.group(0)
            entry = lock.get(iid)
            if not entry:
                problems.append(f"{iid}: chưa tạo ảnh (chạy generate)")
                return mt.group(0)
            img = by_id[iid]
            files = entry["files"]
            prefer = [f for f in files if f["path"].endswith(".webp")] or files
            mid = min(prefer, key=lambda f: abs(f["w"] - 1024))
            eager = img.get("loading") == "eager"
            updates = {
                "src": rel_from_page(pf, mid["path"]),
                "width": mid["w"],
                "height": mid["h"],
                "loading": "eager" if eager else "lazy",
                "decoding": "async",
            }
            if len(prefer) > 1:
                updates["srcset"] = ", ".join(f"{rel_from_page(pf, f['path'])} {f['w']}w" for f in prefer)
                updates["sizes"] = img.get("sizes", "100vw")
            if eager:
                updates["fetchpriority"] = "high"
            if not (args.keep_alt and amap.get("alt")):
                updates["alt"] = img["alt"]
            new = build_img_tag(attrs, updates, mt.group("close"))
            if new != mt.group(0):
                changed += 1
            return new

        out = IMG_TAG_RE.sub(repl, src)

        # og:image
        og = next((i for i in m["images"] if i.get("type") == "og"), None)
        if og and og["id"] in lock and "<head" in out.lower():
            og_file = lock[og["id"]]["files"][0]
            url = m["site_url"].rstrip("/") + "/" + og_file["path"]
            tags = {
                "og:image": url,
                "og:image:width": str(og_file["w"]),
                "og:image:height": str(og_file["h"]),
                "og:image:alt": og["alt"],
            }
            for prop, val in tags.items():
                pat = re.compile(r'<meta\s+[^>]*property=["\']%s["\'][^>]*>' % re.escape(prop), re.I)
                tag = f'<meta property="{prop}" content="{htmllib.escape(val, quote=True)}">'
                if pat.search(out):
                    # chỉ ghi đè nếu trang chưa có ảnh OG riêng (đang trỏ tới og-image hoặc rỗng)
                    cur = pat.search(out).group(0)
                    if prop == "og:image" and "content=\"\"" not in cur and og["id"] not in cur:
                        break  # trang có OG riêng -> giữ nguyên toàn bộ nhóm og:image
                    out = pat.sub(tag, out, count=1)
                else:
                    nl = "\r\n" if "\r\n" in src else "\n"
                    out = re.sub(r"(</head>)", lambda mm: f"  {tag}{nl}{mm.group(1)}", out, count=1, flags=re.I)
            if out != src and changed == 0:
                changed = 1

        if out != src:
            with open(pf, "w", encoding="utf-8", newline="") as f:
                f.write(out)
        total += changed
        status = f"{changed} thay đổi" if out != src else "không đổi"
        print(f"{page}: {status}")
        for p in problems:
            print(f"   ! {p}")
    print(f"\nĐã cập nhật {total} thẻ.")


def html_pages() -> list[str]:
    return [p.name for p in ROOT.glob("*.html")]


# ----------------------------------------------------------------------------
# Lệnh: list / check
# ----------------------------------------------------------------------------
def ids_in_html() -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for page in html_pages():
        txt = (ROOT / page).read_text(encoding="utf-8", errors="replace")
        for mt in IMG_TAG_RE.finditer(txt):
            amap = {a[0].lower(): a[1] for a in parse_attrs(mt.group("attrs"))}
            if amap.get("data-img"):
                found.setdefault(amap["data-img"], []).append(page)
    return found


def cmd_list(args, m: dict) -> None:
    lock = load_lock()
    in_html = ids_in_html()
    print(f"{'ID':32} {'TRANG':34} {'TỈ LỆ':6} {'ẢNH':12} HTML")
    for img in select(m, args.only, args.page):
        e = lock.get(img["id"])
        ph = e.get("placeholder") if e else None
        state = "—" if not e else ("minh họa" if ph == "illustration" else "placeholder" if ph else "ok")
        if e and e.get("prompt_hash") != prompt_hash(build_prompt(m, img), img):
            state += "*"
        where = "og-meta" if img.get("type") == "og" else (",".join(in_html.get(img["id"], [])) or "CHƯA GẮN")
        print(f"{img['id']:32} {img['page']:34} {img['aspect_ratio']:6} {state:12} {where}")
    print("\n* = prompt đã đổi, lần generate sau sẽ tạo lại.")


def cmd_check(args, m: dict) -> None:
    in_html = ids_in_html()
    ids = {i["id"] for i in m["images"] if i.get("type") != "og"}
    missing = sorted(ids - set(in_html))
    orphan = sorted(set(in_html) - {i["id"] for i in m["images"]})
    wrong_page = [f"{i['id']} (manifest: {i['page']}, HTML: {', '.join(in_html[i['id']])})"
                  for i in m["images"] if i["id"] in in_html and not any(page_match(pg, i["page"]) for pg in in_html[i["id"]])]
    ok = True
    if missing:
        ok = False
        print("Chưa có <img data-img> trong HTML:")
        for x in missing:
            sec = next(i["section"] for i in m["images"] if i["id"] == x)
            print(f"  - {x:30} → {sec}")
    if orphan:
        ok = False
        print("data-img trong HTML nhưng không có trong manifest:", ", ".join(orphan))
    if wrong_page:
        print("Lưu ý, id đặt khác trang với manifest:", "; ".join(wrong_page))
    if ok:
        print("Mọi ảnh trong manifest đã có vị trí trong HTML.")


# ----------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Tạo & gắn ảnh cho website iViTech")
    ap.add_argument("command", choices=["list", "check", "generate", "inject", "all", "import", "prompts", "import-dir"])
    ap.add_argument("--only", help="danh sách id, phân tách bằng dấu phẩy")
    ap.add_argument("--page", help="chỉ xử lý một trang, vd product-ivivi.html")
    ap.add_argument("--force", action="store_true", help="tạo lại dù ảnh đã có")
    ap.add_argument("--placeholder", action="store_true", help="tạo ảnh giả (không gọi API)")
    ap.add_argument("--model", help="model ảnh, mặc định lấy từ manifest / biến IMAGE_MODEL")
    ap.add_argument("--size", choices=["1K", "2K", "4K"], help="độ phân giải ảnh gốc")
    ap.add_argument("--extra", default="", help="chỉ dẫn thêm vào cuối prompt")
    ap.add_argument("--dry-run", action="store_true", help="chỉ in prompt, không gọi API")
    ap.add_argument("--file", help="(import) đường dẫn ảnh cần nhập")
    ap.add_argument("--keep-alt", action="store_true", help="giữ alt đã viết tay trong HTML")
    args = ap.parse_args()
    m = load_manifest()

    if args.command == "list":
        cmd_list(args, m)
    elif args.command == "check":
        cmd_check(args, m)
    elif args.command == "generate":
        cmd_generate(args, m)
    elif args.command == "inject":
        cmd_inject(args, m)
    elif args.command == "import":
        cmd_import(args, m)
    elif args.command == "prompts":
        cmd_prompts(args, m)
    elif args.command == "import-dir":
        cmd_import_dir(args, m)
    elif args.command == "all":
        cmd_generate(args, m)
        if not args.dry_run:
            cmd_inject(args, m)


if __name__ == "__main__":
    main()
