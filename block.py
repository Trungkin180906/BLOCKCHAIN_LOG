"""blockchain.py
Định nghĩa class Blockchain: quản lý toàn bộ chuỗi các Block.
Nhiệm vụ chính:
    1. Tạo Genesis Block (block đầu tiên, previous_hash = "0").
    2. add_block(): nối block mới vào cuối chuỗi.
    3. is_chain_valid(): quét toàn bộ chuỗi để phát hiện block nào bị sửa.
    4. find_block_by_log_hash(): hỗ trợ phần Audit Tool (Giai đoạn 4) tìm
       xem 1 mã hash log có tồn tại/khớp trên chuỗi hay không."""
from .blocks import block
class blockchain:
    def __init__(self):
        self.chain=[self._create_genesis_block()]#list chứ toàn bộ block trong chuỗi

    @staticmethod
    def _create_genesis_block():
        """tạo block đầu tiên của chuỗi
        previous_hash=0 vì ko có block trước đó
        return block: object block đầu tiên của chuỗi"""
        return block(index=0, log_data='GENESIS BLOCK', previous_hash='0')#trả về object block đầu tiên 
    
    def get_last_block(self):
        """lấy block cuối cùng trong chuỗi
        return block: object block cuối cùng trong chuỗi"""
        return self.chain[-1]#trả về block cuối cùng trong list chain
    
    def add_block(self, log_data):
        """tạo log mới chứa log_data, gắn previous_hash=hash của block 
        cuối cùng trong chuỗi, rồi nối vào chuỗi
        args: new_block: object block mới cần thêm vào chuỗi
        return block: object block mới đã được thêm vào """
        previous_block=self.get_last_block()#lấy block cuối cùng trong chuỗi
        new_block=block(index=previous_block.index+1,
                        log_data=log_data,
                        previous_hash=previous_block.hash,)#tạo block mới với index tăng 1 
        self.chain.append(new_block)#nối block mới vào chuỗi
        return new_block
    
    ##lớp kiểm tra tính toàn vẹn
    def is_chain_valid(self):
        """quét toàn bộ chuỗi để phát hiện block bị sửa
        Với mỗi block (trừ Genesis), kiểm tra 3 điều:
            (a) log_data hiện tại có còn khớp với log_hash đã lưu không?
                (phát hiện nếu ai đó sửa trực tiếp nội dung log_data)
            (b) Hash tổng thể lưu trong block có khớp với hash TÍNH LẠI từ
                (index, timestamp, log_hash, previous_hash) không? (phát
                hiện nếu các field này bị sửa)
            (c) previous_hash lưu trong block hiện tại có khớp với hash
                thật của block ngay trước nó không"""
        for i in range(1, len(self.chain)):#bỏ qua block đầu tiên 
            current_block=self.chain[i]
            previous_block=self.chain[i-1]
            #check (a) log_data có bị sửa hay ko

            real_log_hash=current_block.calculate_log_hash(current_block.log_data)#tính hash_log từ log_data hiện tại
            if real_log_hash!=current_block.log_hash:#nếu hash_log ko khớp với hash_log đã lưu
                return False, (f'Block {current_block.index} đã bị sửa'
                                f'Log_data không khớp với log_hash đã lưu'
                                f'(log_hash lưu trữ: {current_block.log_hash[:10]}...,' 
                                f'hash tính lại từ log_data: {real_log_hash[:10]}...)')
            
            #check (b) hash tổng thể có bị sửa hay ko
            recalculated_hash=current_block.calculate_hash()#tính hash tổng thể từ các field hiện tại
            if current_block.hash!=recalculated_hash:#nếu hash tổng thể ko khớp với hash đã lưu
                return False, (f'Block {current_block.index} đã bị sửa'
                                f'Hash tổng thể không khớp'
                                f'(hash lưu trữ: {current_block.hash[:10]}...,' 
                                f'hash tính lại: {recalculated_hash[:10]}...)')
            
            #check (c) sợi dây liên kết với block trước có bị đứt
            if current_block.previous_hash!=previous_block.hash:
                return False, (f'Đứt xích tại Block {current_block.index}'
                                f'previous_hash không khớp với hash của block {previous_block.index}')
            
        return True, None
        
    def find_block_by_log_hash(self, log_hash):
        """tìm block đầu tiên trong chuỗi có log_hash khớp với log_hash đưa vào
        args: log_hash str: mã hash log cần tìm 
        return block: object block có log_hash khớp, hoặc none nếu ko tim thấy"""
        for b in self.chain:#lặp qua toàn bộ block trong chuỗi
            if b.log_hash==log_hash:
                return b
        return None
        
    def to_list(self):
        """chuyển toàn bộ chain thành list[dict] để phục lưu trữ json"""
        return [b.to_dict() for b in self.chain]#trả về list chứa dict của từng block
        
    @classmethod
    def from_list(cls, chain_data):
        """dựng lại 1 object blockchain từ list[dict]
        args: chain_data list[dict]: list chứa dict của từng block
        return blockchain: object blockchain được dựng lại từ list[dict]"""
        bc=cls.__new__(cls)#tạo object blockchain mới từ class mà ko gọi __init__
        bc.chain=[block.from_dict(item) for item in chain_data]#dựng lại list block từ list
        return blockchain
        
    def __len__(self):
        return len(self.chain)
        
    def __repr__(self):
        return f'Blockchain(length={len(self.chain)} block)'
        
