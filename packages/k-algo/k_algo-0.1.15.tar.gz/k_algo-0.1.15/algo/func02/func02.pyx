# cython: language_level=3
import cython

@cython.locals(n=cython.int, a=cython.int, b=cython.int, i=cython.int)
def fib(n: int) -> int:
    """回傳第 n 個 Fibonacci 數"""
    if n <= 0:
        return 0
    elif n == 1:
        return 1

    a, b = 0, 1
    for i in range(2, n + 1):
        a, b = b, a + b
    return b
