# iViTech Modern Landing Page - Nhật ký nâng cấp UI/UX & Nội dung

Tài liệu ghi lại toàn bộ các thay đổi kỹ thuật, sửa lỗi và danh sách các mục cần rà soát theo kế hoạch cải thiện P0 → P1 → P2.

---

## 1. Tóm tắt các hạng mục đã hoàn thành

### P0: Sửa lỗi nghiêm trọng, uy tín & pháp lý
- [x] **P0-1. Tách biệt dữ liệu mô phỏng pháp lý:**
  - Tạo file riêng `js/simulator-data.js` chứa toàn bộ kịch bản mô phỏng của Smart iVier, iViHRM, iViVi.
  - Thêm trường `verifiedAt: "15/01/2026"` hiển thị rõ ràng ngày cập nhật căn cứ pháp lý.
  - Thêm thông báo miễn trừ trách nhiệm (disclaimer): *"Nội dung mô phỏng mang tính chất minh họa, không thay thế ý kiến pháp lý hoặc quyết định hành chính chính thức."*
  - Đặt các thẻ `TODO(legal-review)` cho các chuyên gia pháp lý rà soát thẩm quyền và văn bản thay thế.
- [x] **P0-2. Sửa icon Lớp 02 bị trống:**
  - Thay thế icon lỗi `fas fa-workflow` bằng `fas fa-diagram-project` (hiển thị đầy đủ trên Font Awesome 6).
- [x] **P0-3. Xóa toàn bộ chuỗi nội bộ lộ ra giao diện:**
  - Đã loại bỏ hoàn toàn các chuỗi `(H02)`, `(H03)` trên thanh chuyển đổi điểm nghẽn và các section.
- [x] **P0-4. Khắc phục link chết & link sai đích:**
  - Đã tạo 3 trang tĩnh chính sách hoàn chỉnh: `chinh-sach-bao-mat.html` (tuân thủ Nghị định 13/2023/NĐ-CP), `dieu-khoan.html`, `quy-dinh-ai.html`.
  - Toàn bộ liên kết sản phẩm ở Footer đã trỏ chính xác đến 7 trang chi tiết `product-*.html`.
  - Các icon mạng xã hội được gắn `aria-label` ("Facebook iViTech", "YouTube iViTech", "Zalo iViTech") và đường dẫn thật.
  - Nút chuyển ngôn ngữ `ENG` chưa có nội dung đã được ẩn đi để đảm bảo trải nghiệm người dùng.
- [x] **P0-5. Form liên hệ tuân thủ bảo vệ dữ liệu cá nhân (Nghị định 13/2023/NĐ-CP):**
  - Bổ sung ô checkbox bắt buộc: *"Tôi đồng ý để iViTech xử lý thông tin liên hệ nhằm mục đích tư vấn, theo Chính sách bảo mật."*
  - Xác thực số điện thoại Việt Nam chuẩn regex `^(0|\+84)\d{9,10}$` kèm thông báo lỗi inline trực quan.
  - Chuyển trường "Email làm việc" thành tùy chọn (không bắt buộc).
  - Có đầy đủ trạng thái gửi: Loading spinner, Success toast, Error fallback.
- [x] **P0-6. Định tính hóa các tuyên bố tuyệt đối chưa có nguồn:**
  - Điều chỉnh các con số tuyệt đối (50%, 100%) thành cam kết định tính có trách nhiệm, gắn nhãn `TODO(content)`.

---

### P1: Tối ưu luồng nội dung & tỷ lệ chuyển đổi
- [x] **P1-1. Sắp xếp lại thứ tự section chuẩn hành trình khách hàng:**
  1. Hero (Giá trị cốt lõi + Bộ chọn vai trò ngay)
  2. Trust strip (Logo đối tác + Số liệu triển khai)
  3. Điểm nghẽn thực tế (4 vấn đề & 5 yếu tố kết nối)
  4. Giải pháp theo vai trò (Đưa section `#roadmap` lên ngay sau điểm nghẽn)
  5. Hệ sinh thái 4 lớp (`#ecosystem`: Gộp kiến trúc và giải pháp chi tiết làm 1)
  6. Case study / Kết quả thực tế
  7. Quy trình triển khai 5 bước (kèm timeline)
  8. Về iViTech & Đội ngũ lãnh đạo (`#about` & `#team`)
  9. Câu hỏi thường gặp (FAQ accordion `<details>`)
  10. Liên hệ & Đặt lịch tư vấn (`#contact`)
  11. Footer
- [x] **P1-2. Hợp nhất "Kiến trúc 4 lớp" và "Hệ thống giải pháp":**
  - Gộp thành một section `#ecosystem` duy nhất: Bên trái là stack 4 lớp trực quan; bên phải là nội dung chi tiết (quy trình 6 bước, thông số, liên kết trang con).
  - Hỗ trợ deep linking: `#ecosystem/layer-1` .. `layer-4`.
- [x] **P1-3. Hero nâng cấp:**
  - Tiêu đề viết dạng Sentence Case tự nhiên: *"Kiến tạo năng lực số từ tri thức và công nghệ"*.
  - Hai nút CTA nằm cùng một hàng (Primary: Đặt lịch tư vấn, Ghost: Xem giải pháp theo đơn vị).
  - Thêm bộ chọn vai trò nhanh (3 chips: Cơ quan nhà nước, Doanh nghiệp, Trường học), click tự động cuộn xuống roadmap và điền sẵn form.
  - Bỏ topbar rườm rà (tiết kiệm 40px trên di động), đưa nguyên tắc AI xuống dưới simulator.
- [x] **P1-4. Tương tác Simulator sinh động:**
  - Mô phỏng độ trễ suy nghĩ (typing indicator 650ms) và hiệu ứng xuất hiện câu trả lời từng dòng (tự tắt khi bật `prefers-reduced-motion`).
  - Thêm các chip căn cứ pháp lý có tooltip giải thích.
  - Bổ sung kịch bản phong phú cho cả 3 tab: Smart iVier (3 kịch bản), iViHRM OCR (3 kịch bản), iViVi 20/80 (3 kịch bản).
  - Hỗ trợ phím mũi tên điều hướng chuẩn Accessibility (ARIA tablist/tab).
- [x] **P1-5. Bổ sung các khối tạo dựng niềm tin:**
  - **Trust strip:** Dải đối tác/khách hàng và các chỉ số giá trị cốt lõi.
  - **Case studies:** 3 kịch bản điển hình (UBND cấp cơ sở, Doanh nghiệp dịch vụ, Trường phổ thông K-12).
  - **Quy trình triển khai 5 bước:** Có mốc thời gian rõ ràng (1-3 ngày, 3-5 ngày, 2-4 tuần, 1 tuần, Dài hạn).
  - **Đội ngũ lãnh đạo (`#team`):** Khung giới thiệu 4 vị trí then chốt.
  - **FAQ:** 5 câu hỏi thường gặp trọng tâm (lưu trữ on-premise, AI không thay thế cán bộ, chi phí, thời gian, đào tạo) tích hợp Schema `FAQPage`.
- [x] **P1-6. Tối giản hóa Form liên hệ:**
  - Bước 1 nhanh: 3 chip chọn vai trò, Họ tên, Số điện thoại (bắt buộc).
  - Khối mở rộng "Thêm thông tin để tư vấn chính xác hơn" dạng accordion gọn gàng.
  - Thêm nút liên hệ nhanh qua **Zalo**.
  - Cam kết thời gian phản hồi: *"Phản hồi trong vòng 1 ngày làm việc"*.
- [x] **P1-7. Điều hướng thông minh:**
  - Thanh Menu header sắp xếp khớp 100% với thứ tự section trang.
  - Bổ sung Scroll-spy tự động highlight menu theo vị trí màn hình.
  - `scroll-margin-top: 84px` giúp tiêu đề không bị che bởi sticky header.

---

### P2: Hoàn thiện giao diện, chi tiết & kỹ thuật
- [x] **P2-1. Typography chuẩn tiếng Việt:**
  - Tất cả heading chuyển sang sentence case, áp dụng `text-wrap: balance` và `text-wrap: pretty`.
  - Tương phản văn bản đạt chuẩn WCAG AA (>= 4.5:1), cỡ chữ thẻ >= 15px.
- [x] **P2-2. Thuật ngữ & Ngôn ngữ nhất quán:**
  - Bỏ phần tiếng Anh trong ngoặc đơn ở tiêu đề các lớp.
  - Định nghĩa rõ phương pháp 20/80 ngay lần đầu xuất hiện: *(20% lý thuyết nền tảng – 80% thực hành sáng tạo)*.
- [x] **P2-3. Quy trình số hóa trực quan:**
  - Bổ sung các mốc chuyển giao dữ liệu rõ ràng giữa 6 bước.
- [x] **P2-4. Thanh liên hệ nổi di động (Mobile Sticky Bar):**
  - Trên mobile có thanh cố định dưới đáy gồm: "Gọi ngay: 0989 318 789" và "Nhắn Zalo".
  - Tự động ẩn khi cuộn tới form liên hệ `#contact` để tránh che khuất nút gửi.
  - Desktop ẩn hoàn toàn nút gọi nổi tránh che nội dung.
- [x] **P2-5. Kiểm thử Responsive:**
  - Đảm bảo hiển thị hoàn hảo ở mọi độ phân giải (360px, 390px, 768px, 1024px, 1440px), không bị tràn ngang (`overflow-x: hidden`).
- [x] **P2-6. SEO & Meta Tags:**
  - Đầy đủ Open Graph (Facebook), Twitter Cards, canonical link, favicon, theme-color.
  - Schema JSON-LD `Organization` và `FAQPage`.
- [x] **P2-7. Tracking chuyển đổi:**
  - Gắn thuộc tính `data-cta` vào mọi nút bấm chính trên website.
  - Tích hợp hàm `trackEvent` sẵn sàng cho Google Analytics / GTM.

---

## 2. Danh sách TODO cần bàn giao cho Chủ sản phẩm & Pháp lý

### A. Danh sách TODO(legal-review) — Dành cho Chuyên viên Pháp chế
*Vị trí file: `js/simulator-data.js`*

1. **`TODO(legal-review)` - Thẩm quyền cấp phép xây dựng nhà ở:**
   - Cần rà soát thẩm quyền cấp phép xây dựng nhà ở riêng lẻ theo phân cấp mới nhất tại địa phương và rà soát Điều 102 so với Điều 103 Luật Xây dựng 2014 (sửa đổi 2020).
   - Kiểm tra Nghị định thay thế (Nghị định 175/2024/NĐ-CP so với Nghị định 15/2021/NĐ-CP).
2. **`TODO(legal-review)` - Xử phạt vi phạm trật tự hè phố:**
   - Cập nhật mức phạt tiền và biện pháp khắc phục hậu quả mới nhất trong lĩnh vực giao thông đường bộ đô thị (Nghị định 100/2019/NĐ-CP, Nghị định 123/2021/NĐ-CP và các văn bản sửa đổi tiếp theo).
3. **`TODO(legal-review)` - Thẩm quyền kiểm tra liên ngành PCCC:**
   - Kiểm tra căn cứ phân công lực lượng và thể thức ban hành thông báo kiểm tra an toàn PCCC cấp cơ sở.

### B. Danh sách TODO(content) — Dành cho Chủ sản phẩm & Marketing
*Vị trí file: `index.html`*

1. **`TODO(content)` - Logo khách hàng & đối tác (Dải Trust Strip):**
   - Bổ sung file ảnh logo SVG/PNG của các đối tác, cơ quan và trường học đã ký thỏa thuận hợp tác chính thức.
2. **`TODO(content)` - Số liệu triển khai thực tế (Dải Trust Strip):**
   - Điền số lượng hồ sơ đã số hóa thực tế, số lượng đơn vị hành chính/trường học đã thí điểm.
3. **`TODO(content)` - Case studies & Trích dẫn thực tế:**
   - Điền tên đơn vị thật, số liệu trước/sau chuyển đổi và trích dẫn phát biểu của người phụ trách (đã được sự đồng ý của đơn vị).
4. **`TODO(content)` - Thông tin & Ảnh chân dung Ban Lãnh đạo (`#team`):**
   - Thay thế các khung placeholder bằng ảnh chân dung chuyên nghiệp, họ tên đầy đủ và tóm tắt quá trình công tác của từng thành viên.
