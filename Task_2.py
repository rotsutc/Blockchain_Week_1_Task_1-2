import hashlib
import time
import os

# ----------------------------------
# Helper: đo thời gian hash
# ----------------------------------
def benchmark(hash_func, label, rounds=500000):
    data = os.urandom(128)
    start = time.time()
    for _ in range(rounds):
        hash_func(data)
    end = time.time()
    print(f"{label}: {end - start:.4f} s")

# ----------------------------------
# Thử nghiệm
# ----------------------------------
def sha256(x):
    return hashlib.sha256(x).digest()

def sha3_256(x):
    return hashlib.sha3_256(x).digest()

def blake2b(x):
    return hashlib.blake2b(x, digest_size=32).digest()

print("=== Benchmark Hash Functions ===")
benchmark(sha256, "SHA-256")
benchmark(sha3_256, "SHA-3")
benchmark(blake2b, "BLAKE2b")

# ----------------------------------
# Kiểm tra output giống C (nếu có)
# ----------------------------------
print("\n=== Check Sample Hash Values ===")
msg = b"Hello Blockchain"
print("SHA-256 :", hashlib.sha256(msg).hexdigest())
print("SHA-3   :", hashlib.sha3_256(msg).hexdigest())
print("BLAKE2b :", hashlib.blake2b(msg, digest_size=32).hexdigest())
