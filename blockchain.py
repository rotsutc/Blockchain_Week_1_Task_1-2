"""
Blockchain Implementation with Proof-of-Work
=============================================
Một implementation đầy đủ của blockchain với các tính năng:
- Block class với tất cả attributes cần thiết
- Blockchain class để quản lý chain
- Proof-of-Work (PoW) mining algorithm
- Chain validation để kiểm tra tính toàn vẹn
- Demo application với nhiều tính năng

Các khái niệm chính:
--------------------
1. BLOCK: Đơn vị cơ bản của blockchain, chứa:
   - Data (transactions, messages, etc.)
   - Hash của chính nó
   - Hash của block trước đó (previous_hash)
   - Nonce (số dùng cho Proof-of-Work)
   - Timestamp và index

2. BLOCKCHAIN: Chuỗi các blocks liên kết với nhau:
   - Mỗi block chứa hash của block trước
   - Thay đổi 1 block → thay đổi tất cả blocks sau nó
   - Rất khó để giả mạo do Proof-of-Work

3. PROOF-OF-WORK (PoW): Cơ chế bảo mật:
   - Miner phải tìm nonce sao cho hash thỏa mãn điều kiện
   - Ví dụ: Hash phải bắt đầu với "0000" (difficulty = 4)
   - Tốn computational power → khó để attack

4. HASH: Cryptographic hash function:
   - Input khác nhau → Output hoàn toàn khác nhau
   - One-way: Không thể reverse
   - Deterministic: Cùng input → Cùng output
   - Avalanche effect: Thay đổi 1 bit → Thay đổi ~50% output
"""

import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Literal

# Định nghĩa các thuật toán hash được hỗ trợ
# Type hint để IDE có thể autocomplete và type check
HashAlgorithm = Literal["sha256", "sha512", "sha3-256", "sha3-512", "blake2b"]


class Block:
    """
    Block class đại diện cho một block trong blockchain
    
    Attributes:
        index (int): Vị trí của block trong chain
        timestamp (float): Thời gian tạo block (Unix timestamp)
        data (Any): Dữ liệu được lưu trong block
        previous_hash (str): Hash của block trước đó
        nonce (int): Số dùng cho Proof-of-Work
        hash (str): Hash của block hiện tại
        hash_algorithm (str): Thuật toán hash được sử dụng
    """
    
    def __init__(self, index: int, timestamp: float, data: Any, previous_hash: str, 
                 nonce: int = 0, hash_algorithm: HashAlgorithm = "sha256"):
        """
        Khởi tạo một Block mới
        
        Args:
            index: Vị trí của block trong chain
            timestamp: Thời gian tạo block
            data: Dữ liệu cần lưu trữ
            previous_hash: Hash của block trước
            nonce: Giá trị nonce cho PoW (mặc định 0)
            hash_algorithm: Thuật toán hash (sha256, sha512, sha3-256, sha3-512, blake2b)
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash_algorithm = hash_algorithm
        self.hash = self.calculate_hash()
    
    def calculate_hash(self) -> str:
        """
        Tính toán hash của block sử dụng thuật toán được chọn
        
        Hash được tính dựa trên tất cả các attributes của block:
        index, timestamp, data, previous_hash, và nonce
        
        *** ĐÂY LÀ TRÁI TIM CỦA BLOCKCHAIN ***
        - Hash là "fingerprint" duy nhất của block
        - Thay đổi bất kỳ thông tin nào → Hash thay đổi hoàn toàn
        - Hash phụ thuộc vào previous_hash → Tạo chuỗi liên kết
        - Nonce được thay đổi trong mining để tìm hash hợp lệ
        
        Hỗ trợ các thuật toán:
        - SHA-256: Được Bitcoin sử dụng, 256-bit output
        - SHA-512: Phiên bản mạnh hơn của SHA-2, 512-bit output
        - SHA3-256: Thuật toán Keccak, được Ethereum sử dụng
        - SHA3-512: Phiên bản mạnh hơn của SHA-3
        - BLAKE2b: Nhanh hơn MD5, an toàn như SHA-3
        
        Returns:
            str: Hash của block dưới dạng hex string (hexadecimal)
        """
        # Kết hợp tất cả thông tin của block thành một string
        # sort_keys=True để đảm bảo order nhất quán
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        
        # Tính hash theo thuật toán được chọn
        # .encode() chuyển string thành bytes
        # .hexdigest() chuyển hash thành hex string
        if self.hash_algorithm == "sha256":
            return hashlib.sha256(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "sha512":
            return hashlib.sha512(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "sha3-256":
            return hashlib.sha3_256(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "sha3-512":
            return hashlib.sha3_512(block_string.encode()).hexdigest()
        elif self.hash_algorithm == "blake2b":
            return hashlib.blake2b(block_string.encode()).hexdigest()
        else:
            # Fallback to SHA-256 nếu thuật toán không được hỗ trợ
            return hashlib.sha256(block_string.encode()).hexdigest()
    
    def __str__(self) -> str:
        """String representation của Block"""
        return f"Block #{self.index} [Hash: {self.hash[:16]}...]"
    
    def to_dict(self) -> Dict:
        """
        Chuyển block thành dictionary để dễ dàng hiển thị
        
        Returns:
            Dict: Dictionary chứa thông tin block
        """
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "datetime": datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S'),
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash,
            "hash_algorithm": self.hash_algorithm
        }


class Blockchain:
    """
    Blockchain class quản lý toàn bộ chain
    
    Attributes:
        chain (List[Block]): Danh sách các blocks trong blockchain
        difficulty (int): Độ khó cho Proof-of-Work (số lượng số 0 đầu tiên)
        hash_algorithm (str): Thuật toán hash sử dụng cho toàn bộ chain
    """
    
    def __init__(self, difficulty: int = 4, hash_algorithm: HashAlgorithm = "sha256"):
        """
        Khởi tạo blockchain mới với genesis block
        
        Args:
            difficulty: Độ khó cho PoW (số lượng số 0 đầu hash, mặc định 4)
            hash_algorithm: Thuật toán hash (sha256, sha512, sha3-256, sha3-512, blake2b)
        """
        self.chain: List[Block] = []
        self.difficulty = difficulty
        self.hash_algorithm = hash_algorithm
        # Tạo genesis block (block đầu tiên)
        self.create_genesis_block()
    
    def create_genesis_block(self) -> Block:
        """
        Tạo genesis block - block đầu tiên trong blockchain
        
        Genesis block có:
        - Index = 0
        - Previous hash = "0"
        - Data đặc biệt đánh dấu là genesis block
        
        Returns:
            Block: Genesis block đã được tạo và thêm vào chain
        """
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            data="Genesis Block - The beginning of the blockchain",
            previous_hash="0",
            hash_algorithm=self.hash_algorithm
        )
        self.chain.append(genesis_block)
        print(f"✓ Genesis block created: {genesis_block.hash[:16]}...")
        print(f"  Hash Algorithm: {self.hash_algorithm.upper()}")
        return genesis_block
    
    def get_latest_block(self) -> Block:
        """
        Lấy block cuối cùng trong chain
        
        Returns:
            Block: Block cuối cùng
        """
        return self.chain[-1]
    
    def add_block(self, data: Any) -> Block:
        """
        Thêm block mới vào blockchain (với mining)
        
        Process:
        1. Tạo block mới với data
        2. Mine block (Proof-of-Work)
        3. Thêm vào chain
        
        Args:
            data: Dữ liệu cần lưu trong block mới
            
        Returns:
            Block: Block mới đã được mine và thêm vào chain
        """
        previous_block = self.get_latest_block()
        new_block = Block(
            index=len(self.chain),
            timestamp=time.time(),
            data=data,
            previous_hash=previous_block.hash,
            hash_algorithm=self.hash_algorithm
        )
        
        # Mine block với Proof-of-Work
        self.mine_block(new_block)
        
        # Thêm vào chain
        self.chain.append(new_block)
        return new_block
    
    def mine_block(self, block: Block) -> None:
        """
        Mine một block sử dụng Proof-of-Work algorithm
        
        *** PROOF-OF-WORK (PoW) - TRÁI TIM CỦA BLOCKCHAIN ***
        
        Cách hoạt động:
        ----------------
        1. Tạo target string: "0" * difficulty
           - Ví dụ: difficulty=4 → target="0000"
        
        2. Loop vô tận:
           - Tăng nonce lên 1
           - Tính hash của block với nonce mới
           - Kiểm tra hash có bắt đầu với target không?
           - Nếu có → Tìm thấy! (block đã mined)
           - Nếu không → Tiếp tục loop
        
        3. Khi tìm thấy:
           - Block có hash hợp lệ
           - Đã chứng minh đã dùng computational power
           - Block sẵn sàng được thêm vào chain
        
        Tại sao cần PoW?
        ----------------
        - Bảo mật: Attacker phải redo tất cả PoW của chain → Rất khó
        - Decentralization: Ai cũng có thể mine, không cần trust
        - Incentive: Miner được thưởng khi mine thành công
        - Consensus: Longest chain = valid chain
        
        Độ khó (Difficulty):
        --------------------
        - Difficulty = 1: Hash bắt đầu với "0" (~16 tries)
        - Difficulty = 2: Hash bắt đầu với "00" (~256 tries)
        - Difficulty = 3: Hash bắt đầu với "000" (~4,096 tries)
        - Difficulty = 4: Hash bắt đầu với "0000" (~65,536 tries)
        - Mỗi tăng 1 → Tăng ~16x thời gian (vì hex = base 16)
        
        Bitcoin:
        --------
        - Difficulty tự động điều chỉnh mỗi 2016 blocks
        - Target: 1 block mỗi 10 phút
        - Hiện tại: ~19-20 leading zeros (cực kỳ khó!)
        
        Args:
            block: Block cần mine
        """
        # Tạo target string: chuỗi các số 0
        # Hash phải bắt đầu với string này
        target = "0" * self.difficulty
        start_time = time.time()
        
        print(f"\n⛏️  Mining block #{block.index}...")
        print(f"   Target: {target}...")
        print(f"   Difficulty: {self.difficulty} leading zeros required")
        
        # Proof-of-Work loop
        # Tìm nonce sao cho hash thỏa mãn điều kiện
        while not block.hash.startswith(target):
            block.nonce += 1  # Tăng nonce
            block.hash = block.calculate_hash()  # Tính hash mới
            
            # Hiển thị tiến trình mỗi 100,000 lần thử
            # Để user biết mining đang diễn ra
            if block.nonce % 100000 == 0:
                print(f"   Trying nonce: {block.nonce:,} - Hash: {block.hash[:16]}...")
        
        # Đã tìm thấy hash hợp lệ!
        elapsed_time = time.time() - start_time
        print(f"✓ Block mined successfully!")
        print(f"   Nonce found: {block.nonce:,}")
        print(f"   Hash: {block.hash}")
        print(f"   Mining time: {elapsed_time:.2f} seconds")
        
        # Tính hash rate (tránh chia cho 0 khi mining quá nhanh)
        if elapsed_time > 0:
            print(f"   Hash rate: {block.nonce/elapsed_time:,.0f} hashes/second")
        else:
            print(f"   Hash rate: Very fast (< 0.01s)")
    
    def is_chain_valid(self) -> bool:
        """
        Kiểm tra tính hợp lệ của toàn bộ blockchain
        
        *** VALIDATION - BẢO MẬT BLOCKCHAIN ***
        
        Đây là cơ chế quan trọng nhất để đảm bảo:
        - Blockchain không bị giả mạo (tampered)
        - Tất cả blocks đều hợp lệ
        - Chain integrity được duy trì
        
        3 Validation Checks:
        --------------------
        
        CHECK 1: Hash Validity
        - Recalculate hash của mỗi block
        - So sánh với hash đã lưu
        - Nếu khác → Block đã bị thay đổi!
        - Ví dụ: Ai đó thay đổi data nhưng không update hash
        
        CHECK 2: Chain Linkage
        - Kiểm tra previous_hash của block hiện tại
        - Phải match với hash của block trước
        - Nếu không match → Chain bị break!
        - Ví dụ: Ai đó insert hoặc remove block
        
        CHECK 3: Proof-of-Work
        - Kiểm tra hash có satisfy difficulty requirement không
        - Hash phải bắt đầu với số lượng zeros đúng
        - Nếu không → Block chưa được mine properly!
        - Ví dụ: Ai đó tạo fake block không qua PoW
        
        Tại sao blockchain an toàn?
        ---------------------------
        1. Thay đổi 1 block:
           - Hash của block đó thay đổi
           - Previous_hash của block tiếp theo không match
           - Validation FAIL!
        
        2. Để giả mạo thành công, attacker phải:
           - Thay đổi block
           - Recalculate hash (tốn thời gian do PoW)
           - Thay đổi ALL blocks sau nó (rất khó!)
           - Làm nhanh hơn network (gần như không thể!)
        
        3. Longest chain rule:
           - Honest chain grow nhanh hơn (nhiều miners)
           - Attacker's chain ngắn hơn → Bị reject
        
        Returns:
            bool: True nếu chain hợp lệ, False nếu phát hiện vấn đề
        """
        print("\n🔍 Validating blockchain...")
        print(f"   Checking {len(self.chain)} blocks...")
        
        # Bỏ qua genesis block (block 0), bắt đầu từ block 1
        # Genesis block không có previous block để validate
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            
            # CHECK 1: Hash của block có đúng không?
            # Recalculate hash và compare
            recalculated_hash = current_block.calculate_hash()
            if current_block.hash != recalculated_hash:
                print(f"\n✗ Block #{i}: Hash không hợp lệ!")
                print(f"   Expected (recalculated): {recalculated_hash}")
                print(f"   Got (stored): {current_block.hash}")
                print(f"   → Block data might have been tampered!")
                return False
            
            # CHECK 2: Previous hash có khớp không?
            # Link giữa các blocks phải đúng
            if current_block.previous_hash != previous_block.hash:
                print(f"\n✗ Block #{i}: Previous hash không khớp!")
                print(f"   Expected: {previous_block.hash}")
                print(f"   Got: {current_block.previous_hash}")
                print(f"   → Chain linkage broken!")
                return False
            
            # CHECK 3: Hash có thỏa mãn difficulty không?
            # Đảm bảo block đã được mine properly
            target = "0" * self.difficulty
            if not current_block.hash.startswith(target):
                print(f"\n✗ Block #{i}: Hash không thỏa mãn difficulty!")
                print(f"   Required: {target}... ({self.difficulty} leading zeros)")
                print(f"   Got: {current_block.hash[:len(target)]}...")
                print(f"   → Block was not properly mined!")
                return False
            
            # Block này hợp lệ
            print(f"   ✓ Block #{i} is valid")
        
        # Tất cả blocks đều hợp lệ!
        print("\n✓ Blockchain is completely valid!")
        print(f"   All {len(self.chain)} blocks passed validation")
        print(f"   Chain integrity: INTACT")
        return True
    
    def get_chain_info(self) -> Dict:
        """
        Lấy thông tin tổng quan về blockchain
        
        Returns:
            Dict: Thông tin blockchain
        """
        return {
            "length": len(self.chain),
            "difficulty": self.difficulty,
            "hash_algorithm": self.hash_algorithm,
            "latest_block_hash": self.get_latest_block().hash,
            "genesis_block_hash": self.chain[0].hash
        }
    
    def print_chain(self) -> None:
        """In ra toàn bộ blockchain với format đẹp"""
        print("\n" + "="*70)
        print("BLOCKCHAIN OVERVIEW")
        print("="*70)
        
        info = self.get_chain_info()
        print(f"Chain Length: {info['length']} blocks")
        print(f"Difficulty: {info['difficulty']}")
        print(f"Hash Algorithm: {info['hash_algorithm'].upper()}")
        print(f"Genesis Block: {info['genesis_block_hash'][:16]}...")
        print(f"Latest Block: {info['latest_block_hash'][:16]}...")
        print("="*70)
        
        for block in self.chain:
            print(f"\n--- Block #{block.index} ---")
            print(f"Timestamp: {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Data: {block.data}")
            print(f"Previous Hash: {block.previous_hash[:16]}...")
            print(f"Nonce: {block.nonce:,}")
            print(f"Hash: {block.hash}")
        
        print("\n" + "="*70)


def demonstrate_tampering(blockchain: Blockchain) -> None:
    """
    Demo về việc blockchain chống lại tampering (giả mạo dữ liệu)
    
    *** DEMO: TẠI SAO BLOCKCHAIN AN TOÀN? ***
    
    Scenario này minh họa:
    -----------------------
    1. Setup:
       - Có một blockchain với ít nhất 3 blocks
       - Tất cả blocks đều valid
    
    2. Attack:
       - Attacker thay đổi data của Block #1 (giữa chain)
       - KHÔNG recalculate hash (vì không biết nonce)
       - Hy vọng không ai phát hiện
    
    3. Detection:
       - Chạy validation
       - Blockchain phát hiện ngay lập tức!
       - Lý do: Hash không match với data mới
    
    4. Result:
       - Chain bị mark là INVALID
       - Attacker FAIL!
    
    Bài học:
    --------
    - Không thể thay đổi data mà không bị phát hiện
    - Hash function là "tamper-evident seal"
    - PoW làm việc recalculate hash rất tốn kém
    - Chain càng dài → càng khó để attack
    
    Real-world application:
    -----------------------
    - Medical records: Không thể alter patient data
    - Supply chain: Không thể fake product origin
    - Voting systems: Không thể change votes
    - Financial records: Không thể modify transactions
    
    Args:
        blockchain: Blockchain để demo
    """
    print("\n" + "="*70)
    print("DEMO: TAMPERING DETECTION")
    print("="*70)
    
    # Cần ít nhất 3 blocks cho demo có ý nghĩa
    if len(blockchain.chain) < 3:
        print("⚠️  Need at least 3 blocks for this demo")
        print("   Please add more blocks first!")
        return
    
    # Lưu dữ liệu gốc để có thể show comparison
    original_data = blockchain.chain[1].data
    original_hash = blockchain.chain[1].hash
    
    print(f"\n📝 Original Block #1 data: {original_data}")
    print(f"   Original hash: {original_hash[:16]}...")
    
    # STEP 1: Validation trước khi thay đổi
    print("\n--- STEP 1: Validating BEFORE tampering ---")
    is_valid_before = blockchain.is_chain_valid()
    print(f"   Result: {'✓ VALID' if is_valid_before else '✗ INVALID'}")
    
    # STEP 2: Giả mạo dữ liệu (ATTACK!)
    print("\n--- STEP 2: TAMPERING ATTACK ---")
    print("⚠️  Attacker is changing data in Block #1...")
    blockchain.chain[1].data = "HACKED DATA - This has been modified!"
    print(f"   New data: {blockchain.chain[1].data}")
    print(f"   Hash remains: {blockchain.chain[1].hash[:16]}... (unchanged)")
    print("   ↑ Attacker didn't recalculate hash (too expensive!)")
    
    # STEP 3: Validation sau khi thay đổi (DETECTION!)
    print("\n--- STEP 3: Validating AFTER tampering ---")
    is_valid_after = blockchain.is_chain_valid()
    print(f"   Result: {'✓ VALID' if is_valid_after else '✗ INVALID'}")
    
    # Khôi phục dữ liệu gốc (clean up)
    blockchain.chain[1].data = original_data
    blockchain.chain[1].hash = original_hash
    
    # Summary
    print("\n" + "="*70)
    print("📊 DEMO SUMMARY")
    print("="*70)
    print(f"   Valid before tampering: {is_valid_before}")
    print(f"   Valid after tampering:  {is_valid_after}")
    print(f"   Tampering detected:     {not is_valid_after}")
    print("\n💡 CONCLUSION:")
    print("   ✓ Blockchain successfully detected the tampering!")
    print("   ✓ Data integrity is guaranteed by hash linkage!")
    print("   ✓ This is why blockchain is called 'immutable'!")
    print("="*70)


def interactive_demo():
    """
    Interactive demo application với nhiều tính năng
    
    Cho phép user:
    - Chọn hash algorithm
    - Chọn difficulty level
    - Thêm blocks với data tùy chỉnh
    - Validate chain
    - Xem chain
    - Demo tampering detection
    """
    print("="*70)
    print("BLOCKCHAIN DEMO APPLICATION")
    print("="*70)
    
    # Chọn hash algorithm
    print("\nChọn thuật toán Hash:")
    print("1. SHA-256 (Bitcoin) - 256 bit, nhanh")
    print("2. SHA-512 - 512 bit, an toàn hơn")
    print("3. SHA3-256 (Keccak/Ethereum) - 256 bit, hiện đại")
    print("4. SHA3-512 - 512 bit, hiện đại nhất")
    print("5. BLAKE2b - Nhanh nhất, rất an toàn")
    
    hash_algorithms = {
        "1": "sha256",
        "2": "sha512", 
        "3": "sha3-256",
        "4": "sha3-512",
        "5": "blake2b"
    }
    
    while True:
        try:
            choice = input("\nNhập lựa chọn (1-5): ").strip()
            if choice in hash_algorithms:
                hash_algorithm = hash_algorithms[choice]
                break
            print("Lựa chọn không hợp lệ!")
        except:
            print("Lựa chọn không hợp lệ!")
    
    # Chọn difficulty
    print("\nChọn độ khó (difficulty) cho Proof-of-Work:")
    print("1. Easy (difficulty = 2) - Nhanh, cho testing")
    print("2. Medium (difficulty = 3) - Cân bằng")
    print("3. Hard (difficulty = 4) - Mất thời gian hơn, an toàn hơn")
    print("4. Very Hard (difficulty = 5) - Rất chậm, production-ready")
    
    while True:
        try:
            choice = input("\nNhập lựa chọn (1-4): ").strip()
            difficulty_map = {"1": 2, "2": 3, "3": 4, "4": 5}
            if choice in difficulty_map:
                difficulty = difficulty_map[choice]
                break
            print("Lựa chọn không hợp lệ!")
        except:
            print("Lựa chọn không hợp lệ!")
    
    # Khởi tạo blockchain
    print(f"\n🔗 Initializing blockchain...")
    print(f"   Hash Algorithm: {hash_algorithm.upper()}")
    print(f"   Difficulty: {difficulty}")
    blockchain = Blockchain(difficulty=difficulty, hash_algorithm=hash_algorithm)
    
    # Menu chính
    while True:
        print("\n" + "="*70)
        print("MENU")
        print("="*70)
        print("1. Thêm block mới vào blockchain")
        print("2. Hiển thị toàn bộ blockchain")
        print("3. Validate blockchain")
        print("4. Xem thông tin blockchain")
        print("5. Demo tampering detection")
        print("6. Thoát")
        
        choice = input("\nNhập lựa chọn (1-6): ").strip()
        
        if choice == "1":
            # Thêm block mới
            data = input("\nNhập dữ liệu cho block mới: ").strip()
            if data:
                blockchain.add_block(data)
                print(f"\n✓ Block đã được thêm vào blockchain!")
            else:
                print("Dữ liệu không được để trống!")
        
        elif choice == "2":
            # Hiển thị blockchain
            blockchain.print_chain()
        
        elif choice == "3":
            # Validate blockchain
            is_valid = blockchain.is_chain_valid()
            if is_valid:
                print("\n✓ Blockchain is VALID! ✓")
            else:
                print("\n✗ Blockchain is INVALID! ✗")
        
        elif choice == "4":
            # Thông tin blockchain
            info = blockchain.get_chain_info()
            print("\n" + "="*70)
            print("BLOCKCHAIN INFO")
            print("="*70)
            print(f"Total Blocks: {info['length']}")
            print(f"Difficulty: {info['difficulty']}")
            print(f"Genesis Block Hash: {info['genesis_block_hash']}")
            print(f"Latest Block Hash: {info['latest_block_hash']}")
            print("="*70)
        
        elif choice == "5":
            # Demo tampering
            if len(blockchain.chain) < 3:
                print("\n⚠️  Cần ít nhất 3 blocks để demo tampering.")
                print("   Hãy thêm thêm blocks trước!")
            else:
                demonstrate_tampering(blockchain)
        
        elif choice == "6":
            # Thoát
            print("\n👋 Cảm ơn bạn đã sử dụng Blockchain Demo!")
            print("="*70)
            break
        
        else:
            print("\n⚠️  Lựa chọn không hợp lệ!")


def quick_demo():
    """
    Quick demo tự động để test nhanh tất cả tính năng
    
    Demo sẽ:
    1. Tạo blockchain
    2. Thêm nhiều blocks
    3. Validate chain
    4. Demo tampering detection
    """
    print("="*70)
    print("QUICK AUTOMATIC DEMO")
    print("="*70)
    
    # Tạo blockchain với difficulty = 3 cho demo nhanh
    print("\n🔗 Creating blockchain với difficulty = 3...")
    blockchain = Blockchain(difficulty=3)
    
    # Thêm một số blocks
    print("\n📦 Adding blocks...")
    blockchain.add_block("Transaction 1: Alice sends 10 BTC to Bob")
    blockchain.add_block("Transaction 2: Bob sends 5 BTC to Charlie")
    blockchain.add_block("Transaction 3: Charlie sends 2 BTC to David")
    
    # Hiển thị blockchain
    blockchain.print_chain()
    
    # Validate
    blockchain.is_chain_valid()
    
    # Demo tampering
    demonstrate_tampering(blockchain)
    
    print("\n✓ Quick demo completed!")


if __name__ == "__main__":
    """
    Main entry point của chương trình
    
    Cho phép chọn giữa:
    1. Interactive demo - Tương tác đầy đủ
    2. Quick demo - Demo tự động nhanh
    """
    print("\n🔐 BLOCKCHAIN WITH PROOF-OF-WORK 🔐")
    print("\nChọn chế độ:")
    print("1. Interactive Demo (Recommended - Tương tác đầy đủ)")
    print("2. Quick Automatic Demo (Nhanh - Tự động)")
    
    while True:
        try:
            choice = input("\nNhập lựa chọn (1-2): ").strip()
            if choice == "1":
                interactive_demo()
                break
            elif choice == "2":
                quick_demo()
                break
            else:
                print("Lựa chọn không hợp lệ!")
        except KeyboardInterrupt:
            print("\n\n👋 Thoát chương trình!")
            break
        except Exception as e:
            print(f"\n⚠️  Lỗi: {e}")
            break
