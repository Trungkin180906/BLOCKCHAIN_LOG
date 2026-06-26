"""blockchain.py
Định nghĩa class Blockchain: quản lý toàn bộ chuỗi các Block.
Nhiệm vụ chính:
    1. Tạo Genesis Block (block đầu tiên, previous_hash = "0").
    2. add_block(): nối block mới vào cuối chuỗi.
    3. is_chain_valid(): quét toàn bộ chuỗi để phát hiện block nào bị sửa.
    4. find_block_by_log_hash(): hỗ trợ phần Audit Tool (Giai đoạn 4) tìm
       xem 1 mã hash log có tồn tại/khớp trên chuỗi hay không."""
from core.blocks import Block

class Blockchain:
    def __init__(self):
        self.chain=[]
        self.chain.append(self.create_genesis_block())#tạo genesis block ngay khi khởi tạo chuỗi

    def create_genesis_block(self):
        """tạo block đầu tiên của chuỗi
        previous_hash=0 vì ko có block trước đó
        return block: object block đầu tiên của chuỗi"""
        return Block(index=0, log_data='Genesis Block - khởi tạo chuỗi', previous_hash='0')#trả về object block đầu tiên 
    
    def get_last_block(self)->Block:
        """lấy block cuối cùng trong chuỗi
        return block: object block cuối cùng trong chuỗi"""
        return self.chain[-1]#trả về block cuối cùng trong list chain
    
    def add_block(self, new_block:Block)->Block:#thêm block
        """tạo log mới chứa log_data, gắn previous_hash=hash của block 
        cuối cùng trong chuỗi, rồi nối vào chuỗi
        args: new_block: object block mới cần thêm vào chuỗi
        return block: object block mới đã được thêm vào """
        new_block.previous_hash=self.get_last_block().hash
        new_block.hash=new_block.calculate_hash()
        self.chain.append(new_block)
        return new_block
    
    ##lớp kiểm tra tính toàn vẹn
    def is_chain_valid(self)->dict:
        """quét toàn bộ chuỗi để phát hiện block bị sửa
        Với mỗi block (trừ Genesis), kiểm tra 3 điều:
        Duyệt từ block 1 đến cuối, kiểm tra 3 điều kiện:
            1. Hash tính lại có khớp không?         → phát hiện data bị sửa
            2. previous_hash có trỏ đúng block trước? → phát hiện đứt xích
            3. log_hash có khớp với log_data không?   → phát hiện log bị sửa"""
        error=[]
        for i in range(1, len(self.chain)):#bỏ qua block đầu tiên 
            current_block=self.chain[i]
            previous_block=self.chain[i-1]

            #check (a) hash của block có bị sửa hay ko
            recalculated_hash=current_block.calculate_hash()#tính hash tổng thể từ các field hiện tại
            if current_block.hash!=recalculated_hash:#nếu hash tổng thể ko khớp với hash đã lưu
                error.append({
                    "block_index": i,
                    "error": (
                        f"Hash không khớp! "
                        f"Lưu: {current_block.hash[:16]}... | "
                        f"Tính lại: {recalculated_hash[:16]}...")})
            
            #check (b) hash tổng thể có bị sửa hay ko
            if current_block.previous_hash != previous_block.hash:
                error.append({
                    "block_index": i,
                    "error": (
                        f"Liên kết bị đứt! "
                        f"previous_hash: {current_block.previous_hash[:16]}... "
                        f"≠ hash block #{i-1}: {previous_block.hash[:16]}...")})
            
            #check (c) sợi dây liên kết với block trước có bị đứt
            if not current_block.is_log_intact():
                error.append({
                    "block_index": i,
                    "error": (
                        f"Log Data bị sửa! "
                        f"log_hash lưu: {current_block.log_hash[:16]}... "
                        f"không khớp với log_data hiện tại.")})
            
        return {"valid"         : len(error) == 0,
                "errors"        : error,
                "blocks_checked": len(self.chain) - 1,}

    #tấn công giả lập
    def tamper_block(self, index:int, new_log_data:str)->dict:
        if index<1 or index>=len(self.chain):
            return {"success": False,
                    "error"  : "Không thể sửa Genesis Block hoặc index vượt phạm vi."}
        block=self.chain[index]
        old_data=block.log_data

        #sửa thẳng không tính lại hassh 
        block.log_data=new_log_data
        return {"success"     : True,
                "block_index" : index,
                "old_data"    : old_data,
                "new_data"    : new_log_data,
                "stored_hash" : block.hash,
                "actual_hash" : block.calculate_hash(),
                "hash_match"  : block.hash == block.calculate_hash(),}

    def to_dict(self)->list[dict]:
        """chuyển toàn bộ chain thành list[dict] để phục lưu trữ json"""
        return [b.to_dict() for b in self.chain]#trả về list chứa dict của từng block
        
    def get_stats(self)->dict:
        """dựng lại 1 object blockchain từ list[dict]
        args: chain_data list[dict]: list chứa dict của từng block
        return blockchain: object blockchain được dựng lại từ list[dict]"""
        latest=self.get_last_block()
        return {"total_blocks" : len(self.chain),
               "latest_index" : latest.index,
               "latest_hash"  : latest.hash,
               "genesis_hash" : self.chain[0].hash,
               "is_valid"     : self.is_chain_valid()["valid"],}
        
    def __len__(self):
        return len(self.chain)
        
    def __repr__(self):
        return f'Blockchain(block={len(self.chain)} valid={self.is_chain_valid()['valid']})'
        
