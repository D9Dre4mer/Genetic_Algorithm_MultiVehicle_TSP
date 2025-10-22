# 🧬 Genetic Algorithm for Multi-Vehicle TSP Optimization

*Giải thuật di truyền tối ưu hóa bài toán di chuyển trong ngành Logistic cho 168 phường, xã mới sau khi sát nhập ở TP.HCM.*

## 📋 Tổng quan

Dự án này sử dụng **Giải thuật Di truyền (Genetic Algorithm)** để giải quyết bài toán **Multi-Vehicle Traveling Salesman Problem (TSP)** cho 168 phường/xã ở TP.HCM sau sáp nhập hành chính năm 2025. Thuật toán tập trung tối đa vào việc giảm khoảng cách di chuyển tổng thể.

## 🎯 Mục tiêu

- **Mục tiêu chính**: Tối thiểu hóa tổng quãng đường di chuyển
- **Kết quả**: Đạt 1,614 km cho 168 phường với 4 xe giao hàng
- **Hội tụ**: Thuật toán hội tụ hoàn toàn tại thế hệ 2000

## ⚠️ Lưu ý quan trọng

**Hạn chế về khoảng cách**: Thuật toán hiện tại sử dụng khoảng cách Haversine (đường chim bay) chứ không phải khoảng cách thực tế theo đường xe cơ giới. Khoảng cách thực tế có thể lớn hơn 1.5-2 lần do hệ thống đường xá.

## 📁 Cấu trúc dự án

```
Genetic_Algorithm_MultiVehicle_TSP/
├── data/
│   └── Phuong_TPHCM_With_Coordinates.CSV    # Dữ liệu 168 phường với tọa độ
├── src/
│   ├── tsp_solver.py                        # Giải thuật di truyền Multi-Vehicle TSP
│   ├── create_visualizations.py             # Tạo biểu đồ phân tích
│   └── create_maps.py                       # Tạo bản đồ routes
├── results/
│   ├── route_map.png                        # Bản đồ routes cho các xe
│   ├── efficiency_map.png                   # Bản đồ hiệu quả từng xe
│   ├── evolution.png                        # Biểu đồ tiến hóa (hội tụ hoàn toàn)
│   ├── vehicle_analysis.png                 # Phân tích từng xe
│   ├── algorithm_performance.png            # Hiệu suất thuật toán
│   ├── before_after_comparison.png          # So sánh trước/sau
│   ├── summary_report.html                  # Báo cáo tổng hợp
│   └── multi_vehicle_tsp_results.json       # Kết quả JSON (1,614 km)
├── docs/
│   └── genetic-algorithm-tsp-hcmc.md         # Tài liệu chi tiết về giải thuật di truyền
├── tools/
│   └── upload_and_rewrite.py                # Tool upload ảnh lên ImgBB
├── requirements.txt                          # Dependencies Python
└── README.md                                 # File này
```

## 🚀 Cài đặt và chạy

### 1. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 2. Chạy thuật toán

```bash
cd src
python tsp_solver.py
```

Nhập số xe giao hàng (2-8) khi được yêu cầu.

### 3. Tạo visualizations

```bash
python create_visualizations.py
python create_maps.py
```

## 📁 Hướng dẫn sử dụng thư mục `src/`

### 🧬 `tsp_solver.py` - Giải thuật di truyền chính

**Mục đích**: File chính chứa thuật toán di truyền để giải bài toán Multi-Vehicle TSP.

**Tính năng**:
- ✅ Nhập số xe giao hàng (2-8 xe)
- ✅ Tự động tải dữ liệu từ `../data/Phuong_TPHCM_With_Coordinates.CSV`
- ✅ Chạy thuật toán di truyền với 20,000 thế hệ
- ✅ Early stopping khi hội tụ (2000 thế hệ)
- ✅ Xuất kết quả ra `../results/multi_vehicle_tsp_results.json`

**Tham số có thể điều chỉnh**:
```python
# Trong hàm main()
population_size = 250        # Kích thước quần thể
generations = 20000         # Số thế hệ tối đa
mutation_rate = 0.3         # Tỷ lệ đột biến (30%)
elite_ratio = 0.05          # Tỷ lệ cá thể ưu tú (5%)
stagnation_threshold = 2000 # Ngưỡng dừng sớm
```

### 📊 `create_visualizations.py` - Tạo biểu đồ phân tích

**Mục đích**: Tạo các biểu đồ phân tích kết quả thuật toán.

**Output files** (trong `../results/`):
- 📈 `evolution.png` - Biểu đồ tiến hóa fitness
- 🚚 `vehicle_analysis.png` - Phân tích từng xe (khoảng cách, thời gian, số điểm)
- ⚡ `algorithm_performance.png` - Hiệu suất thuật toán qua thế hệ
- 📊 `before_after_comparison.png` - So sánh trước/sau tối ưu
- 📋 `summary_report.html` - Báo cáo tổng hợp HTML

**Tính năng**:
- ✅ Đọc kết quả từ `multi_vehicle_tsp_results.json`
- ✅ Tạo biểu đồ với matplotlib/seaborn
- ✅ Hỗ trợ tiếng Việt
- ✅ Xuất file chất lượng cao (300 DPI)

### 🗺️ `create_maps.py` - Tạo bản đồ routes

**Mục đích**: Tạo bản đồ trực quan cho routes của các xe.

**Output files** (trong `../results/`):
- 🗺️ `route_map.png` - Bản đồ routes cho tất cả xe
- ⚡ `efficiency_map.png` - Bản đồ hiệu quả từng xe

**Tính năng**:
- ✅ Sử dụng Folium để tạo bản đồ tương tác
- ✅ Hiển thị routes với màu sắc khác nhau cho từng xe
- ✅ Marker cho điểm xuất phát và đích đến
- ✅ Popup thông tin chi tiết cho từng điểm

### ⚙️ Tùy chỉnh nâng cao

**Thay đổi số xe**:
```python
# Trong tsp_solver.py, hàm main()
num_vehicles = int(input("Nhập số xe giao hàng (2-8): "))
```

**Thay đổi tham số GA**:
```python
# Trong tsp_solver.py, class MultiVehicleTSPGA
def __init__(self, ...):
    self.population_size = 250      # Tăng để khám phá tốt hơn
    self.generations = 20000       # Tăng để hội tụ tốt hơn
    self.mutation_rate = 0.3       # Giảm để ổn định hơn
    self.elite_ratio = 0.05        # Tăng để giữ cá thể tốt
```

**Thay đổi dữ liệu đầu vào**:
```python
# Trong tsp_solver.py, hàm load_data()
df = pd.read_csv('../data/Phuong_TPHCM_With_Coordinates.CSV')
# Thay đổi đường dẫn file CSV tại đây
```

## 📊 Kết quả chính

### Thống kê bài toán
- **Số phường/xã**: 168
- **Số xe giao hàng**: 4
- **Population Size**: 250
- **Generations**: 20,000
- **Early Stopping**: 2000 thế hệ

### Kết quả tối ưu
- **Tổng khoảng cách**: 1,614.0 km (đường chim bay)
- **Tổng thời gian**: 5,765 phút (ước tính)
- **Vi phạm time window**: 82
- **Số xe sử dụng**: 4

### Phân bố khoảng cách
- **Xe 1**: 41 điểm, 531.9 km (13.0 km/điểm)
- **Xe 2**: 45 điểm, 334.4 km (7.4 km/điểm)  
- **Xe 3**: 42 điểm, 360.5 km (8.6 km/điểm)
- **Xe 4**: 40 điểm, 526.4 km (13.2 km/điểm)

## 🔧 Thuật toán

### Các thành phần chính
1. **Geographic Clustering**: Chia TP.HCM thành các vùng địa lý
2. **Distance-Focused Weighting**: 95% khoảng cách, 5% cân bằng tải
3. **Exponential Fitness**: Scaling tốt hơn cho khoảng cách ngắn
4. **Local Search**: 2-opt và balance load
5. **Early Stopping**: Dừng khi hội tụ hoàn toàn

### Tham số tối ưu
- **Population Size**: 250
- **Generations**: 20,000
- **Mutation Rate**: 30%
- **Elite Ratio**: 5%
- **Early Stopping**: 2000 thế hệ

## 📈 Tiến trình hội tụ

- **Thế hệ 0**: Fitness = 0.618256
- **Thế hệ 100**: Local search cải thiện lên 0.826206
- **Thế hệ 200**: Balance load cải thiện lên 0.829503
- **Thế hệ 300**: Local search cải thiện lên 0.834379
- **Thế hệ 300-2000**: **HỘI TỤ HOÀN TOÀN** - Fitness ổn định tại 0.834379

## 🎯 Ứng dụng thực tế

- **Logistics đô thị**: Tối ưu lộ trình cho nhiều xe giao hàng
- **Giao hàng Tết**: Phân chia địa bàn hợp lý cho hàng triệu đơn hàng
- **Drone delivery**: Tối ưu khoảng cách cho đội drone
- **Giao thông công cộng**: Tối ưu tuyến xe bus, taxi
- **Delivery apps**: Grab, Gojek áp dụng cho tài xế

## 🔮 Gợi ý mở rộng

### 🚚 Dynamic Vehicle Assignment
- Tự động điều chỉnh số xe dựa trên khối lượng công việc
- Tích hợp với hệ thống quản lý xe

### 🕐 Real-time Traffic Integration
- Tích hợp API giao thông thực tế (Google Maps, HERE)
- Cập nhật lộ trình theo tình hình giao thông

### ⚡ Machine Learning Enhancement
- Sử dụng ML để dự đoán thời gian giao hàng
- Tối ưu dựa trên dữ liệu lịch sử và mô hình thời tiết

### 🎯 Advanced Distance Optimization
- Tích hợp API bản đồ thực tế (Google Maps, OpenStreetMap)
- Tính khoảng cách theo đường xe cơ giới thực tế
- Xem xét thời gian giao thông và tắc đường
- Áp dụng ma trận khoảng cách thực tế thay vì Haversine

## 📚 Tài liệu tham khảo

1. Holland, J. H. (1975). *Adaptation in Natural and Artificial Systems*.
2. Goldberg, D. E. (1989). *Genetic Algorithms in Search, Optimization, and Machine Learning*.
3. DEAP Framework (2024). *Evolutionary Algorithms in Python*.
4. Cổng thông tin TP.HCM (2025). *Danh sách 168 phường, xã, thị trấn sau sáp nhập*.
5. OpenStreetMap Nominatim API (2025). *Geocoding Service*.

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 👥 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

---

**⚠️ Lưu ý quan trọng**: Kết quả hiện tại dựa trên khoảng cách Haversine (đường chim bay). Để áp dụng thực tế, cần tích hợp API bản đồ để tính khoảng cách theo đường xe cơ giới thực tế.
