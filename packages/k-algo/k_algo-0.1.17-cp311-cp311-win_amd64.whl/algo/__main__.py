# algo/__main__.py
from . import factorial, fib, fast_sum, call_numpy, call_pandas

def main() -> None:
    print("5! =", factorial(5))
    print("Fib(10) =", fib(10))
    print(fast_sum([1, 2, 3.5]))   # -> 6.5
    call_numpy([1, 2, 3.5])
    call_pandas()

if __name__ == "__main__":
    main()
