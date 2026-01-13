def oil_columns(matrix):
    rows = len(matrix)
    cols = len(matrix[0])

    oil_cols = []  # chứa danh sách mỗi vùng dầu loang
    visited = [False] * cols

    for c in range(cols):
        # kiểm tra xem cột này có ít nhất 1 ô dầu không
        has_oil = any(matrix[r][c] == 1 for r in range(rows))
        if not has_oil:
            continue

        if visited[c]:
            continue

        # bắt đầu tạo một vùng mới
        region = []
        stack = [c]
        visited[c] = True

        while stack:
            col = stack.pop()

            # lấy tất cả vị trí trong cột này
            for r in range(rows):
                if matrix[r][col] == 1:
                    region.append([r, col])

            # xem cột bên cạnh có nối không (dù là 0)
            for nc in [col - 1, col + 1]:
                if 0 <= nc < cols and not visited[nc]:
                    # nếu cột bên cạnh có dầu, coi như nối
                    if any(matrix[r][nc] == 1 for r in range(rows)):
                        visited[nc] = True
                        stack.append(nc)

        oil_cols.append(region)

    return oil_cols


# Test
matrix = [
    [1,1,1,0],
    [0,0,0,1],
    [1,1,0,0],
    [0,0,0,0]
]

regions = oil_columns(matrix)

print("Số vùng dầu loang:", len(regions))
for i, reg in enumerate(regions, 1):
    print(f"Vị trí {i}:", reg)
