#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Thuật toán di truyền giải bài toán Multi-Vehicle TSP với Time Windows cho TP.HCM
Advanced Genetic Algorithm for Multi-Vehicle TSP with Time Windows
"""

import pandas as pd
import numpy as np
import random
import math
import time
from typing import List, Tuple, Dict, Optional
import json
from datetime import datetime, timedelta

class MultiVehicleTSPGA:
    """Thuật toán di truyền giải bài toán Multi-Vehicle TSP với Time Windows"""
    
    def __init__(self, coords: Dict[str, Tuple[float, float]], 
                 num_vehicles: int = 3,
                 population_size: int = 100, 
                 generations: int = 500,
                 mutation_rate: float = 0.1,
                 elite_ratio: float = 0.1,
                 time_windows: Optional[Dict[str, Tuple[int, int]]] = None):
        """
        Khởi tạo thuật toán di truyền Multi-Vehicle TSP
        
        Args:
            coords: Dictionary chứa tọa độ các điểm
            num_vehicles: Số lượng xe giao hàng
            population_size: Kích thước quần thể
            generations: Số thế hệ
            mutation_rate: Tỷ lệ đột biến
            elite_ratio: Tỷ lệ elitism
            time_windows: Time windows cho từng điểm (start_time, end_time) tính bằng phút từ 0h
        """
        self.coords = coords
        self.locations = list(coords.keys())
        self.num_vehicles = num_vehicles
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = int(population_size * elite_ratio)
        
        # Time windows (mặc định: 8h-18h cho tất cả điểm)
        self.time_windows = time_windows or {
            loc: (480, 1080) for loc in self.locations  # 8h-18h
        }
        
        # Giờ cao điểm (7h-9h, 17h-19h)
        self.rush_hours = [(420, 540), (1020, 1140)]  # 7h-9h, 17h-19h
        
        # Không phân chia theo quận/huyện, chỉ tối ưu theo tọa độ phường/xã
        
        # Lưu lịch sử tiến hóa
        self.fitness_history = []
        self.best_routes_history = []
        
        # Thêm logic dừng sớm
        self.stagnation_threshold = 2000  # Tăng lên 2000 thế hệ để hội tụ hoàn toàn
        self.best_fitness = 0
        self.stagnation_count = 0
        
    
    def haversine_distance(self, lat1: float, lon1: float, 
                          lat2: float, lon2: float) -> float:
        """
        Tính khoảng cách giữa hai điểm theo công thức Haversine
        
        Args:
            lat1, lon1: Tọa độ điểm 1
            lat2, lon2: Tọa độ điểm 2
            
        Returns:
            Khoảng cách tính bằng km
        """
        R = 6371  # Bán kính Trái Đất (km)
        
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        
        a = (math.sin(dphi/2)**2 + 
             math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2)
        
        return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    def calculate_travel_time(self, lat1: float, lon1: float, 
                             lat2: float, lon2: float, 
                             current_time: int = 480) -> int:
        """
        Tính thời gian di chuyển giữa hai điểm (tính bằng phút)
        
        Args:
            lat1, lon1: Tọa độ điểm đầu
            lat2, lon2: Tọa độ điểm cuối
            current_time: Thời gian hiện tại (phút từ 0h)
            
        Returns:
            Thời gian di chuyển tính bằng phút
        """
        distance = self.haversine_distance(lat1, lon1, lat2, lon2)
        
        # Tốc độ trung bình (km/h)
        base_speed = 30  # 30 km/h trong giờ bình thường
        
        # Giảm tốc độ trong giờ cao điểm
        for rush_start, rush_end in self.rush_hours:
            if rush_start <= current_time <= rush_end:
                base_speed = 20  # 20 km/h trong giờ cao điểm
                break
        
        # Thời gian di chuyển (phút)
        travel_time = (distance / base_speed) * 60
        
        return int(travel_time)
    
    def is_time_window_valid(self, location: str, arrival_time: int) -> bool:
        """
        Kiểm tra xem thời gian đến có trong time window không
        
        Args:
            location: Tên địa điểm
            arrival_time: Thời gian đến (phút từ 0h)
            
        Returns:
            True nếu trong time window, False nếu không
        """
        start_time, end_time = self.time_windows[location]
        return start_time <= arrival_time <= end_time
    
    def create_initial_population(self) -> List[List[List[str]]]:
        """
        Tạo quần thể ban đầu cho Multi-Vehicle TSP
        
        Returns:
            Danh sách các giải pháp (mỗi giải pháp là danh sách routes cho các xe)
        """
        population = []
        
        for _ in range(self.population_size):
            # Tạo giải pháp ngẫu nhiên
            solution = self._create_random_solution()
            population.append(solution)
            
        return population
    
    def _create_kmeans_clustered_solution(self) -> List[List[str]]:
        """
        Tạo giải pháp dựa trên K-means clustering để phân chia địa lý tốt hơn
        """
        from sklearn.cluster import KMeans
        
        # Chuẩn bị dữ liệu tọa độ
        coords_array = np.array([self.coords[loc] for loc in self.locations])
        
        # K-means clustering
        kmeans = KMeans(n_clusters=self.num_vehicles, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(coords_array)
        
        # Phân chia locations theo cluster
        routes = [[] for _ in range(self.num_vehicles)]
        for i, loc in enumerate(self.locations):
            cluster_id = cluster_labels[i]
            routes[cluster_id].append(loc)
        
        # Cân bằng số điểm giữa các xe
        return self._balance_quadrants(routes)
    
    def _create_geographic_clustered_solution(self) -> List[List[str]]:
        """
        Tạo giải pháp dựa trên clustering địa lý để cân bằng hiệu quả tốt hơn
        
        Returns:
            Danh sách routes cho các xe
        """
        all_locations = self.locations.copy()
        
        # Tính trung tâm địa lý
        center_lat = sum(self.coords[loc][0] for loc in all_locations) / len(all_locations)
        center_lon = sum(self.coords[loc][1] for loc in all_locations) / len(all_locations)
        
        # Chia thành các góc phần tư dựa trên trung tâm
        quadrants = [[] for _ in range(self.num_vehicles)]
        
        # Calculate max_distance_from_center for num_vehicles > 4 case
        max_distance_from_center = 0
        if self.num_vehicles > 4:
            for loc in all_locations:
                lat, lon = self.coords[loc]
                dist = ((lat - center_lat)**2 + (lon - center_lon)**2)**0.5
                if dist > max_distance_from_center:
                    max_distance_from_center = dist

        for loc in all_locations:
            lat, lon = self.coords[loc]
            
            # Xác định góc phần tư dựa trên số xe
            if self.num_vehicles == 2:
                # Chia đôi theo kinh độ
                quadrant = 0 if lon >= center_lon else 1
            elif self.num_vehicles == 3:
                # Chia thành 3 vùng
                if lat >= center_lat:
                    quadrant = 0 if lon >= center_lon else 1
                else:
                    quadrant = 2
            elif self.num_vehicles == 4:
                # Chia thành 4 góc phần tư
                if lat >= center_lat and lon >= center_lon:
                    quadrant = 0  # Đông Bắc
                elif lat >= center_lat and lon < center_lon:
                    quadrant = 1  # Tây Bắc
                elif lat < center_lat and lon >= center_lon:
                    quadrant = 2  # Đông Nam
                else:
                    quadrant = 3  # Tây Nam
            else:
                # Cho số xe > 4, chia theo khoảng cách từ trung tâm
                distance_from_center = ((lat - center_lat)**2 + (lon - center_lon)**2)**0.5
                quadrant = int((distance_from_center / max_distance_from_center) * self.num_vehicles) % self.num_vehicles
            
            quadrants[quadrant].append(loc)
        
        # Cân bằng số điểm giữa các vùng
        routes = self._balance_quadrants(quadrants)
        
        return routes
    
    def _balance_quadrants(self, quadrants: List[List[str]]) -> List[List[str]]:
        """
        Cân bằng số điểm giữa các vùng để tránh xe nào quá ít điểm
        
        Args:
            quadrants: Danh sách các vùng với điểm
            
        Returns:
            Routes đã cân bằng
        """
        all_locations = []
        for quadrant in quadrants:
            all_locations.extend(quadrant)
        
        # Tính số điểm trung bình mỗi xe
        avg_points = len(all_locations) // self.num_vehicles
        remaining_points = len(all_locations) % self.num_vehicles
        
        # Phân chia lại để cân bằng
        balanced_routes = []
        start_idx = 0
        
        for i in range(self.num_vehicles):
            # Tính số điểm cho xe này
            if i < remaining_points:
                vehicle_points = avg_points + 1
            else:
                vehicle_points = avg_points
            
            # Lấy điểm cho xe này
            end_idx = start_idx + vehicle_points
            vehicle_locations = all_locations[start_idx:end_idx]
            
            # Tạo route ngẫu nhiên cho xe này
            if vehicle_locations:
                random.shuffle(vehicle_locations)
                balanced_routes.append(vehicle_locations)
            else:
                balanced_routes.append([])
            
            start_idx = end_idx
        
        return balanced_routes
    
    def _create_random_solution(self) -> List[List[str]]:
        """
        Tạo một giải pháp ngẫu nhiên cho Multi-Vehicle TSP
        
        Returns:
            Danh sách routes cho các xe
        """
        # 60% tạo giải pháp K-means clustering, 30% geographic clustering, 10% ngẫu nhiên
        rand = random.random()
        if rand < 0.6:
            return self._create_kmeans_clustered_solution()
        elif rand < 0.9:
            return self._create_geographic_clustered_solution()
        else:
            # Tạo routes cho từng xe với đa dạng hơn
            routes = []
            all_locations = self.locations.copy()
            random.shuffle(all_locations)
            
            # Chia đều số điểm cho các xe nhưng cho phép một chút biến động
            points_per_vehicle = len(all_locations) // self.num_vehicles
            remaining_points = len(all_locations) % self.num_vehicles
            
            start_idx = 0
            for vehicle_id in range(self.num_vehicles):
                # Tính số điểm cho xe này với một chút biến động
                if vehicle_id < remaining_points:
                    base_points = points_per_vehicle + 1
                else:
                    base_points = points_per_vehicle
                
                # Thêm biến động ngẫu nhiên (±2 điểm)
                variation = random.randint(-2, 2)
                vehicle_points = max(1, base_points + variation)
                
                # Đảm bảo không vượt quá số điểm còn lại
                remaining = len(all_locations) - start_idx
                vehicle_points = min(vehicle_points, remaining)
                
                # Lấy điểm cho xe này
                end_idx = start_idx + vehicle_points
                vehicle_locations = all_locations[start_idx:end_idx]
                
                # Tạo route ngẫu nhiên cho xe này
                if vehicle_locations:
                    random.shuffle(vehicle_locations)
                    routes.append(vehicle_locations)
                else:
                    routes.append([])
                
                start_idx = end_idx
            
            return routes
    
    def route_distance(self, route: List[str]) -> float:
        """
        Tính tổng khoảng cách của một lộ trình
        
        Args:
            route: Danh sách các điểm theo thứ tự
            
        Returns:
            Tổng khoảng cách tính bằng km
        """
        if not route:
            return 0
            
        total_distance = 0
        
        for i in range(len(route) - 1):
            coord1 = self.coords[route[i]]
            coord2 = self.coords[route[i + 1]]
            total_distance += self.haversine_distance(*coord1, *coord2)
        
        # Quay về điểm xuất phát
        coord1 = self.coords[route[-1]]
        coord2 = self.coords[route[0]]
        total_distance += self.haversine_distance(*coord1, *coord2)
        
        return total_distance
    
    def multi_objective_fitness(self, solution: List[List[str]]) -> tuple:
        """
        Hàm fitness đa mục tiêu cải tiến: tối ưu khoảng cách và cân bằng hiệu quả
        
        Args:
            solution: Giải pháp gồm routes cho các xe
            
        Returns:
            Tuple (distance_fitness, efficiency_balance_fitness) - càng cao càng tốt
        """
        total_distance = 0
        vehicle_distances = []
        
        for vehicle_id, route in enumerate(solution):
            if not route:
                vehicle_distances.append(0)
                continue
            route_dist = self.route_distance(route)
            total_distance += route_dist
            vehicle_distances.append(route_dist)
        
        # Mục tiêu 1: Tối ưu tổng khoảng cách với scaling tốt hơn
        # Sử dụng exponential để tăng độ nhạy với khoảng cách ngắn
        distance_fitness = np.exp(-total_distance / 10000)  # Scaling tốt hơn
        
        # Mục tiêu 2: Cân bằng hiệu quả giữa các xe (cải tiến)
        if len(vehicle_distances) > 1 and max(vehicle_distances) > 0:
            max_distance = max(vehicle_distances)
            min_distance = min(vehicle_distances)
            
            # Tính coefficient of variation (CV) để đo độ phân tán
            mean_distance = np.mean(vehicle_distances)
            std_distance = np.std(vehicle_distances)
            
            if mean_distance > 0:
                cv = std_distance / mean_distance
                # Fitness cân bằng: CV càng thấp càng tốt
                efficiency_balance_fitness = np.exp(-cv * 2)  # Exponential penalty cho CV cao
            else:
                efficiency_balance_fitness = 1.0
        else:
            efficiency_balance_fitness = 1.0
        
        return (distance_fitness, efficiency_balance_fitness)
    
    def adaptive_fitness(self, solution: List[List[str]], generation: int) -> float:
        """
        Hàm fitness thích ứng: điều chỉnh trọng số theo thế hệ
        
        Args:
            solution: Giải pháp gồm routes cho các xe
            generation: Thế hệ hiện tại
            
        Returns:
            Giá trị fitness tổng hợp
        """
        distance_fitness, efficiency_balance_fitness = self.multi_objective_fitness(solution)
        
        # Trọng số thích ứng: tập trung hoàn toàn vào khoảng cách
        total_generations = self.generations
        
        # Tất cả các giai đoạn đều tập trung vào khoảng cách
        distance_weight = 0.95  # Tập trung 95% vào khoảng cách
        efficiency_weight = 0.05  # Chỉ 5% cho cân bằng hiệu quả
        
        # Fitness tổng hợp với trọng số thích ứng
        combined_fitness = (distance_weight * distance_fitness + 
                          efficiency_weight * efficiency_balance_fitness)
        
        return combined_fitness
    
    def local_search_2opt(self, solution: List[List[str]]) -> List[List[str]]:
        """
        Local search 2-opt để cải thiện từng route
        """
        improved_solution = []
        
        for route in solution:
            if len(route) <= 2:
                improved_solution.append(route)
                continue
                
            best_route = route.copy()
            best_distance = self.route_distance(route)
            improved = True
            
            while improved:
                improved = False
                for i in range(1, len(best_route) - 1):
                    for j in range(i + 1, len(best_route)):
                        # Thử 2-opt swap
                        new_route = best_route[:i] + best_route[i:j+1][::-1] + best_route[j+1:]
                        new_distance = self.route_distance(new_route)
                        
                        if new_distance < best_distance:
                            best_route = new_route
                            best_distance = new_distance
                            improved = True
                            break
                    if improved:
                        break
            
            improved_solution.append(best_route)
        
        return improved_solution
    
    def balance_load_local_search(self, solution: List[List[str]]) -> List[List[str]]:
        """
        Local search để cân bằng tải giữa các xe
        """
        improved_solution = [route.copy() for route in solution]
        
        # Tính khoảng cách mỗi xe
        vehicle_distances = []
        for route in improved_solution:
            if route:
                vehicle_distances.append(self.route_distance(route))
            else:
                vehicle_distances.append(0)
        
        # Tìm xe có khoảng cách lớn nhất và nhỏ nhất
        max_distance_idx = vehicle_distances.index(max(vehicle_distances))
        min_distance_idx = vehicle_distances.index(min(vehicle_distances))
        
        # Nếu chênh lệch quá lớn, di chuyển điểm
        if vehicle_distances[max_distance_idx] - vehicle_distances[min_distance_idx] > 50:
            if len(improved_solution[max_distance_idx]) > 1:
                # Chọn điểm tốt nhất để di chuyển
                point_to_move = self._find_best_point_for_efficiency(
                    improved_solution[max_distance_idx], improved_solution[min_distance_idx]
                )
                
                if point_to_move:
                    improved_solution[max_distance_idx].remove(point_to_move)
                    improved_solution[min_distance_idx].append(point_to_move)
        
        return improved_solution
    
    def _balance_efficiency_post_optimization(self, solution: List[List[str]]) -> List[List[str]]:
        """
        Cân bằng hiệu quả sau khi tối ưu bằng cách di chuyển điểm giữa các xe
        
        Args:
            solution: Giải pháp cần cân bằng
            
        Returns:
            Giải pháp đã cân bằng hiệu quả
        """
        # Tính khoảng cách mỗi xe
        vehicle_distances = []
        for route in solution:
            if route:
                vehicle_distances.append(self.route_distance(route))
            else:
                vehicle_distances.append(0)
        
        # Tìm xe có khoảng cách lớn nhất và nhỏ nhất
        max_distance_idx = vehicle_distances.index(max(vehicle_distances))
        min_distance_idx = vehicle_distances.index(min(vehicle_distances))
        
        # Nếu chênh lệch quá lớn (>200km), cân bằng hiệu quả (tăng threshold cao)
        if vehicle_distances[max_distance_idx] - vehicle_distances[min_distance_idx] > 200:
            # Di chuyển một điểm từ xe có khoảng cách lớn sang xe có khoảng cách nhỏ
            if len(solution[max_distance_idx]) > 1:
                # Chọn điểm tốt nhất để di chuyển (gần nhất với xe đích)
                point_to_move = self._find_best_point_for_efficiency(
                    solution[max_distance_idx], solution[min_distance_idx]
                )
                
                if point_to_move:
                    # Di chuyển điểm
                    solution[max_distance_idx].remove(point_to_move)
                    solution[min_distance_idx].append(point_to_move)
        
        return solution
    
    def _find_best_point_for_efficiency(self, from_route: List[str], to_route: List[str]) -> str:
        """
        Tìm điểm tốt nhất để di chuyển nhằm cân bằng hiệu quả
        
        Args:
            from_route: Route có khoảng cách lớn
            to_route: Route có khoảng cách nhỏ
            
        Returns:
            Điểm tốt nhất để di chuyển
        """
        if not from_route or not to_route:
            return from_route[0] if from_route else None
        
        # Tìm điểm mà khi di chuyển sẽ giảm chênh lệch hiệu quả nhất
        best_point = None
        best_improvement = 0
        
        for point in from_route:
            # Tính khoảng cách hiện tại của route đích
            current_to_distance = self.route_distance(to_route)
            
            # Tính khoảng cách mới nếu thêm điểm này
            new_to_route = to_route + [point]
            new_to_distance = self.route_distance(new_to_route)
            
            # Tính khoảng cách mới của route nguồn
            new_from_route = [p for p in from_route if p != point]
            new_from_distance = self.route_distance(new_from_route) if new_from_route else 0
            
            # Tính cải thiện cân bằng hiệu quả
            current_imbalance = abs(self.route_distance(from_route) - current_to_distance)
            new_imbalance = abs(new_from_distance - new_to_distance)
            improvement = current_imbalance - new_imbalance
            
            if improvement > best_improvement:
                best_improvement = improvement
                best_point = point
        
        return best_point
    
    def _validate_minimum_load(self, solution: List[List[str]]) -> List[List[str]]:
        """
        Validation: đảm bảo không có xe nào quá ít điểm
        
        Args:
            solution: Giải pháp cần validation
            
        Returns:
            Giải pháp đã được validation
        """
        vehicle_loads = [len(route) for route in solution]
        
        # Tính số điểm trung bình
        avg_load = sum(vehicle_loads) / len(vehicle_loads)
        min_threshold = avg_load * 0.3  # Tối thiểu 30% số điểm trung bình
        
        # Tìm xe có ít điểm nhất
        min_load_idx = vehicle_loads.index(min(vehicle_loads))
        
        # Nếu xe có ít điểm nhất quá ít, di chuyển điểm từ xe có nhiều điểm nhất
        if vehicle_loads[min_load_idx] < min_threshold:
            max_load_idx = vehicle_loads.index(max(vehicle_loads))
            
            # Di chuyển điểm từ xe có nhiều điểm sang xe có ít điểm
            if len(solution[max_load_idx]) > 1:
                # Chọn điểm tốt nhất để di chuyển
                point_to_move = self._find_best_point_for_efficiency(
                    solution[max_load_idx], solution[min_load_idx]
                )
                
                if point_to_move:
                    solution[max_load_idx].remove(point_to_move)
                    solution[min_load_idx].append(point_to_move)
        
        return solution
    
    def run_multi_vehicle_ga(self) -> Dict:
        """
        Chạy thuật toán di truyền cho Multi-Vehicle TSP
        
        Returns:
            Dictionary chứa kết quả tối ưu
        """
        print("Khoi tao quan the ban dau...")
        population = self.create_initial_population()
        
        best_solution = None
        best_fitness = 0
        
        for generation in range(self.generations):
            # Đánh giá fitness cho từng giải pháp với adaptive fitness
            fitness_scores = [self.adaptive_fitness(solution, generation) for solution in population]
            
            # Tìm giải pháp tốt nhất
            best_idx = np.argmax(fitness_scores)
            current_best_fitness = fitness_scores[best_idx]
            
            if current_best_fitness > best_fitness:
                best_fitness = current_best_fitness
                best_solution = population[best_idx].copy()
                self.stagnation_count = 0  # Reset stagnation counter
            else:
                self.stagnation_count += 1  # Tăng stagnation counter
            
            # Áp dụng local search cho giải pháp tốt nhất mỗi 100 thế hệ
            if generation % 100 == 0 and generation > 0:
                improved_solution = self.local_search_2opt(best_solution)
                improved_fitness = self.adaptive_fitness(improved_solution, generation)
                if improved_fitness > best_fitness:
                    best_fitness = improved_fitness
                    best_solution = improved_solution
                    print(f"Local search cải thiện tại thế hệ {generation}: {improved_fitness:.6f}")
            
            # Áp dụng balance load local search mỗi 200 thế hệ
            if generation % 200 == 0 and generation > 0:
                balanced_solution = self.balance_load_local_search(best_solution)
                balanced_fitness = self.adaptive_fitness(balanced_solution, generation)
                if balanced_fitness > best_fitness:
                    best_fitness = balanced_fitness
                    best_solution = balanced_solution
                    print(f"Balance load cải thiện tại thế hệ {generation}: {balanced_fitness:.6f}")
            
            # Lưu lịch sử
            self.fitness_history.append(best_fitness)
            self.best_routes_history.append(best_solution.copy())
            
            # Kiểm tra dừng sớm nếu không có cải thiện
            if self.stagnation_count >= self.stagnation_threshold:
                print(f"\nDung som tai the he {generation}: Khong co cai thien trong {self.stagnation_threshold} the he")
                break
            
            # In tiến độ với thông tin chi tiết
            if generation % 50 == 0:
                # Tính các mục tiêu riêng biệt để hiển thị
                distance_fit, efficiency_balance_fit = self.multi_objective_fitness(best_solution)
                print(f"The he {generation}: Fitness = {best_fitness:.6f} "
                      f"(Distance: {distance_fit:.6f}, Efficiency Balance: {efficiency_balance_fit:.6f})")
            
            # Tạo quần thể mới
            new_population = []
            
            # Elitism: giữ lại các giải pháp tốt nhất
            elite_indices = np.argsort(fitness_scores)[-self.elite_size:]
            for idx in elite_indices:
                new_population.append(population[idx].copy())
            
            # Tạo các giải pháp mới bằng crossover và mutation
            while len(new_population) < self.population_size:
                # Chọn cha mẹ
                parent1 = self._tournament_selection_multi(population, fitness_scores)
                parent2 = self._tournament_selection_multi(population, fitness_scores)
                
                # Tạo con
                child = self._multi_vehicle_crossover(parent1, parent2)
                
                # Đột biến
                if random.random() < self.mutation_rate:
                    child = self._multi_vehicle_mutation(child)
                
                new_population.append(child)
            
            population = new_population
        
        # Cân bằng hiệu quả sau khi tối ưu (giảm số lần để tập trung vào khoảng cách)
        balanced_solution = best_solution
        for _ in range(3):  # Giảm xuống 3 lần để tập trung vào khoảng cách
            balanced_solution = self._balance_efficiency_post_optimization(balanced_solution)
        
        # Validation: đảm bảo không có xe nào quá ít điểm
        balanced_solution = self._validate_minimum_load(balanced_solution)
        
        # Tính toán kết quả cuối cùng với giải pháp đã cân bằng hiệu quả
        result = self._calculate_final_results(balanced_solution)
        
        return result
    
    def _tournament_selection_multi(self, population: List[List[List[str]]], 
                                   fitness_scores: List[float], k: int = 3) -> List[List[str]]:
        """Tournament selection cho Multi-Vehicle TSP"""
        tournament_indices = random.sample(range(len(population)), k)
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_idx].copy()
    
    def _multi_vehicle_crossover(self, parent1: List[List[str]], 
                                parent2: List[List[str]]) -> List[List[str]]:
        """Crossover cho Multi-Vehicle TSP - phân chia ngẫu nhiên theo tọa độ"""
        child = []
        
        # Lấy tất cả địa điểm từ cả hai cha mẹ
        all_locations = set()
        for route in parent1 + parent2:
            all_locations.update(route)
        
        # Phân chia ngẫu nhiên các địa điểm cho các xe
        all_locations = list(all_locations)
        random.shuffle(all_locations)
        
        # Phân chia đều cho các xe
        points_per_vehicle = len(all_locations) // self.num_vehicles
        remaining_points = len(all_locations) % self.num_vehicles
        
        start_idx = 0
        for vehicle_id in range(self.num_vehicles):
            # Tính số điểm cho xe này
            vehicle_points = points_per_vehicle
            if vehicle_id < remaining_points:
                vehicle_points += 1
            
            # Lấy điểm cho xe này
            end_idx = start_idx + vehicle_points
            vehicle_locations = all_locations[start_idx:end_idx]
            
            child.append(vehicle_locations)
            start_idx = end_idx
        
        return child
    
    def _multi_vehicle_mutation(self, solution: List[List[str]]) -> List[List[str]]:
        """Mutation cho Multi-Vehicle TSP"""
        mutated = [route.copy() for route in solution]
        
        # Hoán đổi ngẫu nhiên hai địa điểm trong cùng một route
        for route in mutated:
            if len(route) > 1:
                i, j = random.sample(range(len(route)), 2)
                route[i], route[j] = route[j], route[i]
        
        return mutated
    
    def _calculate_final_results(self, best_solution: List[List[str]]) -> Dict:
        """Tính toán kết quả cuối cùng"""
        results = {
            'best_solution': best_solution,
            'vehicle_routes': [],
            'total_distance': 0,
            'total_time': 0,
            'fitness_history': self.fitness_history,
            'time_window_violations': 0
        }
        
        for vehicle_id, route in enumerate(best_solution):
            if not route:
                continue
                
            route_info = {
                'vehicle_id': vehicle_id,
                'route': route,
                'distance': self.route_distance(route),
                'time': 0
            }
            
            # Tính thời gian và kiểm tra time windows
            current_time = 480  # Bắt đầu lúc 8h sáng
            violations = 0
            
            for i, location in enumerate(route):
                # Kiểm tra time window
                if not self.is_time_window_valid(location, current_time):
                    violations += 1
                
                # Cập nhật thời gian
                if i < len(route) - 1:
                    next_location = route[i + 1]
                    coord1 = self.coords[location]
                    coord2 = self.coords[next_location]
                    travel_time = self.calculate_travel_time(*coord1, *coord2, current_time)
                    current_time += travel_time + 15  # Thêm 15 phút để giao hàng
                
                # Không cần ghi nhận quận/huyện nữa
            
            route_info['time'] = current_time - 480  # Thời gian làm việc (phút)
            
            results['vehicle_routes'].append(route_info)
            results['total_distance'] += route_info['distance']
            results['total_time'] += route_info['time']
            results['time_window_violations'] += violations
        
        return results

def load_data(csv_file: str) -> Dict[str, Tuple[float, float]]:
    """
    Tải dữ liệu từ file CSV
    
    Args:
        csv_file: Đường dẫn đến file CSV
        
    Returns:
        Dictionary chứa tọa độ các điểm
    """
    print(f"Dang tai du lieu tu {csv_file}...")
    
    df = pd.read_csv(csv_file)
    
    coords = {}
    for _, row in df.iterrows():
        name = row['Xa_Phuong_Moi_TPHCM']
        lat = row['Latitude']
        lon = row['Longitude']
        
        # Kiểm tra tọa độ hợp lệ
        if pd.notna(lat) and pd.notna(lon):
            coords[name] = (float(lat), float(lon))
    
    print(f"Da tai {len(coords)} phuong/xa voi toa do hop le")
    return coords

if __name__ == "__main__":
    print("Multi-Vehicle TSP with Time Windows - TP.HCM")
    print("=" * 50)
    
    # Tải dữ liệu
    coords = load_data('data/Phuong_TPHCM_With_Coordinates.CSV')
    
    if len(coords) == 0:
        print("Khong co du lieu hop le!")
        exit(1)
    
    # Sử dụng 4 xe mặc định
    num_vehicles = 4
    
    print(f"Using {num_vehicles} vehicles")
    print()
    
    # Khởi tạo thuật toán tập trung hoàn toàn vào khoảng cách
    ga = MultiVehicleTSPGA(
        coords=coords,
        num_vehicles=num_vehicles,
        population_size=250,  # Tăng population để đa dạng tối đa
        generations=20000,    # Tăng lên 20,000 thế hệ để hội tụ hoàn toàn
        mutation_rate=0.3,   # Giữ mutation cao để tìm kiếm tốt
        elite_ratio=0.05     # Giữ elite thấp để đa dạng
    )
    
    # Chạy thuật toán
    results = ga.run_multi_vehicle_ga()
    
    # In kết quả
    print("\nKET QUA TOI UU:")
    print("-" * 40)
    print(f"Tong khoang cach: {results['total_distance']:.2f} km")
    print(f"Tong thoi gian: {results['total_time']:.1f} phut")
    print(f"Vi pham time window: {results['time_window_violations']}")
    print(f"So xe su dung: {len([r for r in results['vehicle_routes'] if r['route']])}")
    
    # Lưu kết quả
    with open('results/multi_vehicle_tsp_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print("Da luu ket qua vao results/multi_vehicle_tsp_results.json")