# Lấp các ô ảnh còn trống bằng minh họa (không cần API key)

> **Dành cho agent (Antigravity):** chép thư mục `tools/` này vào gốc repo, ghi đè `tools/generate_images.py`, rồi chạy các lệnh dưới đây. **Không** sửa `tools/image_manifest.json` đang có.

## Chạy

```bash
pip install pillow
python tools/render_illustrations.py --list      # xem những ô nào sẽ được vẽ (ô xanh PLACEHOLDER)
python tools/render_illustrations.py --preview   # vẽ thử ra tools/_preview/ để xem trước, chưa gắn vào site
python tools/render_illustrations.py             # vẽ, xuất WebP 640/1024/1600, gắn vào mọi trang HTML
python tools/apply_motion.py install --bump      # (nếu đã cài Motion Kit) đổi ?v= để xóa cache
```

Vẽ cả 34 ô mất khoảng 1 phút. Script không cần mạng và không cần API key. Sau khi chạy xong, commit và push thư mục `assets/img/generated/` cùng các file HTML.

## Script làm gì

- Với mỗi ô có `data-img` mà lock đang ghi `placeholder`, hoặc chưa có ảnh, script vẽ một **minh họa phẳng theo màu thương hiệu**. Minh họa gồm khung thiết bị, huy hiệu icon Font Awesome, đường nối, quy trình từng bước, và không có chữ.
- Mỗi ô có **bố cục và icon riêng theo nội dung**, khai báo trong `tools/illustrations.json`. Có 5 bố cục:
  - `hub`: thiết bị trung tâm và các icon nối vào. Dùng cho trang sản phẩm, Lớp 02, Lớp 04.
  - `broken`: giống `hub` nhưng màu xám, đường nối đứt. Dùng cho 4 "điểm nghẽn".
  - `flow`: các bước từ trái sang phải, bước cuối màu xanh lá. Dùng cho Lớp 01, quy trình, ảnh tổng quan, ảnh OG.
  - `scene`: màn hình lớn, hàng thiết bị bên dưới và người ở hai bên. Dùng cho vai trò, lớp học, case study, đào tạo.
  - `backdrop`: nền navy với mạng lưới điểm sáng. Dùng cho ảnh nền khối Liên hệ và khối CTA.
- Ảnh vẽ xong đi qua đúng quy trình của `generate_images.py`: nhập vào, xuất WebP, rồi tự điền `src`, `srcset`, `width/height` và `alt` vào HTML.

## Tùy chỉnh

- **Đổi icon hoặc bố cục của một ô:** sửa mục đó trong `tools/illustrations.json`, rồi chạy `python tools/render_illustrations.py --only <id>`. Tên icon tra tại fontawesome.com (bản Free, kiểu Solid).
- **Ra biến thể khác:** thêm `"seed": 7` (một số bất kỳ) vào mục đó.
- **Đổi màu:** sửa `palette` ở đầu `illustrations.json`.
- **Vẽ lại tất cả:** thêm `--force`.

## Về sau, khi có ảnh thật

Minh họa được đánh dấu `minh họa` trong lock (xem bằng `python tools/generate_images.py list`). Khi có `GEMINI_API_KEY`, lệnh `python tools/generate_images.py generate` sẽ **tự thay** các minh họa bằng ảnh AI. Muốn giữ minh họa cho một ô thì thêm `"keep_illustration": true` vào mục ảnh đó trong manifest, trước khi chạy `render_illustrations.py`.

Muốn thay bằng ảnh chụp thật (ảnh dự án, ảnh đội ngũ), dùng: `python tools/generate_images.py import --only <id> --file anh.jpg`, rồi chạy `inject`.

## Lưu ý

- `og:image` lấy tên miền từ `site_url` trong `tools/image_manifest.json`, hiện đang là `https://ivitech.vn`. Nếu bản này chạy ở `beta.ivitech.vn` hoặc GitHub Pages, hãy đổi `site_url` cho đúng rồi chạy lại `inject`.
- Nên thêm vào `.gitignore`: `tools/_incoming/`, `tools/_preview/`, `tools/_image_sources/`.
- Icon dùng Font Awesome Free: font theo giấy phép SIL OFL 1.1, icon theo CC BY 4.0 (xem `tools/fonts/FONTAWESOME-LICENSE.txt`). Site đang dùng Font Awesome nên đã có ghi công sẵn.
