from signum import sign
from testing import get_passes, set_high_priority, success

from math import nan
import os
import psutil
import time

MAX_PASSES = get_passes(__file__)

def benchmark_and_leak_check():
    process = psutil.Process(os.getpid())

    # Test data
    test_cases = [
        ("Base (int)", lambda: sign(-5)),
        ("Base (float)", lambda: sign(-5.5)),
        ("Preprocess (str)", lambda: sign("15 men", preprocess=lambda s: (float(s.split()[0]),))),
        ("If_exc (error)", lambda: sign("error", if_exc=(-2,))),
        ("Codeshift (error)", lambda: sign("error", codeshift=2)),
        ("Codeshift (int)", lambda: sign(-5, codeshift=2)),
        ("Codeshift (nan)", lambda: sign(nan, codeshift=2)),
    ]

    print(f"{'Test Case':<20} | {'Time (s)':<10} | {'Memory (MB)':<12}")
    print("-" * 53)

    for name, func in test_cases:
        # Before
        start_mem = process.memory_info().rss / 1024 / 1024
        start_time = time.perf_counter()

        # Main loop (MAX_PASSES calls)
        for _ in range(MAX_PASSES):
            func()

        # After
        end_time = time.perf_counter()
        end_mem = process.memory_info().rss / 1024 / 1024

        duration = end_time - start_time
        mem_diff = end_mem - start_mem

        print(f"{name:<20} | {duration:>9.4f} | {end_mem:>10.2f} ({mem_diff:+.2f})")

if __name__ == "__main__":

    print(f'***** Test: {__file__}')
    print(f'MAX_PASSES: {MAX_PASSES}')
    print(f'*** {set_high_priority()} ***\n')

    for _ in range(MAX_PASSES): # Warm up Python
        sign(1)
    benchmark_and_leak_check()
    print(f'\n{success(7, passes=MAX_PASSES)}')
