import json
import os

class StorageManager:
    def __init__(self, file_path="data/chain_data.json"):
        """Khởi tạo thủ kho, chỉ định rõ cái kho chứa là file nào"""
        self.file_path = file_path
        # Tránh lỗi sập app nếu chưa có thư mục data/
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_chain(self, chain_data_list):
        """
        Lưu toàn bộ chuỗi (đã chuyển thành List[Dict]) xuống ổ cứng.
        """
        try:
            # Dùng indent=4 để file JSON lưu ra nhìn đẹp và dễ đọc khi mở bằng Notepad
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(chain_data_list, f, indent=4)
            return True
        except Exception as e:
            print(f"LỖI VẬN HÀNH: Không thể ghi đè dữ liệu xuống ổ cứng: {e}")
            return False

    def load_chain(self):
        """
        Đọc dữ liệu từ file JSON lên để khôi phục chuỗi.
        Trả về một list chứa các dict. Nếu không có file hoặc file hỏng thì trả về list rỗng.
        """
        if not os.path.exists(self.file_path):
            return [] # Chưa có file thì báo là chuỗi trống
            
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            # Bắt tại trận lỗi file bị hỏng
            print("File chain_data.json đã bị hỏng cấu trúc (Corrupted)!")
            return []