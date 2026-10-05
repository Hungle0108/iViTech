# iViTech Motion Kit: hiệu ứng và hình ảnh

> **Dành cho agent (Antigravity):** làm lần lượt Phần A (hiệu ứng), Phần B (ảnh), Phần C (nghiệm thu). Không sửa `motion.js` hoặc `motion.css` của Motion Kit nếu chỉ cần đổi *chỗ* áp hiệu ứng. Hãy sửa bảng `MAP` ở đầu `assets/js/motion.js`, hoặc thêm `data-*` vào HTML.

## Nội dung bộ kit

```
assets/css/motion.css               # toàn bộ hiệu ứng (≈8 KB), nạp sau css/styles.css
assets/js/motion.js                 # điều khiển cuộn/hover/tab (≈8 KB khi minify), không cần thư viện
tools/apply_motion.py               # gắn / gỡ kit vào tất cả *.html
tools/generate_images.py            # bản mới: thêm lệnh prompts, import-dir, gộp manifest phụ
tools/image_manifest.motion.json    # 4 ảnh mới (nền liên hệ, nền CTA, dải quy trình, minh họa FAQ)
```

Chép đè vào thư mục gốc repo. **Giữ nguyên** `tools/image_manifest.json` đang có, vì file manifest phụ sẽ được gộp tự động.

---

## Phần A: Hiệu ứng

### A1. Cài đặt

```bash
python tools/apply_motion.py install          # chèn link CSS + script vào cả 11 trang
python tools/apply_motion.py status           # ✓ ở mọi trang
```

Mỗi lần sửa `motion.css` hoặc `motion.js`, chạy `python tools/apply_motion.py install --bump` để đổi `?v=`. Nếu không, GitHub Pages và trình duyệt có thể vẫn dùng bản cũ trong cache.

Gỡ toàn bộ: `python tools/apply_motion.py remove`.

### A2. Hiệu ứng có sẵn (áp tự động theo class hiện có của site)

| Vùng | Hiệu ứng |
|---|---|
| Toàn trang | Thanh tiến độ cuộn 3px gradient ở mép trên |
| Hero trang chủ | Eyebrow → H1 → mô tả → nút → chip "Bạn là" hiện lần lượt (fade-up, cách nhau 90ms). Khung mô phỏng trượt từ phải vào và nghiêng nhẹ theo chuột (desktop). Quầng sáng trôi chậm + parallax |
| Hero trang sản phẩm | Chữ hiện lần lượt. Ảnh hero "kéo màn" từ trên xuống, sau đó zoom rất chậm (Ken Burns 22s). Thẻ chỉ số trượt vào sau ảnh, các dòng chỉ số hiện lần lượt |
| Tiêu đề mọi section | Pill → H2 → mô tả hiện lần lượt |
| Lưới thẻ | Hiện so le (stagger). Hover thì thẻ nổi lên 6px kèm bóng đổ, ảnh trong thẻ zoom 6%, icon nghiêng nhẹ, mũi tên "Chi tiết" trượt sang phải |
| Đội ngũ | Thẻ phóng nhẹ (zoom) khi hiện |
| Quy trình 5 bước, stepper 6 bước số hóa | Các bước sáng **lần lượt** khi cuộn tới, như đang "chạy" quy trình |
| Tab 4 lớp / tab vai trò | Nội dung tab mới trượt nhẹ lên khi đổi tab. Ảnh trong tab được kéo màn |
| Nút chính | Vệt sáng quét qua khi hover, nút lún nhẹ khi bấm |
| CTA sản phẩm, khối liên hệ | Đốm sáng nhẹ đi theo con trỏ, nền gradient chuyển chậm |
| Ảnh | Ảnh tải xong mới hiện (mờ dần vào), tránh thấy ảnh hiện dần từng phần |

Đã kiểm tra trực tiếp trên `hungle0108.github.io/iViTech` (ngày 05/10/2026): hero, lưới 4 điểm nghẽn, quy trình 5 bước và chuyển tab "4 lớp" chạy đúng.

### A3. Nguyên tắc an toàn (đã có sẵn, đừng phá)

- Người dùng bật **Giảm chuyển động** trong hệ điều hành thì mọi hiệu ứng tắt và nội dung hiện ngay. Tắt tay bằng `<html data-motion="off">`.
- Nếu `motion.js` không tải được trong 2.5 giây, đoạn script nhỏ trong `<head>` sẽ gỡ class `.motion-ready`, nên **nội dung không bao giờ bị ẩn vĩnh viễn**.
- Hiệu ứng chỉ dùng `transform` và `opacity`, nên không làm xô lệch bố cục (CLS = 0).
- Hiệu ứng hover viết bằng `:where()`, nên CSS gốc của site luôn được ưu tiên hơn.
- Nghiêng và đốm sáng chỉ bật khi có chuột và màn hình ≥ 1024px.

### A4. Tùy chỉnh

**Đổi màu:** sửa 4 biến `--m-brand-*` và `--m-accent` ở đầu `motion.css` cho khớp `:root` trong `css/styles.css`.

**Thêm hoặc bớt chỗ áp hiệu ứng:** sửa bảng `MAP` ở đầu `motion.js`, ví dụ:

```js
{ sel: '.my-new-grid > .item', reveal: 'fade-up', stagger: 100 },
```

`reveal` nhận một trong các giá trị: `fade-up`, `fade-down`, `fade-left`, `fade-right`, `zoom`, `blur`, `wipe` (dành cho `figure.media`).

**Hoặc viết thẳng trong HTML** (thuộc tính viết tay được ưu tiên hơn MAP):

```html
<div data-reveal="fade-left" data-delay="150">…</div>
<div class="grid" data-stagger="90" data-reveal-children="zoom">…các con…</div>
<span data-count="12000" data-suffix="+">12.000+</span>        <!-- đếm số khi cuộn tới -->
<div data-parallax="0.2">…</div>                              <!-- trôi chậm theo cuộn -->
<div data-tilt="4">…</div>                                    <!-- nghiêng theo chuột, tối đa 4° -->
<ol data-sequence=".step" data-interval="200" data-sequence-line>…</ol>  <!-- sáng lần lượt + thanh tiến độ -->
```

> Chỉ dùng `data-count` cho **số liệu thật đã được iViTech xác nhận** (xem IMPROVEMENTS.md, P0-6). Không tạo dải số liệu mới bằng số ước lượng.

**Đừng lạm dụng:** mỗi section chỉ nên có 1 kiểu hiệu ứng chính. Không thêm hiệu ứng cho form, bảng giá hay nội dung pháp lý.

---

## Phần B: Hình ảnh

### B1. Hiện trạng

Ảnh trên site vẫn là **ảnh giả** (khối gradient navy có chữ PLACEHOLDER). Vì vậy hiệu ứng ảnh chưa tạo được cảm giác sinh động. Có 2 cách thay bằng ảnh thật:

**Cách 1: có Gemini API key** (nhanh nhất, tự động hoàn toàn)

```bash
pip install -r tools/requirements-images.txt
$env:GEMINI_API_KEY="..."                    # PowerShell
python tools/generate_images.py all          # tạo ảnh thật cho mọi ảnh placeholder và gắn vào HTML
```

**Cách 2: không có API key, dùng công cụ tạo ảnh có sẵn của Antigravity**

```bash
python tools/generate_images.py prompts      # ghi tools/image_prompts.md: mỗi ảnh một prompt + tỉ lệ + tên file
```

Agent đọc `tools/image_prompts.md`, tạo **từng** ảnh bằng công cụ tạo ảnh của mình với đúng prompt và tỉ lệ, rồi lưu thành `tools/_incoming/<id>.png`. Sau đó chạy:

```bash
python tools/generate_images.py import-dir   # nhập tất cả, tự xuất WebP 640/1024/1600
python tools/generate_images.py inject       # gắn vào HTML
```

File đã nhập được chuyển vào `tools/_incoming/_imported/`. File đặt sai tên (không trùng id nào) sẽ bị bỏ qua và có thông báo.

Ở cả hai cách, **mở và kiểm tra bằng mắt từng ảnh** theo checklist trong IMPROVEMENTS.md: không có chữ hay logo, tay và mặt không méo, bối cảnh giống Việt Nam, màu đúng tông.

### B2. 4 ảnh mới trong `image_manifest.motion.json`

Đặt các vị trí ảnh sau vào HTML, rồi chạy lại bước B1.

**1. Nền mờ khối liên hệ (`index.html#contact`)**: đặt làm con đầu tiên của `section.contact-section-v2`:

```html
<div class="section-bg-wrap" aria-hidden="true">
  <img data-img="home-contact-bg" alt="" data-parallax="0.12">
</div>
```

`.section-bg-wrap` đã có sẵn trong `motion.css`: ảnh phủ kín, mờ 18%, có lớp navy phủ lên trên để chữ trắng vẫn đọc được. Section cần có `position:relative; overflow:hidden`. Nếu chưa có thì thêm, và đặt `.container` ở `position:relative; z-index:1`.

**2. Nền CTA trang sản phẩm (cả 7 trang)**: cùng mẫu trên, đặt trong `section.product-cta-section`, dùng `data-img="product-cta-bg"`. Một ảnh này dùng chung cho cả 7 trang.

**3. Dải minh họa quy trình (`#process`)**: chèn giữa tiêu đề section và `.process-stepper-5`:

```html
<figure class="media media--21x9 process-banner">
  <img data-img="home-process-banner" class="media__img" alt="">
</figure>
```

```css
.media--21x9 { aspect-ratio: 21 / 9; }
.process-banner { max-width: 1120px; margin: 0 auto 40px; }
@media (max-width: 767px) { .process-banner { aspect-ratio: 16 / 9; } }
```

**4. Minh họa cạnh FAQ (`#faq`)**: chuyển `.faq-section .container` thành lưới 2 cột từ 1024px:

```html
<div class="faq-layout">
  <figure class="media media--4x5 faq-side"><img data-img="home-faq-side" class="media__img" alt=""></figure>
  <div class="faq-accordion">…giữ nguyên các câu hỏi…</div>
</div>
```

```css
.media--4x5 { aspect-ratio: 4 / 5; }
.faq-layout { display: grid; gap: 48px; }
@media (min-width: 1024px) { .faq-layout { grid-template-columns: 380px 1fr; align-items: start; } .faq-side { position: sticky; top: 112px; } }
@media (max-width: 1023px) { .faq-side { display: none; } }
```

Tiêu đề section vẫn để phía trên `.faq-layout`, rộng toàn bộ.

### B3. Thêm ảnh về sau

Thêm mục mới vào `tools/image_manifest.motion.json`, hoặc tạo `tools/image_manifest.<tên>.json` riêng. Mỗi mục cần `id`, `page` (chấp nhận dạng mẫu như `product-*.html`), `section`, `aspect_ratio` (`1:1`, `3:2`, `2:3`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9` hoặc `21:9`), `style`, `prompt` và `alt`. Sau đó đặt `<img data-img="...">` vào HTML.

---

## Phần C: Nghiệm thu

- [ ] `python tools/apply_motion.py status` hiện ✓ ở cả 11 trang. Console không lỗi.
- [ ] Mở từng trang ở 1440px và 390px, cuộn từ đầu đến cuối. **Không có nội dung nào bị ẩn mãi**: đợi 4 giây ở mỗi section, mọi thứ phải hiện ra.
- [ ] Bật "Giảm chuyển động" (Windows: Settings → Accessibility → Visual effects → Animation effects: Off). Tải lại trang thì không còn hiệu ứng nào và mọi nội dung hiện ngay.
- [ ] Lighthouse mobile: CLS ≤ 0.05, Performance không giảm quá 3 điểm so với trước khi gắn kit.
- [ ] Đổi tab "4 lớp" và tab "vai trò" liên tục 10 lần: không bị nháy, không có tab nào trống.
- [ ] Menu dropdown, FAQ accordion, form, video facade vẫn hoạt động như cũ.
- [ ] `python tools/generate_images.py list` không còn ảnh nào ở trạng thái `placeholder`.
- [ ] Ảnh AI có nhãn "Ảnh minh họa (AI)" ở những chỗ người xem dễ hiểu nhầm là ảnh thật (case study).
