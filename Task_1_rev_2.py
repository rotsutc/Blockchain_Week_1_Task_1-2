import hashlib
import time
import json
import copy
import sys
from datetime import datetime

# --- CẤU HÌNH MÀU SẮC ---
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

sys.stdout.reconfigure(encoding='utf-8')

# ==========================================
# HÀM HỖ TRỢ: MERKLE TREE
# ==========================================
def calculate_merkle_root(transactions):
    """
    Tính toán Merkle Root cho một danh sách các giao dịch.
    """
    # 1. Nếu không có giao dịch, trả về hash của chuỗi rỗng hoặc giá trị mặc định
    if not transactions:
        return hashlib.sha256(b'').hexdigest()

    # 2. Tạo danh sách Hash cho tầng lá (Leaf Nodes)
    temp_tree = []
    for tx in transactions:
        # Đảm bảo tx là string trước khi encode
        tx_string = json.dumps(tx, sort_keys=True) if not isinstance(tx, str) else tx
        temp_tree.append(hashlib.sha256(tx_string.encode()).hexdigest())

    # 3. Xây dựng cây từ dưới lên (Bottom-Up)
    while len(temp_tree) > 1:
        new_level = []
        # Duyệt qua từng cặp (step = 2)
        for i in range(0, len(temp_tree), 2):
            left_hash = temp_tree[i]
            
            # Nếu còn phần tử bên phải thì lấy, nếu không (lẻ) thì nhân đôi phần tử trái
            if i + 1 < len(temp_tree):
                right_hash = temp_tree[i+1]
            else:
                right_hash = left_hash # Nhân đôi nút lẻ
            
            # Hash(Left + Right)
            combined = left_hash + right_hash
            new_hash = hashlib.sha256(combined.encode()).hexdigest()
            new_level.append(new_hash)
        
        temp_tree = new_level

    # Phần tử cuối cùng còn lại là Merkle Root
    return temp_tree[0]

# ==========================================
# CLASS BLOCK
# ==========================================
class Block:
    def __init__(self, index, timestamp, transactions, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = transactions  # Bây giờ là một LIST các giao dịch
        self.previous_hash = previous_hash
        self.nonce = 0
        
        # Tính Merkle Root từ danh sách transactions
        self.merkle_root = calculate_merkle_root(self.data)
        
        # Hash của Block bây giờ phụ thuộc vào Merkle Root (không phải data thô)
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """Tính toán Block Header Hash"""
        block_header = {
            "index": self.index,
            "timestamp": self.timestamp,
            "merkle_root": self.merkle_root, # Dùng Merkle Root thay vì data
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        block_string = json.dumps(block_header, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def update_merkle_root(self):
        """Hàm tiện ích để cập nhật lại Merkle Root khi data bị sửa"""
        self.merkle_root = calculate_merkle_root(self.data)

# ==========================================
# CLASS BLOCKCHAIN
# ==========================================
class Blockchain:
    def __init__(self):
        self.chain = []
        self.difficulty = 4
        self.create_genesis_block()

    def create_genesis_block(self):
        print(f"{Colors.HEADER}=== KHỞI TẠO BLOCKCHAIN (BINARY MERKLE TREE) ==={Colors.ENDC}")
        # Genesis block chứa một danh sách giao dịch mẫu
        genesis_tx = ["Genesis Transaction"]
        genesis_block = Block(0, time.time(), genesis_tx, "0")
        genesis_block.hash = self.mine_block_internal(genesis_block)
        self.chain.append(genesis_block)
        print(f"{Colors.GREEN}✔ Genesis Block Created.{Colors.ENDC}")
        print(f"  └── Merkle Root: {genesis_block.merkle_root}\n")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
        print(f"⛏️  Đang đào Block #{new_block.index} ({len(new_block.data)} giao dịch)...", end="\r")
        
        new_block.previous_hash = self.get_latest_block().hash
        new_block.hash = self.mine_block_internal(new_block)
        
        self.chain.append(new_block)
        print(f"{Colors.GREEN}✔ Block #{new_block.index} đã đào xong.                           {Colors.ENDC}")
        print(f"  ├── Merkle Root: {new_block.merkle_root}")
        print(f"  └── Block Hash : {new_block.hash}\n")

    def mine_block_internal(self, block):
        target = "0" * self.difficulty
        while not block.calculate_hash().startswith(target):
            block.nonce += 1
        return block.calculate_hash()

    def mine_block(self, transactions_list):
        """API nhận vào một LIST các giao dịch"""
        latest_block = self.get_latest_block()
        # Đảm bảo đầu vào là list
        if not isinstance(transactions_list, list):
            transactions_list = [transactions_list]
            
        new_block = Block(latest_block.index + 1, time.time(), transactions_list, latest_block.hash)
        self.add_block(new_block)

    def is_chain_valid(self, verbose=True):
        """Kiểm tra tính toàn vẹn (Bao gồm cả kiểm tra Merkle Root)"""
        
        # Kiểm tra Genesis
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.previous_hash != "0":
             if verbose: print(f"{Colors.FAIL}✘ LỖI: Genesis Block sai lệch.{Colors.ENDC}")
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
                if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Liên kết Hash bị gãy.{Colors.ENDC}")
                return False

            # 3. KIỂM TRA MERKLE ROOT (QUAN TRỌNG)
            # Tính lại Merkle Root từ dữ liệu thô hiện tại
            recalculated_merkle_root = calculate_merkle_root(current.data)
            if current.merkle_root != recalculated_merkle_root:
                if verbose:
                    print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Dữ liệu giao dịch bị sửa đổi!{Colors.ENDC}")
                    print(f"   Merkle Root lưu : {current.merkle_root}")
                    print(f"   Merkle Root tính: {recalculated_merkle_root}")
                return False

            # 4. Kiểm tra Block Hash (Header Integrity)
            # Hash của block phụ thuộc vào Merkle Root. Nếu Merkle Root sai -> Hash block sai.
            if current.hash != current.calculate_hash():
                if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Block Header Hash không khớp.{Colors.ENDC}")
                return False

            # 5. Kiểm tra PoW
            if not current.hash.startswith("0" * self.difficulty):
                if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: PoW không hợp lệ.{Colors.ENDC}")
                return False
            
            # 6. Kiểm tra Timestamp
            if current.timestamp < previous.timestamp:
                if verbose: print(f"{Colors.FAIL}✘ LỖI Block #{current.index}: Lỗi thời gian.{Colors.ENDC}")
                return False

        return True

# ==========================================
# HÀM TEST TẤN CÔNG
# ==========================================
def run_attack_test(test_name, original_chain, attack_logic):
    print(f"{Colors.HEADER}====== {test_name} ======{Colors.ENDC}")
    chain_copy = copy.deepcopy(original_chain)
    attack_logic(chain_copy)
    
    # In kết quả
    if chain_copy.is_chain_valid(verbose=True):
        print(f"Kết quả: {Colors.GREEN}✔ Blockchain HỢP LỆ{Colors.ENDC}")
    else:
        print(f"Kết quả: {Colors.FAIL}🛡️  Phát hiện tấn công! Blockchain KHÔNG HỢP LỆ{Colors.ENDC}")
    print("-" * 60 + "\n")

# ==========================================
# CHẠY CHƯƠNG TRÌNH
# ==========================================
if __name__ == "__main__":
    my_blockchain = Blockchain()
    
    # Tạo các khối với NHIỀU giao dịch (để minh họa Merkle Tree)
    block1_txs = ["A gửi 10 BTC cho B", "B gửi 5 BTC cho C", "Phí giao dịch: 1 BTC"]
    my_blockchain.mine_block(block1_txs) # Block 1

    block2_txs = ["C gửi 50 BTC cho D", "D gửi 1 BTC cho A"]
    my_blockchain.mine_block(block2_txs) # Block 2
    
    block3_txs = ["A mua Pizza giá 10000 BTC", "Tạp chí Blockchain ra mắt", "Xác nhận 3", "Xác nhận 4"]
    my_blockchain.mine_block(block3_txs) # Block 3

    # Kiểm tra ban đầu
    print(f"{Colors.HEADER}====== KIỂM TRA BAN ĐẦU ======{Colors.ENDC}")
    if my_blockchain.is_chain_valid():
        print(f"{Colors.GREEN}✔ Blockchain hoạt động tốt với Merkle Tree.{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}✘ Có lỗi xảy ra.{Colors.ENDC}")
    print("\n" + "="*60)
    print(f"{Colors.WARNING}          BẮT ĐẦU MÔ PHỎNG TẤN CÔNG          {Colors.ENDC}")
    print("="*60 + "\n")

    # --- Kịch bản 1: Sửa nội dung 1 giao dịch trong danh sách ---
    # Hacker sửa "A gửi 10 BTC" thành "A gửi 1000 BTC" trong Block 1
    def attack_modify_tx(chain):
        # Sửa giao dịch đầu tiên của Block 1
        chain.chain[1].data[0] = "A gửi 1000 BTC cho Hacker" 
        # Lưu ý: Hacker KHÔNG cập nhật lại Merkle Root (vì hắn không thể ký lại Header mà không đào lại)
    
    run_attack_test("TEST 1: Sửa nội dung giao dịch (Merkle Root Mismatch)", 
                    my_blockchain, attack_modify_tx)

    # --- Kịch bản 2: Sửa giao dịch VÀ Cố tình tính lại Merkle Root ---
    # Hacker sửa giao dịch và tính lại Merkle Root để khớp với dữ liệu mới
    # NHƯNG hắn không đào lại (Hash Block sẽ sai)
    def attack_smart_modify(chain):
        chain.chain[2].data[0] = "Giao dịch giả mạo"
        # Hacker tính lại Merkle Root
        chain.chain[2].update_merkle_root() 
        # Nhưng Hash của Block (Header) lúc này sẽ thay đổi, không khớp với PoW cũ
    
    run_attack_test("TEST 2: Sửa giao dịch & Merkle Root (Hash Mismatch)", 
                    my_blockchain, attack_smart_modify)

    # --- Kịch bản 3: Cắt đứt liên kết Hash ---
    def attack_break_link(chain):
        chain.chain[2].previous_hash = "000000000fakehash"
        
    run_attack_test("TEST 3: Cắt đứt liên kết Hash", my_blockchain, attack_break_link)