# 🚀 HƯỚNG DẪN DEPLOY LÊN RENDER.COM

## BƯỚC 1: Tạo GitHub Repository

1. Vào https://github.com/new
2. Tạo repo mới tên: `icexai-auth-server`
3. Chọn **Public**
4. Click **Create repository**

## BƯỚC 2: Upload code lên GitHub

Mở Git Bash/Terminal tại thư mục này (`E:\Discordcode\RenderDeploy\`):

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/icexai-auth-server.git
git push -u origin main
```

*(Thay `YOUR_USERNAME` bằng tên GitHub của bạn)*

## BƯỚC 3: Deploy trên Render

1. Vào https://render.com
2. Đăng nhập bằng GitHub
3. Click **New** → **Web Service**
4. Chọn repo `icexai-auth-server`
5. Cấu hình:
   - **Name**: `icexai-auth`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn auth_server:app`
   - **Plan**: **Free**
6. Click **Create Web Service**

## BƯỚC 4: Đợi deploy (2-3 phút)

Render sẽ tự động:
- Cài dependencies
- Chạy server
- Cho bạn link: `https://icexai-auth.onrender.com`

## BƯỚC 5: Test

Vào trình duyệt:
- `https://icexai-auth.onrender.com/` → Xem thông tin server
- `https://icexai-auth.onrender.com/admin` → Xem danh sách key

## BƯỚC 6: Cập nhật Discord Bot

Trong file `bot.py`, thêm code đồng bộ key lên Render:

```python
import requests

RENDER_API = "https://icexai-auth.onrender.com"

def sync_key_to_render(key_data):
    """Đồng bộ key lên Render sau khi tạo"""
    try:
        # Đọc keys hiện tại
        keys = load_keys()
        # Gửi lên Render (hoặc lưu vào file rồi push lên GitHub)
        # ... (code chi tiết sau)
    except:
        pass
```

## LƯU Ý

- Render **FREE** sẽ sleep sau 15 phút không dùng
- Khi có request, server tự wake up (mất ~30s lần đầu)
- Nếu muốn không sleep → Upgrade lên paid ($7/tháng)

## HỖ TRỢ

Nếu gặp lỗi, liên hệ qua Discord!
