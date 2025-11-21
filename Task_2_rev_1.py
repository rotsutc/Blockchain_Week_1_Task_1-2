import hashlib
import time
import matplotlib.pyplot as plt
import numpy as np
import os

# ============================
# 1. HASH FUNCTIONS
# ============================
def sha256(data):
    return hashlib.sha256(data).digest()

def sha3(data):
    return hashlib.sha3_256(data).digest()

def blake2b(data):
    return hashlib.blake2b(data, digest_size=32).digest()

hash_functions = {
    "SHA-256": sha256,
    "SHA-3": sha3,
    "BLAKE2b": blake2b
}

# ============================
# 2. COLLISION RESISTANCE TEST
# ============================
def collision_test():
    print("\n=== Collision (Avalanche Effect) Test ===")
    msg1 = b"Blockchain va ung dung"
    msg2 = b"Blockchain va Ung dung"  # chỉ khác 1 ký tự

    for name, func in hash_functions.items():
        h1 = func(msg1).hex()
        h2 = func(msg2).hex()
        print(f"\n{name}:")
        print(f" msg1 hash = {h1}")
        print(f" msg2 hash = {h2}")
        print(f" Difference = {sum(a!=b for a,b in zip(h1,h2))} / {len(h1)} hex chars")

collision_test()

# ============================
# 3. PERFORMANCE BENCHMARK
# ============================
def benchmark_speed(num_iters=200000):
    print("\n=== Benchmark Speed ===")

    results = {}

    for name, func in hash_functions.items():
        data = os.urandom(32)
        start = time.time()
        for _ in range(num_iters):
            func(data)
        end = time.time()

        elapsed = end - start
        results[name] = elapsed
        print(f"{name}: {elapsed:.4f} sec ({num_iters} hashes)")

    return results

speed_results = benchmark_speed()

# ============================
# 4. THROUGHPUT TEST (MB/s)
# ============================
def benchmark_throughput(block_size=4096, num_iters=50000):
    print("\n=== Benchmark Throughput ===")

    throughput = {}
    data = os.urandom(block_size)

    for name, func in hash_functions.items():
        start = time.time()
        for _ in range(num_iters):
            func(data)
        end = time.time()

        total_bytes = block_size * num_iters
        mbps = (total_bytes / (1024 * 1024)) / (end - start)

        throughput[name] = mbps
        print(f"{name}: {mbps:.2f} MB/s")

    return throughput

throughput_results = benchmark_throughput()

# ============================
# 5. DRAW CHARTS
# ============================

# ---- Performance Time Chart ----
plt.figure(figsize=(7, 5))
plt.bar(speed_results.keys(), speed_results.values())
plt.title("Hiệu suất hàm băm (Thời gian / 200k hashes)")
plt.ylabel("Thời gian (giây)")
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.show()

# ---- Throughput Chart ----
plt.figure(figsize=(7, 5))
plt.bar(throughput_results.keys(), throughput_results.values())
plt.title("Thông lượng hàm băm (MB/s, block size 4096B)")
plt.ylabel("MB/s")
plt.grid(axis="y", linestyle="--", alpha=0.6)
plt.show()
