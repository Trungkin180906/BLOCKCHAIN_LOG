"""Định nghĩa cấu trúc 1 "Block" trong chuỗi Blockchain mô phỏng.
Mỗi Block đóng vai trò như 1 "hộp" chứa:
    - index          : Vị trí của Block trong chuỗi (0, 1, 2, ...)
    - timestamp       : Thời điểm Block được tạo
    - log_data        : Nội dung log gốc (raw) được gom lại (để dễ debug/đọc lại)
    - log_hash        : Mã băm SHA-256 của log_data (đại diện "dấu vân tay" cho log)
    - previous_hash   : Mã băm của Block ngay trước nó -> tạo sự liên kết (chaining)
    - hash            : Mã băm của CHÍNH Block này (tính từ tất cả field bên trên)
Nguyên lý quan trọng:
    Hash của Block hiện tại được tính dựa trên cả "previous_hash" của Block trước.
    => Nếu dữ liệu của 1 Block cũ bị sửa, hash của nó đổi, kéo theo toàn bộ
       các Block phía sau bị "đứt xích" (previous_hash không còn khớp nữa)."""
import hashlib#thư viện mã băm sha-256
import time
import json#thư viện xử lý json

class Block:
    def __init__(self, index, log_data, previous_hash, log_hash=None, timestamp=None):
        self.index=index#vị trí của block trong chuỗi
        self.timestamp=timestamp if timestamp is not None else time.time()#time block được tạo
        self.log_data=log_data#nội dung log gốc
        self.log_hash=log_hash if log_hash is not None else self.calculate_log_hash(log_data)#mã băm 
        self.previous_hash=previous_hash#mã băm của block trước
        self.hash=self.calculate_hash()#mã băm của block hiện tại

    @staticmethod#phương thức tĩnh, không cần tạo đối tượng
    def calculate_log_hash(log_data):
        """Băm nội dung log gốc bằng SHA-256.
        Đây chính là bước "Ép ra dấu vân tay" cho cụm log vừa gom (batching).
        Args: log_data (str): Nội dung log thô.
        Returns:str: Chuỗi hash SHA-256 (dạng hex)."""
        return hashlib.sha256(log_data.encode('utf-8')).hexdigest()#mã băm sha256 chuyển về hex
    
    def calculate_hash(self):
        """Tính hash cho CHÍNH block này.
        Cách làm:
            1. Đóng gói (json.dumps) toàn bộ thông tin quan trọng của block
               thành 1 chuỗi string có cấu trúc cố định (sort_keys=True để
               đảm bảo thứ tự key luôn giống nhau -> hash luôn nhất quán).
            2. Băm chuỗi đó bằng SHA-256.
        Lưu ý: previous_hash được đưa vào cùng -> đây chính là bước "chaining"
        (móc xích các block lại với nhau).
        Returns:
            str: Chuỗi hash SHA-256 (dạng hex) đại diện cho toàn bộ block."""
        block_content={
            'index':self.index,
            'timestamp':self.timestamp,
            'log_hash':self.log_hash,
            'previous_hash':self.previous_hash,}#tạo dict chứa info block
        block_string=json.dumps(block_content, sort_keys=True).encode()#chuyển dict thành chuỗi json
        return hashlib.sha256(block_string).hexdigest()#băm chuỗi json thành hash sha256
    
    def is_log_intact(self):
        """ Kiểm tra xem log_data hiện tại có khớp với log_hash đã lưu
        trong block này không. Dùng cho việc đối soát (audit) từng block lẻ.
        Returns: bool: True nếu khớp (log nguyên vẹn), False nếu lệch (log đã bị sửa).
        """
        return self.calculate_log_hash(self.log_data)==self.log_hash
    
    def to_dict(self):
        """chuyển block thành dict thuân (phục vụ việc lưu json, in ra màn hình)
        return: dict: dict chứa thông tin block"""
        return{
            'index':self.index,
            'timestamp':self.timestamp,
            'log_data':self.log_data,
            'log_hash':self.log_hash,
            'previous_hash':self.previous_hash,
            'hash':self.hash,}
    
    @classmethod#phương thức lớp, có thể gọi trực tiếp từ class mà ko cần tạo object
    def from_dict(cls, data):
        """dựng lại 1 object block từ dict 
        args: data (dict): dict chứa thông tin block
        return: block: object block được dựng lại từ dict 
        để có thể phát hiện log đã bị sửa hay không 
        """
        block=cls(
            index=data['index'],
            log_data=data['log_data'],
            previous_hash=data['previous_hash'],
            log_hash=data['log_hash'],
            timestamp=data['timestamp'],)#tạo object block từ dict
        """gắn hash của block từ dict vào object block để có thể phát hiện log đã bị sửa hay ko"""
        block.hash=data['hash']
        return block
    
    def __repr__(self):#định nghĩa cách hiển thị block khi in
        prev_hash_display='0' if self.previous_hash=='0' else f'{self.previous_hash[:10]}...'
        return (f'Block(index={self.index}, '
                f'hash={self.hash[:10]}..., '
                f'previous_hash={prev_hash_display}...)')
    

