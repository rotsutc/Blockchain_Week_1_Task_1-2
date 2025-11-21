import hashlib
import time
import json
from datetime import datetime
import sys
import copy

# Cấu hình encoding để in tiếng Việt trên Windows console không bị lỗi
sys.stdout.reconfigure(encoding='utf-8')

class Block:
    """
    Đại diện cho một khối (Block) trong Blockchain.
    """
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0  # Number used once cho PoW
        self.hash = self.calculate_hash() # Khởi tạo hash ban đầu

    def calculate_hash(self):
        """
        Tính toán mã hash SHA-256 của block.
        """
        block_dict = {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }
        # sort_keys=True đảm bảo chuỗi JSON luôn nhất quán thứ tự key
        block_string = json.dumps(block_dict, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class Blockchain:
    """
    Đại diện cho toàn bộ chuỗi Blockchain.
    """
    def __init__(self):
        self.chain = []
        self.difficulty = 4 # Độ khó PoW (Số lượng số 0 ở đầu)
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Tạo block đầu tiên (Genesis Block) và thêm vào chuỗi.
        """
        print("Đang tạo Genesis Block...")
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        # Đào Genesis block để nó cũng tuân thủ PoW
        genesis_block.hash = self.mine_block_internal(genesis_block)
        self.chain.append(genesis_block)
        print(f"Genesis Block được tạo. Hash: {genesis_block.hash}\n")

    def get_latest_block(self):
        """
        Lấy block cuối cùng trong chuỗi.
        """
        return self.chain[-1]

    def add_block(self, new_block):
        """
        Phương thức này "đào" block và thêm vào chuỗi.
        """
        print(f"Bắt đầu đào block {new_block.index} với dữ liệu: '{new_block.data}'...")
        new_block.previous_hash = self.get_latest_block().hash
        
        # Bắt đầu quá trình đào (PoW)
        new_block.hash = self.mine_block_internal(new_block)
        
        # Thêm block đã được đào vào chuỗi
        self.chain.append(new_block)
        
        print(f"Block {new_block.index} đã được đào với các thông số:")
        print(f"    + Timestamp: {datetime.fromtimestamp(new_block.timestamp).strftime('%H:%M:%S %d-%m-%Y')}")
        print(f"    + Data: {new_block.data}")
        print(f"    + Previous_hash: {new_block.previous_hash}")
        print(f"    + Nonce: {new_block.nonce}")
        print(f"    + Hash: {new_block.hash}\n")
    
    def mine_block_internal(self, block):
        """
        Tìm một hash hợp lệ (Proof-of-Work).
        """
        difficulty_prefix = "0" * self.difficulty
        
        # Vòng lặp đào: Tính hash lại cho đến khi thỏa mãn độ khó
        while not block.calculate_hash().startswith(difficulty_prefix):
            block.nonce += 1
            
        return block.calculate_hash()

    def mine_block(self, data):
        """
        Tạo một block mới từ dữ liệu người dùng, "đào" nó, và thêm vào chuỗi.
        """
        latest_block = self.get_latest_block()
        new_index = latest_block.index + 1
        new_timestamp = time.time()
        
        new_block = Block(new_index, new_timestamp, data, latest_block.hash)
        self.add_block(new_block)

    def is_chain_valid(self):
        """
        Kiểm tra tính toàn vẹn của toàn bộ blockchain.
        """
        is_valid = True
        
        # Kiểm tra 1: Genesis Block
        genesis = self.chain[0]
        if genesis.index != 0 or genesis.previous_hash != "0" or genesis.hash != genesis.calculate_hash():
            print("LỖI: Genesis Block không hợp lệ.")
            is_valid = False
        
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # Kiểm tra 2: Index liên tục
            if current_block.index != previous_block.index + 1:
                #print(f"Chỉ số hiện tại: {current_block.index}, chỉ số trước: {previous_block.index}")
                print(f"LỖI: Index không liên tục tại Block {current_block.index}.")
                is_valid = False
            
            # Kiểm tra 3: Liên kết Hash (Previous Hash Link)
            if current_block.previous_hash != previous_block.hash:
                print(f"LỖI: Liên kết Hash bị hỏng tại Block {current_block.index}.")
                is_valid = False
                
            # Kiểm tra 4: Tính toàn vẹn Hash (Dữ liệu có bị sửa không?)
            if current_block.hash != current_block.calculate_hash():
                print(f"LỖI: Dữ liệu bị thay đổi tại Block {current_block.index}.")
                print(f"   - Hash lưu trữ: {current_block.hash}")
                print(f"   - Hash thực tế: {current_block.calculate_hash()}")
                is_valid = False

            # Kiểm tra 5: Proof-of-Work (Độ khó)
            if not current_block.hash.startswith("0" * self.difficulty): 
                print(f"LỖI: Proof-of-Work không hợp lệ tại Block {current_block.index}.")
                is_valid = False
                
            # Kiểm tra 6: Tính hợp lệ của Timestamp
            if current_block.timestamp < previous_block.timestamp:
                print(f"LỖI: Timestamp không hợp lệ (nhảy lùi) tại Block {current_block.index}.")
                is_valid = False
            
            # Kiểm tra 7: Kiểu dữ liệu
            if not isinstance(current_block.data, str):
                print(f"LỖI: DATA tại Block {current_block.index} không phải kiểu string.")
                is_valid = False
                
        return is_valid

# --- CHẠY THỬ ---
if __name__ == "__main__":
    
    # 1. Khởi tạo Blockchain
    my_blockchain = Blockchain()
    
    # 2. Thêm các block mới
    my_blockchain.mine_block("Giao dịch 1: A gửi 10 BTC cho B")
    my_blockchain.mine_block("Giao dịch 2: B gửi 20 BTC cho C")
    my_blockchain.mine_block("Giao dịch 3: C gửi 30 BTC cho D")
    my_blockchain.mine_block("Giao dịch 4: C gửi 40 BTC cho B")
    my_blockchain.mine_block("Giao dịch 5: D gửi 50 BTC cho A")
    
    
    # 3. Kiểm tra tính hợp lệ ban đầu
    print("="*80)
    print("Kiểm tra tính hợp lệ của chuỗi...")
    #print(f"Chuỗi có hợp lệ không? -> {my_blockchain.is_chain_valid()}")
    print("✔ Blockchain hợp lệ" if my_blockchain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)
    
    # 4. Thử thay đổi dữ liệu (TẤN CÔNG)
    print("\n" + "="*80)
    print("****** TẤN CÔNG: Thay đổi dữ liệu ******")
    print("="*80)
    
    print("\n" + "====== 1. Thay đổi Genesis Block ======")
    test_chain = copy.deepcopy(my_blockchain)
    test_chain.chain[0].data = "Genesis Block bị thay đổi"
    print("✔ Blockchain hợp lệ" if test_chain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)
    
    print("====== 2. Thay đổi Index ======")
    test_chain = copy.deepcopy(my_blockchain)
    test_chain.chain[1].index = 5
    print("✔ Blockchain hợp lệ" if test_chain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)
    
    print("====== 3. Thay đổi liên kết Hash ======")
    test_chain = copy.deepcopy(my_blockchain)
    test_chain.chain[1].previous_hash = "00001c87f0c96ee59bdbfe321b03d0671b9a191e394b78c0fd544b9bf36e734b"
    print("✔ Blockchain hợp lệ" if test_chain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)
    
    print("====== 4. Thay đổi Hash ======")
    test_chain = copy.deepcopy(my_blockchain)
    test_chain.chain[1].hash = "00001c87f0c96ee59bdbfe321b03d0671b9a191e394b78c0fd544b9bf36e734b"
    print("✔ Blockchain hợp lệ" if test_chain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)
    
    print("====== 5. Kiểm tra Proof of Work ======")
    test_chain = copy.deepcopy(my_blockchain)
    test_chain.chain[3].hash = "00011c87f0c96ee59bdbfe321b03d0671b9a191e394b78c0fd544b9bf36e734b"
    print("✔ Blockchain hợp lệ" if test_chain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)
    
    print("====== 6. Thay đổi Timestamp ======")
    test_chain = copy.deepcopy(my_blockchain)
    test_chain.chain[4].timestamp = test_chain.chain[3].timestamp - 100000
    print("✔ Blockchain hợp lệ" if test_chain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)
    
    print("====== 7. Thay đổi Data ======")
    test_chain = copy.deepcopy(my_blockchain)
    test_chain.chain[2].data = 123456  # Không phải kiểu string
    print("✔ Blockchain hợp lệ" if test_chain.is_chain_valid() 
          else "✘ Blockchain KHÔNG hợp lệ")
    print("="*80)