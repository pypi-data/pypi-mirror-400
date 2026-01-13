
tknp = """
def binary_search(a, target):
    l, r = 0, len(a) - 1
    while l <= r:
        mid = (l + r) // 2
        if a[mid] == target: return mid
        if a[mid] < target: l = mid + 1
        else: r = mid - 1
    return -1
"""


lam_tron_so = """
def lam_tron_so(so_dau_vao):
  # Sử dụng f-string với định dạng :.2f
  # .2f nghĩa là format số float (f) với 2 chữ số sau dấu thập phân (.)
  return f"{so_dau_vao:.2f}"
"""
#Tên hàm: doc_file
doc_file = """
def doc_file(duong_dan_file):
    try:
        with open(duong_dan_file, 'r', encoding='utf-8') as file:
            noi_dung = file.read()
        return noi_dung
    except FileNotFoundError:
        return "Lỗi: Không tìm thấy file tại đường dẫn đã cho."
    except Exception as e:
        return f"Lỗi không xác định khi đọc file: {e}"
"""
#Tên hàm: tim_bcnn
tim_bcnn = """
def tim_ucln(a, b):
    # Hàm UCLN (dựa trên thuật toán Euclid) được nhúng để sử dụng
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a

def tim_bcnn(a, b):
    if a == 0 or b == 0:
        # BCNN của bất kỳ số nào với 0 là 0
        return 0
    
    # Tính UCLN
    ucln = tim_ucln(a, b)
    
    # Tính BCNN theo công thức
    # Lấy giá trị tuyệt đối của tích và chia cho UCLN
    bcnn = abs(a * b) // ucln
    
    return bcnn
"""
#Tên hàm: tim_vi_tri

tim_vi_tri = """
def tim_vi_tri(ma_tran, N):
    # Lặp qua từng hàng (row_index)
    for i, hang in enumerate(ma_tran):
        try:
            # Tìm vị trí cột (col_index) của N trong hàng hiện tại
            j = hang.index(N)
            return i, j  # Trả về (hàng, cột) ngay khi tìm thấy
        except ValueError:
            # Nếu N không có trong hàng hiện tại, tiếp tục sang hàng kế tiếp
            continue
    
    # Nếu vòng lặp kết thúc mà không tìm thấy
    return -1, -1
"""

thuat_toan_tham_lam = """
def thuat_toan_tham_lam(jobs):
    jobs.sort(key=lambda x: x[1])
    
    selected_jobs = []
    end_time = 0 # Thời gian kết thúc của công việc được chọn gần nhất
    
    for start, finish in jobs:
        # Nếu thời gian bắt đầu của công việc hiện tại (start)
        # Lớn hơn hoặc bằng thời gian kết thúc của công việc đã chọn trước đó (end_time)
        if start >= end_time:
            # Chọn công việc này
            selected_jobs.append((start, finish))
            # Cập nhật thời gian kết thúc mới
            end_time = finish
            
    return selected_jobs
"""
#Tên hàm: giai_bai_que_tinh
giai_bai_que_tinh = """
def giai_bai_que_tinh(n):
    n = int(n)
    
    # 1. Tính MAX S: Tổng bình phương các số từ 1 đến n
    # Công thức: n*(n+1)*(2n+1)/6
    max_s = (n * (n + 1) * (2 * n + 1)) // 6
    
    # 2. Tính MIN S: Tổng tích của dãy tăng dần nhân dãy giảm dần
    # Công thức rút gọn: n*(n+1)*(n+2)/6
    min_s = (n * (n + 1) * (n + 2)) // 6
    
    return f"{max_s} {min_s}"
"""    
#Tên hàm: tim_ucln
ucln = """
def ucln(a, b):
    # Xử lý trường hợp số âm hoặc số không hợp lệ nếu cần, 
    # nhưng thường UCLN được định nghĩa cho số dương. 
    # Ta sẽ làm việc với giá trị tuyệt đối để đảm bảo thuật toán hoạt động.
    a = abs(a)
    b = abs(b)

    # Thuật toán Euclid
    while b:
        # Gán a thành b, và b thành phần dư của a chia b
        a, b = b, a % b
        
    # Khi b = 0, giá trị cuối cùng của a chính là UCLN
    return a
"""
sapxep = """
def quicksort(a):
    if len(a) <= 1: return a
    pivot = a[len(a)//2]
    left  = [x for x in a if x < pivot]
    mid   = [x for x in a if x == pivot]
    right = [x for x in a if x > pivot]
    return quicksort(left) + mid + quicksort(right)
"""

snt = """
def eratosthenes(n):
    isprime = [True]*(n+1)
    isprime[0] = isprime[1] = False
    for i in range(2, int(n**0.5)+1):
        if isprime[i]:
            for j in range(i*i, n+1, i):
                isprime[j] = False
    return [i for i in range(n+1) if isprime[i]]
"""

bfs = """
from collections import deque

def bfs_shortest(grid, start, end):
    rows, cols = len(grid), len(grid[0])
    q = deque([(start[0], start[1], 0)])
    visited = set([start])

    while q:
        r, c, d = q.popleft()
        if (r, c) == end: return d
        
        for dr, dc in [(1,0),(-1,0),(0,1),(0,-1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and (nr,nc) not in visited and grid[nr][nc] == 0:
                visited.add((nr,nc))
                q.append((nr,nc,d+1))
    return -1
"""

loang = """
def count_oil_spills(matrix):
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
        return 0 <= r < rows and 0 <= c < cols

    def dfs(r, c):
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

"""
#Tên hàm: tinh_tong_1_den_n
tinh_tong_1_den_n = """
def tinh_tong_1_den_n(n):
    # Công thức Gauss: n * (n + 1) / 2
    # Sử dụng phép chia lấy nguyên (//) để kết quả là số nguyên (int)
    return (n * (n + 1)) // 2
"""
#Tên hàm: tim_mode
tim_mode = """
from collections import Counter
def tim_mode(danh_sach_so):
    if not danh_sach_so:
        return None # Trả về None nếu danh sách rỗng

    # 1. Đếm tần suất sử dụng Counter
    tan_suat = Counter(danh_sach_so)
    
    # 2. Tìm phần tử có tần suất cao nhất
    # most_common(1) trả về list chứa 1 tuple: [(phần tử, số lần xuất hiện)]
    # [0] để lấy tuple đầu tiên, [0] tiếp theo để lấy phần tử (số)
    mode = tan_suat.most_common(1)[0][0]
    
    return mode
"""
dp = """
def longest_increasing_subsequence(a):
    n = len(a)
    dp = [1]*n
    for i in range(n):
        for j in range(i):
            if a[j] < a[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)
"""

matran = """
def read_matrix_from_file(path):
    matrix = []
    with open(path, "r") as f:
        for line in f:
            nums = list(map(int, line.strip().split()))
            matrix.append(nums)
    return matrix
"""
# 2. Kiểm tra số chính phương
kiem_tra_chinh_phuong = """
def kiem_tra_chinh_phuong(so_n):
    if so_n < 0: return False
    can_bac_hai = int(pow(so_n, 0.5))
    return pow(can_bac_hai, 2) == so_n
"""

# 3. Sắp xếp tối ưu (Sử dụng thuật toán Timsort có sẵn)
sap_xep_nhanh = """
def sap_xep_toi_uu(mang):
    mang.sort()
    return mang
"""

# 4. Kiểm tra xâu con liên tiếp (Substring)
xau_con_lien_tiep = """
def kiem_tra_con_lien_tiep(xau_me, xau_con):
    return xau_con in xau_me
"""

# 5. Kiểm tra xâu chứa trong (Subsequence - không cần liên tiếp)
xau_chua_trong = """
def kiem_tra_day_con(xau_me, xau_con):
    it = iter(xau_me)
    return all(ky_tu in it for ky_tu in xau_con)
"""

# 6. Tách các cụm số từ chuỗi
tach_so_tu_xau = """
import re
def tach_so_tu_xau(xau_vao):
    return [int(s) for s in re.findall(r'\d+', xau_vao)]
"""
# 1. Mảng cộng dồn 2 chiều (Truy vấn tổng hình chữ nhật con trong O(1))
mang_cong_don_2d = """
def tao_mang_cong_don_2d(ma_tran):
    R, C = len(ma_tran), len(ma_tran[0])
    P = [[0] * (C + 1) for _ in range(R + 1)]
    for r in range(R):
        for c in range(C):
            P[r+1][c+1] = ma_tran[r][c] + P[r][c+1] + P[r+1][c] - P[r][c]
    return P

def truy_van_tong_2d(P, r1, c1, r2, c2):
    # Tính tổng vùng từ (r1, c1) đến (r2, c2)
    return P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
"""

# 2. Cửa sổ trượt (Tìm tổng lớn nhất của k phần tử liên tiếp)
cua_so_truot = """
tìm tổng lớn nhất của k phần tử liên tiếp
def tong_lien_tiep_max(mang, k):
    n = len(mang)
    if n < k: return 0
    tong_hien_tai = sum(mang[:k])
    tong_max = tong_hien_tai
    for i in range(n - k):
        tong_hien_tai = tong_hien_tai - mang[i] + mang[i + k]
        tong_max = max(tong_max, tong_hien_tai)
    return tong_max
"""

# 3. Hai con trỏ (Tìm cặp số có tổng bằng Target trong mảng đã sắp xếp)
hai_con_tro = """
tìm cặp số có tổng = n
def tim_cap_tong(mang_da_sap_xep, muc_tieu):
    trai, phai = 0, len(mang_da_sap_xep) - 1
    while trai < phai:
        tong = mang_da_sap_xep[trai] + mang_da_sap_xep[phai]
        if tong == muc_tieu:
            return trai, phai
        elif tong < muc_tieu:
            trai += 1
        else:
            phai -= 1
    return -1, -1
"""

# 4. Tìm mảng con có tổng lớn nhất (Thuật toán Kadane)
kadane = """
tìm đoạn con liên tiếp có tổng lớn nhất
def tong_mang_con_lon_nhat(mang):
    max_tong = mang[0]
    hien_tai = mang[0]
    for i in range(1, len(mang)):
        hien_tai = max(mang[i], hien_tai + mang[i])
        max_tong = max(max_tong, hien_tai)
    return max_tong
"""
# 7. Tách vị trí xâu con chủ động
tim_vi_tri_xau = """
tách xâu n trong xâu mẹ
def tim_vi_tri_xau(xau_me, xau_con):
    vi_tri_dau = xau_me.find(xau_con)
    if vi_tri_dau == -1:
        return False, []
    tat_ca_vi_tri = []
    index = vi_tri_dau
    while index != -1:
        tat_ca_vi_tri.append(index)
        index = xau_me.find(xau_con, index + 1)
    return True, tat_ca_vi_tri
"""

# 8. Mảng cộng dồn (Prefix Sum)
mang_cong_don = """
tổng toàn bộ 1 vùng từ vị trí đầu tiên đến vị trí [x,y]
def tao_mang_cong_don(mang):
    p = [0] * (len(mang) + 1)
    for i in range(len(mang)):
        p[i+1] = p[i] + mang[i]
    return p
"""

allcmd = """
def allcmd():
    return "tknp, lam_tron_so, doc_file, tim_bcnn, tim_vi_tri, thuat_toan_tham_lam, giai_bai_que_tinh, ucln, sapxep, snt, bfs, loang, tinh_tong_1_den_n, tim_mode, dp, matran"
"""
__all__ = [
    "allcmd",
    "tknp",
    "lam_tron_so",
    "doc_file",
    "tim_bcnn",
    "tim_vi_tri",
    "thuat_toan_tham_lam",
    "giai_bai_que_tinh",
    "ucln",
    "sapxep",
    "snt",
    "bfs",
    "loang",
    "tinh_tong_1_den_n",
    "tim_mode",
    "dp",
    "matran",
    "mang_cong_don_2d",
    "cua_so_truot",
    "hai_con_tro",
    "kadane",
    "he_thong_te_p",
    "kiem_tra_chinh_phuong",
    "sapxep_moi",
    "xau_con_lien_tiep",
    "xau_chua_trong",
    "tach_so_tu_xau",
    "tim_vi_tri_xau",
    "mang_cong_don"
]
