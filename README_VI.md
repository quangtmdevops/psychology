# Hệ Thống Quản Lý Tâm Lý Học

## 1. Giới thiệu dự án

Dự án Hệ Thống Quản Lý Tâm Lý Học là một nền tảng toàn diện được phát triển nhằm hỗ trợ các chuyên gia tâm lý, bác sĩ tâm thần và các cơ sở y tế trong việc quản lý thông tin bệnh nhân, đánh giá tâm lý và theo dõi quá trình điều trị. Hệ thống cung cấp các công cụ chuyên nghiệp để:

- Quản lý hồ sơ bệnh nhân một cách bảo mật và hiệu quả
- Thực hiện các bài đánh giá tâm lý chuyên sâu
- Theo dõi tiến trình điều trị và cải thiện sức khỏe tâm thần
- Phân tích dữ liệu để đưa ra các đánh giá và dự đoán
- Hỗ trợ công tác nghiên cứu và báo cáo trong lĩnh vực tâm lý học

## 2. Công nghệ sử dụng

### Ngôn ngữ lập trình
- **Python 3.11**: Ngôn ngữ lập trình chính của dự án
- **SQL**: Cho việc tương tác với cơ sở dữ liệu

### Backend
- **FastAPI**: Framework web, tạo ra các api endpoint
- **SQLAlchemy**: dùng để tương tác với cơ sở dữ liệu
- **Alembic**: dùng để quản lý các phiên bản cơ sở dữ liệu
- **PostgreSQL**: Hệ quản trị cơ sở dữ liệu quan hệ
- **Docker & Docker Compose**: Đóng gói và triển khai ứng dụng

### Mô hình AI: 
- **Ragflow**: sử dụng API của Ragflow để làm chatbot. Sử dụng model gpt-3.5-turbo@OpenAI

## 3. Cách kết nối:
### Backend - Ứng dụng điện thoại
- Ứng dụng Backend được triển khai dưới dạng API, ứng dụng điện thoại sẽ gửi request tới URL: https://api.noro-lab.com/ và endpoint tương ứng. Ứng dụng Backend nhận request sẽ tiến hành xử lý và cập nhật dữ liệu vào database, sau đó trả về response cho ứng dụng điện thoại.
### AI - Ứng dụng điện thoại
- Ứng dụng AI được triển khai dưới dạng API,  ứng dụng điện thoại sẽ gửi request tới URL: https://api.inverevitae.com/ và endpoint tương ứng. Ứng dụng AI nhận nội dung câu hỏi và tiến hành suy nghĩ để trả lời, sau đó trả về response là câu trả lời cho ứng dụng điện thoại.


## 3. Hướng dẫn cài đặt

1. **Yêu cầu hệ thống**
   - Docker và Docker Compose
   - Python 3.11+
   - PostgreSQL 15+

2. **Cài đặt**
   ```bash
   # Clone dự án
   git clone [đường-dẫn-đến-repository]
   cd psychology

   # Tạo file .env từ file mẫu và cấu hình
   cp .env.example .env
   # Chỉnh sửa file .env theo cấu hình của bạn

   # Khởi động ứng dụng bằng Docker
   docker-compose up --build
   ```

