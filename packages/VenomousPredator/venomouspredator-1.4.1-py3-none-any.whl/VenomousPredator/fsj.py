import heapq
import sys

try:
    # Đọc n (số mốc) và m (số đường đi)
    print("Nhập n (số điểm) và m (số đường):")
    input_nm = sys.stdin.readline().split()
    if not input_nm:
        print(0)
    n, m = map(int, input_nm)

    # Khởi tạo đồ thị bằng danh sách kề
    # graph[u] = [(v, weight), ...]
    graph = {i: [] for i in range(1, n + 1)}

    print(f"Nhập {m} dòng tiếp theo (u v w):")
    for _ in range(m):
        u, v, w = map(int, sys.stdin.readline().split())
        # Thêm đường đi một chiều từ u đến v với trọng số w
        graph[u].append((v, w))
        
        # LƯU Ý: Nếu đồ thị là vô hướng (đi từ 1->2 cũng như 2->1),
        # hãy bỏ comment dòng bên dưới:
        # graph[v].append((u, w))

    # Đọc điểm bắt đầu và kết thúc
    print("Nhập điểm bắt đầu và kết thúc:")
    start_node, end_node = map(int, sys.stdin.readline().split())

    # Khởi tạo khoảng cách:
    # Tất cả là vô cùng (infinity), trừ điểm xuất phát là 0
    distances = {node: float('inf') for node in range(1, n + 1)}
    distances[start_node] = 0

    # Hàng đợi ưu tiên: lưu tuple (khoảng_cách, đỉnh)
    priority_queue = [(0, start_node)]

    while priority_queue:
        # Lấy ra đỉnh có khoảng cách ngắn nhất hiện tại
        current_dist, current_u = heapq.heappop(priority_queue)

        # Nếu khoảng cách lấy ra lớn hơn khoảng cách đã ghi nhận -> Bỏ qua
        if current_dist > distances[current_u]:
            continue

        # Nếu đã đến đích, có thể dừng sớm (tùy chọn)
        if current_u == end_node:
            break

        # Duyệt các đỉnh kề
        for neighbor, weight in graph[current_u]:
            distance = current_dist + weight

            # Nếu tìm thấy đường đi ngắn hơn -> Cập nhật
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(priority_queue, (distance, neighbor))

    # Kết quả
    result = distances[end_node]
    if result == float('inf'):
        print(f"Kết quả: Không có đường đi từ {start_node} đến {end_node}")
    else:
        print(f"Kết quả độ dài ngắn nhất: {result}")

except ValueError:
    print("Lỗi: Vui lòng nhập đúng định dạng số.")
