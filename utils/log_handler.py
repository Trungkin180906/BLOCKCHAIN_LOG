import os
import time

class LogHandler:
    def __init__(self, log_dir="data/raw_logs", log_file="system.log"):
        """
        Khởi tạo đường dẫn đến thư mục và file log.
        Mặc định trỏ thẳng vào data/raw_logs/system.log như cấu trúc anh em đã chốt.
        """
        self.log_dir = log_dir
        self.log_file = os.path.join(self.log_dir, log_file)
        self._setup_environment()

    def _setup_environment(self):
        """
        Khâu chuẩn bị hiện trường: 
        Nếu thư mục chưa có thì tạo mới. Nếu file log chưa có thì đẻ ra một file rỗng.
        Tránh lỗi sập app ngay lần chạy đầu tiên.
        """
        os.makedirs(self.log_dir, exist_ok=True)
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w", encoding="utf-8") as f:
                f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] SYS - Hệ thống ghi log bắt đầu hoạt động...\n")

    def generate_dummy_log(self, message):
        """
        Hàm này hỗ trợ tạo log giả lập để anh em chạy test lúc demo.
        Ghi nối (append - 'a') thêm một dòng log mới vào cuối file.
        """
        with open(self.log_file, "a", encoding="utf-8") as f:
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            f.write(f"[{timestamp}] INFO - {message}\n")
        print(f"Đã ghi log mới: {message}")

    def fetch_logs_for_batching(self):
        """
        HÀM ĂN TIỀN NHẤT: Bốc log đi băm (Batching)
        Nó sẽ đọc toàn bộ nội dung file log hiện tại, lưu vào biến.
        Sau đó xóa trắng file log cũ đi để hệ thống ghi cụm log mới cho chu kỳ sau.
        """
        if not os.path.exists(self.log_file):
            return ""

        try:
            # Bước 1: Mở hòm bốc hết log ra
            with open(self.log_file, "r", encoding="utf-8") as f:
                logs_content = f.read().strip()
            
            # Bước 2: Nếu bốc được chữ nào thì dọn sạch hòm để đón lứa log mới
            if logs_content:
                with open(self.log_file, "w", encoding="utf-8") as f:
                    f.write("") # Ghi đè bằng chuỗi rỗng = xóa sạch
            
            return logs_content

        except PermissionError:
            # Bắt tại trận lỗi file bị hệ thống khóa
            print("TRỞ NGẠI KỸ THUẬT: File log đang bị một tiến trình khác chiếm dụng, không thể đọc/ghi!")
            return ""
        except Exception as e:
            print(f"Lỗi không xác định khi đọc log: {e}")
            return ""