#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tạo bản đồ đơn giản cho Multi-Vehicle TSP bằng matplotlib
"""

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Dict, List, Tuple

def load_data_and_results():
    """Tải dữ liệu và kết quả"""
    # Tải dữ liệu CSV
    df = pd.read_csv('data/Phuong_TPHCM_With_Coordinates.CSV')
    
    # Tải kết quả TSP
    with open('results/multi_vehicle_tsp_results.json', 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    return df, results

def create_route_map(df: pd.DataFrame, results: Dict, output_file: str = 'results/route_map.png'):
    """Tạo bản đồ routes"""
    import os
    os.makedirs('results', exist_ok=True)
    
    plt.figure(figsize=(16, 12))
    
    # Màu sắc cho từng xe
    colors = ['red', 'blue', 'green', 'purple', 'orange', 'brown', 'pink', 'gray']
    
    # Vẽ tất cả điểm
    plt.scatter(df['Longitude'], df['Latitude'], 
               c='lightgray', s=20, alpha=0.6, label='Tất cả điểm')
    
    # Vẽ routes cho từng xe
    for i, route_info in enumerate(results['vehicle_routes']):
        if not route_info['route']:
            continue
            
        vehicle_id = route_info['vehicle_id']
        route = route_info['route']
        color = colors[vehicle_id % len(colors)]
        
        # Tạo coordinates cho route
        route_coords = []
        for location in route:
            row = df[df['Xa_Phuong_Moi_TPHCM'] == location]
            if not row.empty:
                lat = row.iloc[0]['Latitude']
                lon = row.iloc[0]['Longitude']
                route_coords.append([lon, lat])
        
        if len(route_coords) > 1:
            route_coords = np.array(route_coords)
            
            # Vẽ đường đi
            plt.plot(route_coords[:, 0], route_coords[:, 1], 
                    color=color, linewidth=2, alpha=0.8,
                    label=f'Xe {vehicle_id + 1} ({len(route)} điểm)')
            
            # Vẽ các điểm
            plt.scatter(route_coords[:, 0], route_coords[:, 1], 
                       c=color, s=50, alpha=0.8, edgecolors='black', linewidth=0.5)
            
            # Đánh dấu điểm xuất phát
            plt.scatter(route_coords[0, 0], route_coords[0, 1], 
                       c=color, s=100, marker='s', alpha=1.0, 
                       edgecolors='black', linewidth=2)
    
    plt.title('Multi-Vehicle TSP Routes - TP.HCM', fontsize=16, fontweight='bold')
    plt.xlabel('Kinh độ', fontsize=12)
    plt.ylabel('Vĩ độ', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Da tao ban do routes: {output_file}")

def create_efficiency_map(df: pd.DataFrame, results: Dict, output_file: str = 'results/efficiency_map.png'):
    """Tạo bản đồ hiệu quả từng xe"""
    import os
    os.makedirs('results', exist_ok=True)
    
    fig, axes = plt.subplots(2, 2, figsize=(20, 16))
    axes = axes.flatten()
    
    colors = ['red', 'blue', 'green', 'purple']
    
    for i, route_info in enumerate(results['vehicle_routes']):
        if not route_info['route'] or i >= 4:
            continue
            
        ax = axes[i]
        route = route_info['route']
        color = colors[i]
        
        # Tạo coordinates cho route
        route_coords = []
        for location in route:
            row = df[df['Xa_Phuong_Moi_TPHCM'] == location]
            if not row.empty:
                lat = row.iloc[0]['Latitude']
                lon = row.iloc[0]['Longitude']
                route_coords.append([lon, lat])
        
        if len(route_coords) > 1:
            route_coords = np.array(route_coords)
            
            # Vẽ đường đi
            ax.plot(route_coords[:, 0], route_coords[:, 1], 
                   color=color, linewidth=3, alpha=0.8)
            
            # Vẽ các điểm
            ax.scatter(route_coords[:, 0], route_coords[:, 1], 
                      c=color, s=80, alpha=0.8, edgecolors='black', linewidth=1)
            
            # Đánh dấu điểm xuất phát và kết thúc
            ax.scatter(route_coords[0, 0], route_coords[0, 1], 
                      c=color, s=150, marker='s', alpha=1.0, 
                      edgecolors='black', linewidth=2, label='Xuất phát')
            ax.scatter(route_coords[-1, 0], route_coords[-1, 1], 
                      c=color, s=150, marker='^', alpha=1.0, 
                      edgecolors='black', linewidth=2, label='Kết thúc')
            
            efficiency = route_info['distance'] / len(route)
            ax.set_title(f'Xe {i+1}: {len(route)} điểm, {route_info["distance"]:.1f}km\n'
                        f'Hiệu quả: {efficiency:.1f} km/điểm', fontsize=12, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.legend()
    
    # Ẩn subplot không sử dụng
    for i in range(len([r for r in results['vehicle_routes'] if r['route']]), 4):
        axes[i].set_visible(False)
    
    plt.suptitle('Hiệu quả từng xe giao hàng', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Da tao ban do hieu qua: {output_file}")

def main():
    """Hàm main tạo bản đồ"""
    print("Tao ban do cho Multi-Vehicle TSP...")
    
    # Tải dữ liệu
    df, results = load_data_and_results()
    
    # Tạo các bản đồ (chỉ tập trung vào hiệu quả thuật toán)
    create_route_map(df, results)
    create_efficiency_map(df, results)
    
    print("\nDa tao tat ca ban do!")
    print("Cac file da tao:")
    print("- results/route_map.png: Ban do routes chinh")
    print("- results/efficiency_map.png: Ban do hieu qua tung xe")

if __name__ == "__main__":
    main()