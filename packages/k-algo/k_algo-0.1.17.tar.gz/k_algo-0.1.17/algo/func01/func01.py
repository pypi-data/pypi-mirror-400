# cython: language_level=3
import cython

@cython.locals(n=cython.int, result=cython.int, i=cython.int)
def factorial(n: int) -> int:
    """計算 n!"""
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result
