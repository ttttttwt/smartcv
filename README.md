# Smart CV - Ứng Dụng Tạo CV Thông Minh

Smart CV là một ứng dụng web hiện đại giúp người dùng tạo, chỉnh sửa và quản lý CV một cách dễ dàng và chuyên nghiệp. Ứng dụng tích hợp AI (Google Gemini) để hỗ trợ phân tích, gợi ý cải thiện và dịch thuật CV.

## ✨ Tính Năng Chính

### 🎨 Thiết Kế CV

- **Form Editor**: Giao diện form truyền thống, dễ sử dụng
- **Canvas Editor**: Trình thiết kế kéo-thả với Konva.js
- **Nhiều Template**: Thư viện template đa dạng và chuyên nghiệp
- **Preview Real-time**: Xem trước CV ngay lập tức

### 🤖 Tích Hợp AI

- **Phân Tích CV**: Đánh giá chất lượng CV với điểm số chi tiết
- **Gợi Ý Cải Thiện**: Đưa ra lời khuyên để tối ưu hóa CV
- **AI Writing Assistant**: Hỗ trợ viết nội dung CV
- **Dịch Thuật Đa Ngôn Ngữ**: Dịch CV sang nhiều ngôn ngữ khác nhau

### 📁 Quản Lý CV

- **Danh Sách CV**: Quản lý tất cả CV của bạn
- **Tìm Kiếm & Lọc**: Tìm kiếm theo tên, template, ngày tạo
- **Sao Chép CV**: Tạo bản sao để chỉnh sửa

### 📤 Xuất File

- **Xuất PDF**: Chất lượng cao, ready-to-print
- **Xuất PNG**: Hình ảnh với độ phân giải tùy chỉnh
- **Download Tracking**: Theo dõi số lượt tải xuống

## 🛠 Công Nghệ Sử Dụng

### Backend

- **Flask**: Web framework chính
- **SQLAlchemy**: ORM cho database
- **Flask-Login**: Quản lý authentication

### Frontend

- **HTML5/CSS3**: Giao diện responsive
- **JavaScript ES6+**: Logic frontend
- **Konva.js**: Canvas editor cho thiết kế CV
- **TaiwindCSS**: UI framework

### AI & APIs

- **Google Gemini AI**: Phân tích và sinh text
- **ReportLab**: Tạo file PDF
- **Pillow**: Xử lý hình ảnh

### Database

- **SQLite**: Database mặc định (có thể thay đổi)

## 🚀 Cài Đặt và Chạy

### Yêu Cầu Hệ Thống

- Python 3.8+
- pip (Python package manager)
- Git

### 1. Clone Repository

```bash
git clone <repository-url>
cd smart_cv
```

### 2. Tạo Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Cài Đặt Dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu Hình Environment Variables

Tạo file `.env` trong thư mục gốc:

```env
# API Keys
API_KEY=your_google_gemini_api_key_here

# Flask Configuration
SECRET_KEY=your_secret_key_here
DATABASE_URL=sqlite:///smart_cv.db

# Optional: For production
FLASK_ENV=production
```

### 5. Khởi Tạo Database

```bash
# Tạo database và tables
python app.py
```

### 6. Chạy Ứng Dụng

```bash
python app.py
```

Ứng dụng sẽ chạy tại: `http://localhost:5000`

## 📋 Hướng Dẫn Sử Dụng

### Đăng Ký/Đăng Nhập

1. Truy cập `http://localhost:5000`
2. Đăng ký tài khoản mới hoặc đăng nhập
3. Tài khoản admin mặc định: `admin@smartcv.com` / `admin123`

### Tạo CV Mới

1. **Từ Dashboard**: Click "Tạo CV Mới"
2. **Chọn Template**: Duyệt và chọn template phù hợp
3. **Nhập Thông Tin**: Điền form với thông tin cá nhân
4. **Preview**: Xem trước CV trước khi lưu
5. **Lưu & Xuất**: Lưu CV và xuất file PDF/PNG

### Sử Dụng Canvas Editor

1. Chọn "Canvas Editor" khi tạo CV mới
2. Kéo-thả các elements trên canvas
3. Chỉnh sửa text, màu sắc, vị trí
4. Lưu và preview kết quả

### Sử Dụng AI Features

1. **Phân Tích CV**: Click "Phân Tích CV" để nhận đánh giá
2. **AI Hints**: Sử dụng gợi ý AI khi nhập nội dung
3. **Dịch CV**: Chọn ngôn ngữ và dịch tự động

## 📁 Cấu Trúc Dự Án

```
smart_cv/
├── app.py                 # Ứng dụng Flask chính
├── db.py                  # Cấu hình database
├── requirements.txt       # Dependencies
├── .env                   # Environment variables
├── .gitignore            # Git ignore rules
├── README.md             # Documentation
│
├── models/               # Database models
│   ├── __init__.py
│   ├── user.py          # User model
│   ├── cv.py            # CV model
│   └── cv_template.py   # Template model
│
├── views/                # Flask blueprints/routes
│   ├── main.py          # Main routes
│   ├── user.py          # User authentication
│   └── cv.py            # CV management
│
├── utils/                # Utility functions
│   ├── ai_cv.py         # Gemini AI integration
│   ├── cv_utils.py      # CV processing utilities
│   └── pdf_generator.py # PDF generation
│
├── templates/            # Jinja2 templates
│   ├── base.html
│   ├── index.html
│   ├── dashboard.html
│   └── cv/              # CV related templates
│
├── static/               # Static files
│   ├── css/
│   ├── js/
│   └── images/
│
└── migrations/           # Database migrations
```

## 🔧 API Endpoints

### CV Management

- `GET /cv/list` - Danh sách CV
- `POST /cv/create` - Tạo CV mới
- `GET /cv/<id>/edit` - Chỉnh sửa CV
- `POST /cv/<id>/update` - Cập nhật CV
- `DELETE /cv/<id>/delete` - Xóa CV
- `GET /cv/<id>/preview` - Xem trước CV
- `GET /cv/<id>/download` - Tải xuống CV

### AI Features

- `POST /cv/api/<id>/analyze-cv` - Phân tích CV
- `POST /cv/api/ai-hint` - Gợi ý AI
- `POST /cv/api/translate-cv/<id>` - Dịch CV

### Templates

- `GET /cv/templates` - Danh sách templates
- `GET /cv/api/templates` - API templates
- `POST /cv/api/templates/<id>/select` - Chọn template

## 🎨 Customization

### Thêm Template Mới

1. Tạo template trong `models/cv_template.py`
2. Thiết kế layout với Konva.js JSON
3. Seed data vào database

### Tùy Chỉnh AI Prompts

1. Chỉnh sửa prompts trong `utils/ai_cv.py`
2. Customize evaluation criteria
3. Update suggestion logic

### Styling

1. CSS files trong `static/css/`
2. JavaScript trong `static/js/`
3. Bootstrap customization

## 🚀 Deployment

### Production Setup

1. Thay đổi `FLASK_ENV=production` trong `.env`
2. Sử dụng production database (PostgreSQL/MySQL)
3. Configure web server (Nginx + Gunicorn)
4. Setup SSL certificate

### Docker Deployment

```dockerfile
# Tạo Dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 📝 License

Dự án này được phát hành dưới [MIT License](LICENSE).
