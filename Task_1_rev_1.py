import hashlib
import time
import json
import copy
import sys
from datetime import datetime

# --- CẤU HÌNH MÀU SẮC CHO CONSOLE ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Cấu hình encoding để in tiếng Việt trên Windows
sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# CLASS BLOCK
# ==========================================
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Tính toán mã hash SHA-256 của block."""
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def __str__(self):
        return (f"{Colors.CYAN}Block #{self.index}{Colors.ENDC}\n"
                f"  ├── Time: {datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"  ├── Data: {self.data}\n"
                f"  ├── Hash: {self.hash}\n"
                f"  └── Prev: {self.previous_hash}")

# ==========================================
# CLASS BLOCKCHAIN
# ==========================================
class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 5  # Số lượng số 0 ở đầu
        self.create_genesis_block()

    def create_genesis_block(self):
        print(f"{Colors.HEADER}=== KHỞI TẠO BLOCKCHAIN ==={Colors.ENDC}")
        print("⚙️ Đang tạo Genesis Block...")
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        genesis_block.hash = self.mine_block_internal(genesis_block)
        self.chain.append(genesis_block)
        print(f"{Colors.GREEN}✔ Genesis Block đã tạo thành công.{Colors.ENDC}\n")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        """Thêm block đã đào vào chuỗi và in thông báo đẹp."""
        start_time = time.time()
        print(f"⛏️  Đang đào Block #{new_block.index}...", end="\r")
        
        # Thực hiện Proof of Work
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = self.mine_block_internal(new_block)
        
        self.chain.append(new_block)
        elapsed = time.time() - start_time
        
        print(f"{Colors.GREEN}✔ Block #{new_block.index} đã đào xong ({elapsed:.4f}s){Colors.ENDC}")
        print(f"  ├── Nonce: {new_block.nonce}")
        print(f"  └── Hash : {new_block.hash}\n")

    def mine_block_internal(self, block):
        """Core của thuật toán PoW."""
        target = "0" * self.difficulty
        while not block.calculate_hash().startswith(target):
            block.nonce += 1
        return block.calculate_hash()

    def mine_block(self, data):
        """API để người dùng thêm dữ liệu."""
        latest_block = self.get_latest_block()
        new_block = Block(latest_block.index + 1, time.time(), data, latest_block.hash)
        self.add_block(new_block)

    def is_chain_valid(self, verbose=True):
        """Kiểm tra tính toàn vẹn. Verbose=True để in chi tiết lỗi."""
        
        # Kiểm tra Genesis
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.previous_hash != "0" or genesis.hash != genesis.calculate_hash():
            if verbose: print(f"{Colors.FAIL}✘ LỖI: Genesis Block không hợp lệ.{Colors.ENDC}")
            return False

        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            # 1. Kiểm tra Index
            if current.index != previous.index + 1:
                if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Index không liên tục.{Colors.ENDC}")
                return False

            # 2. Kiểm tra Liên kết Hash
            if current.previous_hash != previous.hash:
                if verbose: 
                    print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Liên kết Hash bị gãy.{Colors.ENDC}")
                    print(f"   Mong đợi: {previous.hash}")
                    print(f"   Thực tế : {current.previous_hash}")
                return False

            # 3. Kiểm tra Dữ liệu (Tampering)
            if current.hash != current.calculate_hash():
                if verbose: 
                    print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Dữ liệu bị thay đổi.{Colors.ENDC}")
                    print(f"   Hash lưu: {current.hash}")
                    print(f"   Hash tính:{current.calculate_hash()}")
                return False

            # 4. Kiểm tra PoW
            if not current.hash.startswith("0" * self.difficulty):
                if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Không thỏa mãn độ khó (PoW).{Colors.ENDC}")
                return False
            
            # 5. Kiểm tra Timestamp
            if current.timestamp < previous.timestamp:
                if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Thời gian không hợp lệ (Back-dated).{Colors.ENDC}")
                return False

            # 6. Kiểm tra Kiểu dữ liệu
            if not isinstance(current.data, str):
                 if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Dữ liệu không phải chuỗi ký tự.{Colors.ENDC}")
                 return False

        return True

# ==========================================
# HÀM HỖ TRỢ TEST (HELPER)
# ==========================================
def run_attack_test(test_name, original_chain, attack_logic):
    """
    Hàm helper để chạy các kịch bản tấn công.
    Giúp code main gọn gàng hơn.
    """
    print(f"{Colors.HEADER}====== {test_name} ======{Colors.ENDC}")
    
    # Tạo bản sao sâu để không ảnh hưởng chuỗi gốc
    chain_copy = copy.deepcopy(original_chain)
    
    # Thực hiện logic tấn công
    attack_logic(chain_copy)
    
    # Kiểm tra
    is_valid = chain_copy.is_chain_valid(verbose=True)
    
    if is_valid:
        print(f"Kết quả: {Colors.GREEN}✔ Blockchain HỢP LỆ (Tấn công thất bại){Colors.ENDC}")
    else:
        print(f"Kết quả: {Colors.FAIL}🛡️  Phát hiện tấn công! Blockchain KHÔNG HỢP LỆ{Colors.ENDC}")
    print("-" * 60 + "\n")

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Khởi tạo và thêm dữ liệu
    my_blockchain = Blockchain()
    
    transactions = [
        "Giao dịch 1: A gửi 10 BTC cho B",
        "Giao dịch 2: B gửi 20 BTC cho C",
        "Giao dịch 3: C gửi 30 BTC cho D",
        "Giao dịch 4: C gửi 40 BTC cho B",
        "Giao dịch 5: D gửi 50 BTC cho A"
    ]

    for tx in transactions:
        my_blockchain.mine_block(tx)

    # 2. Kiểm tra lần đầu
    print(f"{Colors.HEADER}====== KIỂM TRA TÍNH TOÀN VẸN BAN ĐẦU ======{Colors.ENDC}")
    if my_blockchain.is_chain_valid():
        print(f"{Colors.GREEN}✔ Blockchain hoạt động bình thường.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✘ Blockchain bị lỗi ngay từ đầu.{Colors.ENDC}")
    print("\n" + "="*60)
    print(f"{Colors.WARNING}          BẮT ĐẦU MÔ PHỎNG TẤN CÔNG          {Colors.ENDC}")
    print("="*60 + "\n")

    # 3. Chạy các kịch bản tấn công

    # Kịch bản 1: Thay đổi Genesis
    run_attack_test("TEST 1: Thay đổi Genesis Block", my_blockchain, 
                    lambda c: setattr(c.chain[0], 'data', "Genesis FAKE"))

    # Kịch bản 2: Thay đổi Index
    run_attack_test("TEST 2: Thay đổi Index Block", my_blockchain, 
                    lambda c: setattr(c.chain[1], 'index', 99))

    # Kịch bản 3: Phá vỡ liên kết Hash
    fake_hash = "0" * 64
    run_attack_test("TEST 3: Cắt đứt liên kết Hash", my_blockchain, 
                    lambda c: setattr(c.chain[2], 'previous_hash', fake_hash))

    # Kịch bản 4: Thay đổi Hash thủ công
    run_attack_test("TEST 4: Giả mạo Hash hiện tại", my_blockchain, 
                    lambda c: setattr(c.chain[1], 'hash', fake_hash))

    # Kịch bản 5: Hack PoW (Hash sai độ khó)
    # Hash này đúng về mặt crypto nhưng sai về độ khó (không có 4 số 0 đầu)
    bad_pow_hash = "1234" + "a" * 60 
    run_attack_test("TEST 5: Hack Proof of Work", my_blockchain, 
                    lambda c: setattr(c.chain[3], 'hash', bad_pow_hash))

    # Kịch bản 6: Thay đổi Timestamp
    run_attack_test("TEST 6: Hack thời gian (Back-dating)", my_blockchain, 
                    lambda c: setattr(c.chain[4], 'timestamp', c.chain[3].timestamp - 1000))

    # Kịch bản 7: Sai kiểu dữ liệu
    run_attack_test("TEST 7: Inject mã độc (Sai kiểu dữ liệu)", my_blockchain, 
                    lambda c: setattr(c.chain[2], 'data', 123456789))