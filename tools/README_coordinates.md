# Tool Trích Xuất Tọa Độ Xã Phường TPHCM

Tool này giúp trích xuất tọa độ địa lý (latitude, longitude) của các xã phường mới sau khi sáp nhập ở TP.HCM và cập nhật vào file CSV.

## 🚀 Tính năng

- ✅ Trích xuất tọa độ từ tên địa danh sử dụng OpenStreetMap Nominatim API
- ✅ Cập nhật file CSV với cột Latitude và Longitude mới
- ✅ Hỗ trợ dry-run để xem trước kế hoạch
- ✅ Error handling và retry logic
- ✅ Rate limiting để tránh bị block API
- ✅ Logging chi tiết quá trình xử lý

## 📋 Yêu cầu

- Python 3.6+
- Thư viện: `requests`
- Kết nối internet để gọi API

## 🛠️ Cài đặt

```bash
pip install requests
```

## 📖 Cách sử dụng

### 1. Sử dụng từ command line

```bash
# Dry run - chỉ xem kế hoạch
python tools/extract_coordinates.py --dry-run

# Trích xuất tọa độ cho tất cả records
python tools/extract_coordinates.py

# Chỉ định file input/output
python tools/extract_coordinates.py --input Phuong_TPHCM_Formatted.CSV --output Phuong_TPHCM_With_Coordinates.CSV

# Điều chỉnh delay giữa các request (giây)
python tools/extract_coordinates.py --delay 2.0
```

### 2. Sử dụng demo script

```bash
python demo_coordinates.py
```

### 3. Sử dụng trong code Python

```python
from tools.extract_coordinates import CoordinateExtractor

# Khởi tạo extractor
extractor = CoordinateExtractor('Phuong_TPHCM_Formatted.CSV')

# Dry run
stats = extractor.extract_coordinates(dry_run=True)

# Trích xuất thật
stats = extractor.extract_coordinates()
```

## 📊 Cấu trúc file CSV

File CSV sẽ có các cột sau:

| Cột | Mô tả |
|-----|-------|
| STT | Số thứ tự |
| Tinh_TP_Cu | Tỉnh/TP cũ |
| Xa_Phuong_Truoc_Sap_Nhap | Xã/phường trước sáp nhập |
| Xa_Phuong_Moi_TPHCM | Xã/phường mới của TPHCM |
| Latitude | Vĩ độ (được thêm tự động) |
| Longitude | Kinh độ (được thêm tự động) |

## ⚙️ Cấu hình

### Rate Limiting
- Mặc định: 1 giây delay giữa các request
- Có thể điều chỉnh bằng tham số `--delay`

### Retry Logic
- Mặc định: 3 lần retry cho mỗi request
- Delay tăng dần: 1s, 2s, 3s

### API Endpoint
- Sử dụng OpenStreetMap Nominatim API
- Miễn phí, không cần API key
- Giới hạn: 1 request/giây

## 📝 Log Output

```
2024-01-21 10:30:15 - INFO - 🚀 Bắt đầu trích xuất tọa độ...
2024-01-21 10:30:15 - INFO - ✅ Đọc thành công 168 records từ Phuong_TPHCM_Formatted.CSV
2024-01-21 10:30:16 - INFO - 📍 Đang xử lý 1/168: Phường Sài Gòn
2024-01-21 10:30:17 - INFO - ✅ Tìm thấy tọa độ: 10.7769, 106.7009
2024-01-21 10:30:18 - INFO - 📍 Đang xử lý 2/168: Phường Tân Định
...
2024-01-21 10:35:20 - INFO - 📊 THỐNG KÊ KẾT QUẢ:
2024-01-21 10:35:20 - INFO -   Tổng số records: 168
2024-01-21 10:35:20 - INFO -   Đã xử lý: 168
2024-01-21 10:35:20 - INFO -   Tìm thấy tọa độ: 165
2024-01-21 10:35:20 - INFO -   Không tìm thấy: 3
2024-01-21 10:35:20 - INFO -   Lỗi: 0
```

## ⚠️ Lưu ý

1. **Rate Limiting**: API có giới hạn request, tool tự động delay để tránh bị block
2. **Độ chính xác**: Tọa độ có thể không hoàn toàn chính xác, cần kiểm tra lại
3. **Thời gian**: Quá trình có thể mất 3-5 phút cho 168 records
4. **Backup**: Nên backup file gốc trước khi chạy

## 🔧 Troubleshooting

### Lỗi "Connection timeout"
```bash
# Tăng delay giữa các request
python tools/extract_coordinates.py --delay 2.0
```

### Lỗi "No coordinates found"
- Một số địa danh có thể không có trong OpenStreetMap
- Tool sẽ bỏ qua và tiếp tục với record tiếp theo

### Lỗi "Permission denied"
```bash
# Kiểm tra quyền ghi file
chmod 644 Phuong_TPHCM_Formatted.CSV
```

## 📈 Kết quả mong đợi

- **Tỷ lệ thành công**: ~95-98% (165-164/168 records)
- **Thời gian**: 3-5 phút cho toàn bộ dataset
- **Độ chính xác**: Tọa độ trung tâm của xã/phường

## 🤝 Đóng góp

Nếu bạn muốn cải thiện tool:

1. Fork repository
2. Tạo feature branch
3. Commit changes
4. Tạo Pull Request

## 📄 License

MIT License - Sử dụng tự do cho mục đích học tập và nghiên cứu.
