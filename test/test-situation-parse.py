from docx import Document
import re

def docx_to_situations(filename):
    doc = Document(filename)
    situations = []

    current_level = None

    for table in doc.tables:
        for row in table.rows:
            # Lấy text từ các cell, loại bỏ khoảng trắng thừa
            cells = [cell.text.strip() for cell in row.cells]
            cell_text = row.cells[0].text.strip()
            # Bỏ qua hàng tiêu đề
            if not cells or cells[0] in ['STT', '']:
                continue

            # Phát hiện dòng Level (nằm ngoài bảng hoặc trong cell đầu tiên)
            if cells[0].startswith('LEVEL') or 'LEVEL' in cells[0]:
                # Lấy tên level, bỏ emoji
                if re.search(r'level', cell_text, re.IGNORECASE):
                    match = re.search(r'\d+', cell_text)
                    if match:
                        current_level = int(match.group())   # ← chỉ lấy số, kiểu int
                continue

            # Chỉ xử lý các hàng có STT là số
            if not cells or not cells[0].isdigit():
                continue

            stt = cells[0]

            # Một số file ghi tình huống ở cột 1, phương án ở cột 2, giải thích ở cột 3
            # Nhưng trong file của bạn có cấu trúc: STT | Tình huống | Phương án | Giải thích
            if len(cells) < 4:
                continue

            tinh_huong = cells[1]
            phuong_an_raw = cells[2]
            giai_thich_raw = cells[3]

            # Xử lý phần đáp án đúng (in đậm trong file gốc)
            # Trong python-docx, text in đậm vẫn chỉ là text thường, nhưng thường có dòng:
            # "Đáp án đúng là C. ..." hoặc không có
            dap_an_giai_thich = giai_thich_raw

            # Nếu có dòng riêng "Đáp án đúng là...", ưu tiên lấy nó + giải thích
            if "Đáp án đúng là" in giai_thich_raw:
                dap_an_giai_thich = giai_thich_raw
            # Nếu không, tìm trong phương án hoặc giải thích dòng bắt đầu bằng "Đáp án đúng"
            elif "Đáp án đúng" in phuong_an_raw:
                dap_an_giai_thich = phuong_an_raw.split("Đáp án đúng")[1] + "\n" + giai_thich_raw
            elif giai_thich_raw:
                # Một số tình huống Level 3 không có "Đáp án đúng là" mà giải thích luôn mang tính khẩn cấp
                dap_an_giai_thich = giai_thich_raw

            situations.append({
                "level": current_level or "Unknown",
                "stt": stt,
                "tinh_huong": tinh_huong.strip(),
                "phuong_an": phuong_an_raw.strip(),
                "dap_an_giai_thich": dap_an_giai_thich.strip()
            })

    return situations


# === SỬ DỤNG ===
if __name__ == "__main__":
    file_path= r'E:\quangtm\AS_IT\Projects\AS_product_project\psychology\app\data\situation\situation_ques.docx'
    data = docx_to_situations(file_path)

    # In thử 1 ví dụ mỗi level
    for item in data:
        if item["stt"] in ["1", "30"]:  # In câu 1 và câu cuối mỗi level
            print(f"[{item['level']}] Câu {item['stt']}")
            print("Tình huống:", item["tinh_huong"])
            print("Đáp án + Giải thích:", item["dap_an_giai_thich"])
            print("-" * 80)

    print(f"Tổng cộng: {len(data)} tình huống")