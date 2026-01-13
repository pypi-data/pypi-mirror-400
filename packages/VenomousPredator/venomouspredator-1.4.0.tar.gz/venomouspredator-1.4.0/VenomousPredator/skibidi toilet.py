def tim_ucln(a, b):
    a = abs(a)
    b = abs(b)
    while b:
        a, b = b, a % b
    return a

def tim_bcnn(a, b):
    if a == 0 or b == 0:
        return 0
    
    # Tính UCLN
    ucln = tim_ucln(a, b)
    
    # Tính BCNN theo công thức
    # Lấy giá trị tuyệt đối của tích và chia cho UCLN
    bcnn = abs(a * b) // ucln
    
    return bcnn