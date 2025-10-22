#!/usr/bin/env python3
"""
Tool để trích xuất tọa độ của các xã phường mới từ file CSV
Sử dụng OpenStreetMap Nominatim API để lấy tọa độ địa lý
"""

import csv
import requests
import time
import json
import os
from typing import Dict, List, Tuple, Optional
import logging

# Cấu hình logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CoordinateExtractor:
    def __init__(self, csv_file: str, output_file: str = None):
        """
        Khởi tạo extractor
        
        Args:
            csv_file: Đường dẫn đến file CSV gốc
            output_file: Đường dẫn file CSV output (nếu None sẽ ghi đè file gốc)
        """
        self.csv_file = csv_file
        self.output_file = output_file or csv_file
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.headers = {
            'User-Agent': 'TPHCM-Ward-Coordinate-Extractor/1.0'
        }
        self.delay = 1.0  # Delay giữa các request để tránh rate limit
        
    def geocode_location(self, location_name: str, retries: int = 3) -> Optional[Tuple[float, float]]:
        """
        Lấy tọa độ từ tên địa danh sử dụng Nominatim API
        
        Args:
            location_name: Tên địa danh cần tìm tọa độ
            retries: Số lần retry nếu fail
            
        Returns:
            Tuple (lat, lon) hoặc None nếu không tìm thấy
        """
        # Chuẩn hóa tên địa danh cho Việt Nam
        search_query = f"{location_name}, TP.HCM, Vietnam"
        
        params = {
            'q': search_query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'vn',
            'addressdetails': 1
        }
        
        for attempt in range(retries):
            try:
                logger.info(f"Đang tìm tọa độ cho: {location_name} (lần thử {attempt + 1})")
                
                response = requests.get(
                    self.nominatim_url, 
                    params=params, 
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                
                data = response.json()
                
                if data and len(data) > 0:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    logger.info(f"✅ Tìm thấy tọa độ: {lat}, {lon}")
                    return (lat, lon)
                else:
                    logger.warning(f"⚠️ Không tìm thấy tọa độ cho: {location_name}")
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Lỗi request (lần thử {attempt + 1}): {e}")
                if attempt < retries - 1:
                    time.sleep(self.delay * (attempt + 1))
                    
            except (ValueError, KeyError) as e:
                logger.error(f"❌ Lỗi parse dữ liệu: {e}")
                break
                
        return None
    
    def read_csv_data(self) -> List[Dict]:
        """
        Đọc dữ liệu từ file CSV
        
        Returns:
            List các dictionary chứa dữ liệu CSV
        """
        data = []
        try:
            with open(self.csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            logger.info(f"✅ Đọc thành công {len(data)} records từ {self.csv_file}")
        except Exception as e:
            logger.error(f"❌ Lỗi đọc file CSV: {e}")
            raise
            
        return data
    
    def write_csv_data(self, data: List[Dict]):
        """
        Ghi dữ liệu vào file CSV
        
        Args:
            data: List các dictionary chứa dữ liệu CSV
        """
        if not data:
            logger.warning("⚠️ Không có dữ liệu để ghi")
            return
            
        try:
            fieldnames = list(data[0].keys())
            with open(self.output_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            logger.info(f"✅ Ghi thành công {len(data)} records vào {self.output_file}")
        except Exception as e:
            logger.error(f"❌ Lỗi ghi file CSV: {e}")
            raise
    
    def extract_coordinates(self, dry_run: bool = False) -> Dict[str, int]:
        """
        Trích xuất tọa độ cho tất cả các xã phường mới
        
        Args:
            dry_run: Nếu True, chỉ hiển thị kế hoạch mà không thực hiện
            
        Returns:
            Dict với thống kê kết quả
        """
        logger.info("🚀 Bắt đầu trích xuất tọa độ...")
        
        # Đọc dữ liệu CSV
        data = self.read_csv_data()
        
        # Thêm cột tọa độ nếu chưa có
        if 'Latitude' not in data[0]:
            for row in data:
                row['Latitude'] = ''
                row['Longitude'] = ''
        
        stats = {
            'total': len(data),
            'processed': 0,
            'found': 0,
            'not_found': 0,
            'errors': 0
        }
        
        if dry_run:
            logger.info("🔍 DRY RUN - Chỉ hiển thị kế hoạch:")
            for i, row in enumerate(data[:5]):  # Chỉ hiển thị 5 records đầu
                ward_name = row['Xa_Phuong_Moi_TPHCM']
                logger.info(f"  {i+1}. Sẽ tìm tọa độ cho: {ward_name}")
            logger.info(f"... và {len(data)-5} records khác")
            return stats
        
        # Xử lý từng record
        for i, row in enumerate(data):
            ward_name = row['Xa_Phuong_Moi_TPHCM']
            
            # Bỏ qua nếu đã có tọa độ
            if row['Latitude'] and row['Longitude']:
                logger.info(f"⏭️ Bỏ qua {ward_name} (đã có tọa độ)")
                stats['processed'] += 1
                continue
            
            logger.info(f"📍 Đang xử lý {i+1}/{len(data)}: {ward_name}")
            
            # Lấy tọa độ
            coordinates = self.geocode_location(ward_name)
            
            if coordinates:
                lat, lon = coordinates
                row['Latitude'] = str(lat)
                row['Longitude'] = str(lon)
                stats['found'] += 1
                logger.info(f"✅ Thành công: {ward_name} -> {lat}, {lon}")
            else:
                stats['not_found'] += 1
                logger.warning(f"⚠️ Không tìm thấy: {ward_name}")
            
            stats['processed'] += 1
            
            # Delay để tránh rate limit
            if i < len(data) - 1:  # Không delay ở record cuối
                time.sleep(self.delay)
        
        # Ghi dữ liệu đã cập nhật
        self.write_csv_data(data)
        
        # In thống kê
        logger.info("📊 THỐNG KÊ KẾT QUẢ:")
        logger.info(f"  Tổng số records: {stats['total']}")
        logger.info(f"  Đã xử lý: {stats['processed']}")
        logger.info(f"  Tìm thấy tọa độ: {stats['found']}")
        logger.info(f"  Không tìm thấy: {stats['not_found']}")
        logger.info(f"  Lỗi: {stats['errors']}")
        
        return stats

def main():
    """
    Hàm main để chạy tool từ command line
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='Trích xuất tọa độ các xã phường TPHCM')
    parser.add_argument('--input', '-i', default='Phuong_TPHCM_Formatted.CSV',
                       help='File CSV input (default: Phuong_TPHCM_Formatted.CSV)')
    parser.add_argument('--output', '-o', 
                       help='File CSV output (nếu không chỉ định sẽ ghi đè file input)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Chỉ hiển thị kế hoạch, không thực hiện')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay giữa các request (giây, default: 1.0)')
    
    args = parser.parse_args()
    
    # Kiểm tra file input tồn tại
    if not os.path.exists(args.input):
        logger.error(f"❌ File không tồn tại: {args.input}")
        return 1
    
    # Khởi tạo extractor
    extractor = CoordinateExtractor(args.input, args.output)
    extractor.delay = args.delay
    
    try:
        # Chạy trích xuất tọa độ
        stats = extractor.extract_coordinates(dry_run=args.dry_run)
        
        if not args.dry_run:
            logger.info("🎉 Hoàn thành trích xuất tọa độ!")
        else:
            logger.info("🔍 Dry run hoàn thành!")
            
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ Dừng bởi người dùng")
        return 1
    except Exception as e:
        logger.error(f"❌ Lỗi không mong muốn: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
