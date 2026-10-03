/**
 * iViTech Simulator Data
 * File tách riêng dữ liệu kịch bản mô phỏng để bộ phận pháp lý & chuyên môn dễ rà soát.
 * 
 * LƯU Ý PHÁP LÝ:
 * TODO(legal-review): Rà soát thẩm quyền hành chính theo mô hình tổ chức mới (phân cấp, phân quyền giữa các cấp).
 * TODO(legal-review): Rà soát các văn bản quy phạm pháp luật thay thế (ví dụ: NĐ 175/2024/NĐ-CP thay thế NĐ 15/2021/NĐ-CP, Điều 102 vs Điều 103 Luật Xây dựng).
 * 
 * Ngày rà soát gần nhất: 15/01/2026
 */

const SIMULATOR_DATA = {
  disclaimer: "Nội dung mô phỏng mang tính chất minh họa phương thức hỗ trợ của AI, không thay thế ý kiến pháp lý hoặc quyết định hành chính chính thức của cơ quan nhà nước có thẩm quyền.",
  
  "smart-ivier": {
    name: "Smart iVier",
    badge: "AI Hỗ trợ Công vụ",
    scenarios: [
      {
        id: "xaydung",
        label: "Cấp phép xây dựng",
        verifiedAt: "15/01/2026",
        // TODO(legal-review): Kiểm tra thẩm quyền cấp phép nhà ở riêng lẻ và văn bản quy định chi tiết hiện hành
        question: "Quy trình và thẩm quyền cấp Giấy phép xây dựng nhà ở riêng lẻ tại cấp xã/phường?",
        response: [
          "Căn cứ Luật Xây dựng số 50/2014/QH13 (sửa đổi, bổ sung 2020) và các quy định hướng dẫn hiện hành:",
          "1. Thẩm quyền: Cơ quan quản lý trật tự xây dựng theo phân cấp địa phương thẩm định; UBND phường tiếp nhận và xác nhận hiện trạng sử dụng đất.",
          "2. Hồ sơ chuẩn bị: Đơn đề nghị cấp GPXD (theo mẫu); Bản sao giấy tờ chứng minh quyền sử dụng đất; Bản vẽ thiết kế xây dựng.",
          "3. Thời hạn giải quyết: Không quá 15 ngày làm việc kể từ ngày nhận đủ hồ sơ hợp lệ.",
          "➔ Hệ thống đã tạo sẵn dự thảo Phiếu tiếp nhận & Hẹn trả kết quả theo chuẩn thể thức."
        ],
        citations: [
          { text: "Luật Xây dựng 2014 (sửa đổi 2020)", tooltip: "Quy định điều kiện, thẩm quyền cấp phép xây dựng" },
          { text: "Quy định phân cấp địa phương", tooltip: "Xác định cơ quan có thẩm quyền xử lý theo địa bàn" },
          { text: "Thể thức NĐ 30/2020/NĐ-CP", tooltip: "Quy định về kỹ thuật soạn thảo văn bản hành chính" }
        ]
      },
      {
        id: "phapluat",
        label: "Xử phạt hè phố",
        verifiedAt: "15/01/2026",
        // TODO(legal-review): Cập nhật mức xử phạt vi phạm hành chính lĩnh vực giao thông đường bộ theo quy định mới nhất
        question: "Căn cứ pháp lý xử phạt vi phạm hành chính về lấn chiếm vỉa hè, lòng đường đô thị?",
        response: [
          "Căn cứ Nghị định 100/2019/NĐ-CP (sửa đổi, bổ sung bởi Nghị định 123/2021/NĐ-CP) và Luật Xử lý VPHC:",
          "• Hành vi: Sử dụng trái phép lòng đường đô thị, hè phố để kinh doanh dịch vụ ăn uống, bày bán hàng hóa.",
          "• Mức xử phạt: Phạt tiền từ 2.000.000đ đến 3.000.000đ đối với cá nhân; từ 4.000.000đ đến 6.000.000đ đối với tổ chức.",
          "• Biện pháp khắc phục: Buộc thu dọn vật dụng, hoàn trả nguyên trạng phần hè phố, lòng đường.",
          "➔ Cán bộ có thể khởi tạo nhanh Biên bản vi phạm hành chính theo mẫu số 01 (Nghị định 118/2021/NĐ-CP)."
        ],
        citations: [
          { text: "Nghị định 100/2019/NĐ-CP & 123/2021/NĐ-CP", tooltip: "Xử phạt vi phạm hành chính lĩnh vực giao thông" },
          { text: "Luật Xử lý VPHC 2012 (sửa đổi 2020)", tooltip: "Trình tự, thủ tục lập biên bản và ra quyết định xử phạt" }
        ]
      },
      {
        id: "soanthao",
        label: "Dự thảo Thông báo PCCC",
        verifiedAt: "15/01/2026",
        // TODO(legal-review): Rà soát thẩm quyền ban hành kế hoạch kiểm tra liên ngành PCCC tại địa phương
        question: "Dự thảo Thông báo kiểm tra liên ngành an toàn PCCC đối với các cơ sở kinh doanh?",
        response: [
          "Đã khởi tạo tự động dự thảo Thông báo theo đúng kỹ thuật thể thức văn bản hành chính:",
          "• Số ký hiệu: .../TB-UBND; Trích yếu chuẩn: V/v Kiểm tra an toàn phòng cháy, chữa cháy và cứu nạn, cứu hộ năm 2026.",
          "• Thành phần đoàn kiểm tra: Đại diện Công an phường (Trưởng đoàn), Cán bộ Địa chính - Xây dựng, Tổ trưởng dân phố.",
          "• Mốc thời gian & Đối tượng: Liệt kê rõ thời gian từ ngày 15/10 đến 30/10/2026, đính kèm phụ lục danh sách cơ sở.",
          "➔ Cán bộ vui lòng rà soát lại thông tin nhân sự và địa bàn trước khi trình lãnh đạo ký duyệt."
        ],
        citations: [
          { text: "Nghị định 30/2020/NĐ-CP", tooltip: "Quy chuẩn kỹ thuật soạn thảo, phông chữ, bố cục văn bản hành chính" },
          { text: "Luật Phòng cháy và Chữa cháy", tooltip: "Thẩm quyền và trách nhiệm kiểm tra PCCC tại cơ sở" }
        ]
      }
    ]
  },

  "ivihrm": {
    name: "iViHRM OCR & HR",
    badge: "AI Quản trị Nhân sự",
    scenarios: [
      {
        id: "ocr",
        label: "AI OCR Hồ sơ CCCD",
        verifiedAt: "15/01/2026",
        question: "Bóc tách tự động dữ liệu từ ảnh chụp Căn cước công dân gắn chip để nhập hồ sơ nhân sự?",
        response: [
          "Kết quả trích xuất tự động qua mô hình OCR tiếng Việt chuyên sâu trong 1.1 giây:",
          "• Họ và tên: NGUYỄN VĂN AN • Số CCCD: 001095012345 • Giới tính: Nam",
          "• Ngày sinh: 15/08/1995 • Quốc tịch: Việt Nam • Quê quán: Hoàn Kiếm, Hà Nội",
          "• Nơi thường trú: Số 18 Tràng Tiền, Phường Tràng Tiền, Quận Hoàn Kiếm, Hà Nội",
          "➔ Dữ liệu đã tự động điền vào Form Hồ sơ nhân sự mới trên iViHRM, sẵn sàng tạo Hợp đồng thử việc."
        ],
        citations: [
          { text: "Độ chính xác OCR: 99.8%", tooltip: "Mô hình nhận diện ký tự quang học tiếng Việt tối ưu cho giấy tờ tùy thân" },
          { text: "Mã hóa AES-256", tooltip: "Dữ liệu cá nhân được lưu trữ mã hóa chuẩn an toàn thông tin" }
        ]
      },
      {
        id: "chamcong",
        label: "Phân ca & Chấm công",
        verifiedAt: "15/01/2026",
        question: "Tự động tổng hợp dữ liệu chấm công từ nhiều chi nhánh và phát hiện chênh lệch ca kíp?",
        response: [
          "Báo cáo tổng hợp chấm công thời gian thực toàn hệ thống:",
          "• Tỷ lệ đúng giờ: 98.2% trên tổng số 320 nhân sự đang hoạt động.",
          "• Ghi nhận 4 trường hợp đổi ca kíp trực tuyến đã được Trưởng bộ phận phê duyệt qua app di động.",
          "• Tự động đồng bộ giờ làm thêm (OT) sang bảng dự toán lương tháng, không cần nhập liệu thủ công."
        ],
        citations: [
          { text: "Đồng bộ đa điểm", tooltip: "Kết nối máy chấm công khuôn mặt, GPS, WiFi tại tất cả chi nhánh" }
        ]
      },
      {
        id: "tinhluong",
        label: "Tính lương tự động",
        verifiedAt: "15/01/2026",
        question: "Tính toán bảng lương tháng kèm trích nộp BHXH và thuế TNCN theo quy định hiện hành?",
        response: [
          "Bảng tính lương tự động liên kết 100% dữ liệu chấm công và KPI:",
          "• Áp dụng đúng tỷ lệ đóng BHXH, BHYT, BHTN theo quy định mới nhất.",
          "• Tự động tính giảm trừ gia cảnh người phụ thuộc và biểu thuế lũy tiến từng phần thuế TNCN.",
          "• Xuất phiếu lương điện tử (Payslip) gửi bảo mật tới từng nhân viên qua email/Zalo chỉ bằng 1 click."
        ],
        citations: [
          { text: "Luật Thuế TNCN & BHXH", tooltip: "Công thức tính toán cập nhật theo biểu mẫu hiện hành" }
        ]
      }
    ]
  },

  "ivivi": {
    name: "iViVi 20/80",
    badge: "Giáo dục Công nghệ & AI",
    scenarios: [
      {
        id: "robotics",
        label: "Robotics tự hành",
        verifiedAt: "15/01/2026",
        question: "Dự án học sinh: Lắp ráp và lập trình xe robot tự hành dò line tránh vật cản?",
        response: [
          "Phương pháp 20/80 ứng dụng trong dự án xe robot thông minh:",
          "• 20% Lý thuyết: Nguyên lý cảm biến hồng ngoại dò đường và cảm biến siêu âm đo khoảng cách.",
          "• 80% Thực hành: Học sinh tự tay lắp ráp khung xe, đấu nối vi điều khiển và lập trình thuật toán rẽ.",
          "➔ Kết quả: Sau 4 buổi học, 100% học sinh tự vận hành robot hoàn thành đường đua sa bàn thực tế."
        ],
        citations: [
          { text: "Phương pháp 20/80", tooltip: "20% lý thuyết nền tảng – 80% thực hành sáng tạo" },
          { text: "Bộ kit STEM chuẩn quốc tế", tooltip: "Thiết bị an toàn, linh hoạt, hỗ trợ lập trình kéo thả và mã nguồn C++" }
        ]
      },
      {
        id: "aimini",
        label: "Dự án AI Mini",
        verifiedAt: "15/01/2026",
        question: "Học sinh ứng dụng AI phân loại rác thải tự động qua camera như thế nào?",
        response: [
          "Dự án thực tế rèn luyện tư duy công nghệ và ý thức bảo vệ môi trường:",
          "• Thu thập dữ liệu: Học sinh chụp 50 ảnh mẫu rác hữu cơ, rác tái chế và rác vô cơ.",
          "• Huấn luyện mô hình: Sử dụng công cụ trực quan để máy học nhận diện đặc điểm phân loại.",
          "• Kết nối phần cứng: Khi camera nhận diện rác nhựa, cánh tay robot gạt rác vào đúng thùng.",
          "➔ Rèn luyện tư duy giải quyết vấn đề thực tiễn bằng công nghệ AI an toàn và có trách nhiệm."
        ],
        citations: [
          { text: "AI For K-12", tooltip: "Khung năng lực trí tuệ nhân tạo dành cho học sinh phổ thông" }
        ]
      },
      {
        id: "congdanso",
        label: "Kỹ năng Công dân số",
        verifiedAt: "15/01/2026",
        question: "Nội dung đào tạo nhận diện tin giả (Fake News) và bảo vệ an toàn thông tin cá nhân?",
        response: [
          "Chuyên đề Công dân số trong thời đại AI tạo sinh (Generative AI):",
          "• Nhận biết dấu hiệu nhận diện hình ảnh/video deepfake và tin giả trên mạng xã hội.",
          "• Quy tắc bảo vệ mật khẩu, thông tin cá nhân, phòng tránh lừa đảo trực tuyến.",
          "• Văn hóa ứng xử nhân văn trên không gian mạng và tôn trọng bản quyền số."
        ],
        citations: [
          { text: "Khung năng lực số UNESCO", tooltip: "Chuẩn năng lực công dân số toàn cầu cho thế hệ trẻ" }
        ]
      }
    ]
  }
};
