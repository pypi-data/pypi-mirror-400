def count_oil_spills(matrix):
    """
    Đếm số lượng vùng dầu loang độc lập trong ma trận, 
    sử dụng thuật toán DFS với 8 hướng kết nối.
    """
    if not matrix or not matrix[0]:
        return 0

    rows = len(matrix)
    cols = len(matrix[0])
    count = 0

    # 8 hướng di chuyển: (lên, xuống, trái, phải, chéo trên trái/phải, chéo dưới trái/phải)
    directions = [
        (-1, 0), (1, 0), (0, -1), (0, 1), 
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    def is_valid(r, c):
        """Kiểm tra xem (r, c) có nằm trong ma trận hay không."""
        return 0 <= r < rows and 0 <= c < cols

    def dfs(r, c):
        """
        Thực hiện tìm kiếm theo chiều sâu, đánh dấu tất cả các ô dầu loang 
        kết nối với (r, c) là đã được thăm (bằng cách đổi thành 0).
        """
        # Đánh dấu ô hiện tại là đã thăm
        matrix[r][c] = 0

        # Thăm các ô kề theo 8 hướng
        for dr, dc in directions:
            new_r, new_c = r + dr, c + dc
            
            # Nếu ô mới hợp lệ và là dầu loang (1)
            if is_valid(new_r, new_c) and matrix[new_r][new_c] == 1:
                dfs(new_r, new_c)

    # Duyệt qua toàn bộ ma trận
    for r in range(rows):
        for c in range(cols):
            # Nếu tìm thấy một ô dầu loang chưa được thăm (giá trị là 1)
            if matrix[r][c] == 1:
                count += 1      # Tăng số lượng vùng dầu loang
                dfs(r, c)       # Bắt đầu loang để đánh dấu toàn bộ vùng này

    return count

# Dữ liệu đầu vào của bạn
matrix_input = [
    [1,1,1,0],
    [0,0,0,1],
    [1,1,0,0],
    [0,0,0,0],
    [1,1,1,0]
]

# Lưu ý: Hàm sẽ thay đổi ma trận gốc. Nếu muốn giữ ma trận gốc, bạn nên copy nó trước khi gọi hàm.
# matrix_copy = [row[:] for row in matrix_input]

result = count_oil_spills(matrix_input)
print(f"Số lượng vùng dầu loang độc lập là: {result}")