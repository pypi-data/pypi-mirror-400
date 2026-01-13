import numpy as np

def call_numpy(n):
# 建立一個陣列
    x = np.array(n)

    # 向量化運算（逐元素）
    print(f"call_numpy: x + 1 = {x + 1}")      # -> [2 3 4 5]
    print(f"call_numpy: x * x = {x * x}")      # -> [ 1  4  9 16]

    # 常用統計
    print(f"call_numpy: x.sum() = {x.sum()}")    # -> 10
    print(f"call_numpy: x.mean() = {x.mean()}")   # -> 2.5