# PetShop

Học phần: **Kiểm thử phần mềm**  
Đề tài: **Kiểm thử website bán đồ thú cưng PetShop**

## Thành viên

| Vai trò | Họ tên |
| --- | --- |
| Leader | Quang Duy Thai |
| Member | Truong Hoai Son |
| Member | Le Nguyen Nam Anh |

---

Website bán đồ thú cưng, xây dựng bằng **Python Flask** và **MySQL**. Ứng dụng hỗ trợ khách hàng duyệt sản phẩm, quản lý giỏ hàng, đặt hàng (COD), lưu địa chỉ giao hàng; phía quản trị có dashboard, quản lý sản phẩm, danh mục, đơn hàng và tài khoản.

## Công nghệ

- Python 3
- Flask, Flask-Login, Flask-SQLAlchemy, Flask-WTF
- MySQL (PyMySQL), kết nối qua Aiven hoặc MySQL local
- Jinja2, Bootstrap, JavaScript
- python-dotenv
- Công cụ kiểm thử (học phần): Pytest, Postman, JMeter

## Tính năng

**Khách hàng**

- Trang chủ, danh sách sản phẩm (chó, mèo, phụ kiện, khuyến mãi) và trang chi tiết
- Đăng ký, đăng nhập, đăng xuất, hồ sơ tài khoản
- Giỏ hàng: xem, thêm, cập nhật số lượng, xóa
- Sổ địa chỉ giao hàng
- Đặt hàng thanh toán khi nhận hàng (COD), lịch sử và chi tiết đơn

**Quản trị** (`role = admin`)

- Dashboard thống kê đơn hàng
- Quản lý sản phẩm (thêm / sửa / xóa, ảnh)
- Quản lý danh mục
- Quản lý tài khoản (thêm / sửa, khóa, xóa)
- Xem và cập nhật trạng thái đơn hàng

## Cài đặt

Yêu cầu: Python 3, MySQL (local hoặc Aiven).

```bash
# 1. Tạo và kích hoạt môi trường ảo
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

# 2. Cài thư viện
pip install -r requirements.txt

# 3. Cấu hình môi trường
copy .env.example .env
```

Chỉnh file `.env`:

```env
SECRET_KEY=your-secret-key-here

DB_HOST=your-mysql-host
DB_PORT=3306
DB_NAME=petshop_db
DB_USER=your-user
DB_PASSWORD=your-password
```

Tạo database `petshop_db` trên MySQL (bảng được ánh xạ qua SQLAlchemy models).

```bash
# 4. Chạy ứng dụng
python run.py
```

Mở [http://127.0.0.1:5000](http://127.0.0.1:5000).

## Đường dẫn chính

| Đường dẫn | Mô tả |
| --- | --- |
| `/` | Trang chủ |
| `/san-pham` | Danh sách sản phẩm |
| `/san-pham/cho`, `/meo`, `/phu-kien`, `/khuyen-mai` | Lọc theo nhóm |
| `/san-pham/<id>` | Chi tiết sản phẩm |
| `/auth/register`, `/auth/login`, `/auth/logout` | Tài khoản |
| `/auth/profile` | Hồ sơ |
| `/gio-hang` | Giỏ hàng |
| `/dia-chi` | Địa chỉ giao hàng |
| `/dat-hang` | Thanh toán |
| `/dat-hang/lich-su` | Lịch sử đơn |
| `/admin` | Trang quản trị (cần tài khoản admin) |
| `/admin/users` | Quản lý tài khoản |

## Cấu trúc dự án

```
KT_Phan_mem/
├── app/
│   ├── __init__.py          # Factory Flask, LoginManager, blueprints
│   ├── models/              # User, Category, Product, Cart, Address, Order
│   ├── routes/              # home, product, auth, cart, address, order, admin
│   ├── templates/           # Jinja2 (base, home, auth, product, cart, order, admin)
│   └── static/
│       ├── css/style.css
│       ├── js/main.js
│       └── images/
├── config.py                # SECRET_KEY, SQLAlchemy URI từ .env
├── run.py                   # Điểm chạy ứng dụng
├── requirements.txt
├── .env.example
└── README.md
```

## Kiểm thử

Đề tài thuộc học phần Kiểm thử phần mềm. Có thể dùng:

- **Pytest** — unit / integration test cho Flask
- **Postman** — kiểm thử API / luồng HTTP
- **JMeter** — kiểm thử hiệu năng

Thư mục `tests/` có thể bổ sung khi viết bộ test tự động.
