import sys
import time
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTextEdit, QLabel, QGroupBox, 
                             QLineEdit, QSpinBox, QScrollArea, QFrame, QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont

from core.blockchain import Blockchain
from core.block import Block
from utils.log_handler import LogHandler
from utils.storage_manager import StorageManager


class BlockCard(QFrame):
    """Thẻ hiển thị từng Block bo góc Neon, tự động đổi màu theo trạng thái toàn vẹn"""
    def __init__(self, block, is_corrupted=False, parent=None):
        super().__init__(parent)
        self.block = block
        self.setFixedSize(QSize(210, 360))
        
        if is_corrupted:
            border_color = "#ef4444"
            bg_color = "#1e1112"
            title_color = "#fca5a5"
        else:
            border_color = "#10b981"
            bg_color = "#111827"
            title_color = "#34d399"

        self.setStyleSheet(f"""
            BlockCard {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: 12px;
                padding: 12px;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(12, 12, 12, 12)
        
        self.lbl_title = QLabel(f"📦 Block #{block.index}" + (" (Genesis)" if block.index == 0 else ""))
        self.lbl_title.setStyleSheet(f"color: {title_color}; font-weight: bold; font-size: 14px; border: none;")
        layout.addWidget(self.lbl_title)
        
        time_str = time.strftime('%H:%M:%S %d/%m/%Y', time.localtime(block.timestamp))
        layout.addWidget(self._create_field_label("Timestamp:", time_str))
        
        short_log = str(block.log_data)[:20] + "..." if len(str(block.log_data)) > 20 else str(block.log_data)
        layout.addWidget(self._create_field_label("Log Data:", short_log))
        
        log_hash_str = f"{block.log_hash[:8]}...{block.log_hash[-4:]}" if block.log_hash else "N/A"
        layout.addWidget(self._create_field_label("Log Hash (SHA256):", log_hash_str))
        
        if is_corrupted:
            self.lbl_warning = QLabel("⚠️ HASH MISMATCH")
            self.lbl_warning.setStyleSheet("color: #ef4444; font-weight: bold; font-size: 11px; border: none;")
            layout.addWidget(self.lbl_warning)
            
        block_hash_str = f"{block.hash[:8]}...{block.hash[-4:]}" if block.hash else "N/A"
        layout.addWidget(self._create_field_label("Current Hash:", block_hash_str))
        
        prev_hash_str = f"{block.previous_hash[:8]}..." if len(str(block.previous_hash)) > 8 else str(block.previous_hash)
        layout.addWidget(self._create_field_label("Previous Hash:", prev_hash_str))
        
        layout.addStretch()
        
        self.btn_card_attack = QPushButton("💥 Attack")
        self.btn_card_attack.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_card_attack.setStyleSheet("""
            QPushButton {
                background-color: #1f2937;
                color: #9ca3af;
                border: 1px solid #4b5563;
                border-radius: 6px;
                padding: 5px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ef4444;
                color: white;
                border: 1px solid #ef4444;
            }
        """)
        layout.addWidget(self.btn_card_attack)

    def _create_field_label(self, title, val):
        """Hàm trợ giúp tạo các nhãn thông tin nhỏ gọn và sắc nét"""
        lbl = QLabel(f"<span style='color: #9ca3af;'>{title}</span><br><span style='color: #f3f4f6; font-family: monospace;'>{val}</span>")
        lbl.setWordWrap(True)
        lbl.setStyleSheet("border: none; font-size: 11px; line-height: 14px;")
        return lbl


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Blockchain Log Security System - Admin Dashboard")
        self.setMinimumSize(QSize(1200, 700))
        
        self.setStyleSheet("background-color: #0b0f19; color: #e5e7eb;")
        
        self.blockchain = Blockchain()
        self.log_handler = LogHandler()
        self.storage_manager = StorageManager()
        
        self.load_blockchain_data()
        self.init_ui()
        self.refresh_dashboard()

    def load_blockchain_data(self):
        self.blockchain.chain = []
        self.blockchain.chain.append(self.blockchain.create_genesis_block())

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)
        
        self.top_status_bar = QFrame()
        self.top_status_bar.setStyleSheet("QFrame { background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; }")
        top_layout = QHBoxLayout(self.top_status_bar)
        top_layout.setContentsMargins(15, 12, 15, 12)
        
        self.lbl_chain_badge = QLabel(" CHAIN VALID ")
        self.lbl_chain_badge.setStyleSheet("""
            background-color: #064e3b; color: #10b981; font-weight: bold; 
            border: 1px solid #10b981; border-radius: 4px; padding: 4px 8px;
        """)
        top_layout.addWidget(self.lbl_chain_badge)
        
        self.lbl_total_blocks = QLabel("Blocks: 0")
        self.lbl_total_blocks.setStyleSheet("color: #9ca3af; font-size: 13px; font-weight: bold; margin-left: 15px;")
        top_layout.addWidget(self.lbl_total_blocks)
        
        lbl_title_app = QLabel("🛡️ Blockchain Log Audit Tool Dashboard")
        lbl_title_app.setStyleSheet("color: #ffffff; font-size: 16px; font-weight: bold;")
        top_layout.addStretch()
        top_layout.addWidget(lbl_title_app)
        
        main_layout.addWidget(self.top_status_bar)
        
        body_layout = QHBoxLayout()
        body_layout.setSpacing(15)
        
        control_panel = QFrame()
        control_panel.setFixedWidth(290)
        control_panel.setStyleSheet("QFrame { background-color: #111827; border: 1px solid #1f2937; border-radius: 8px; }")
        control_layout = QVBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(12)
        
        control_layout.addWidget(QLabel("<span style='color: #ffffff; font-weight: bold;'>Ghi Nhận Nhật Ký Hệ Thống:</span>"))
        self.txt_log_input = QLineEdit()
        self.txt_log_input.setPlaceholderText("Nhập nội dung sự kiện log...")
        self.txt_log_input.setStyleSheet("""
            QLineEdit {
                background-color: #1f2937; color: #ffffff; 
                border: 1px solid #374151; border-radius: 6px; padding: 8px;
            }
        """)
        control_layout.addWidget(self.txt_log_input)
        
        hbox_btns = QHBoxLayout()
        self.btn_add_log = QPushButton("➕ Add Log")
        self.btn_add_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_log.setStyleSheet("background-color: #065f46; color: #34d399; font-weight: bold; padding: 7px; border-radius: 4px; border: none;")
        self.btn_add_log.clicked.connect(self.handle_add_log_click)
        
        self.btn_random_log = QPushButton("🎲 Random Log")
        self.btn_random_log.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_random_log.setStyleSheet("background-color: #1e3a8a; color: #60a5fa; padding: 7px; border-radius: 4px; border: none;")
        self.btn_random_log.clicked.connect(self.handle_random_log_click)
        
        hbox_btns.addWidget(self.btn_add_log)
        hbox_btns.addWidget(self.btn_random_log)
        control_layout.addLayout(hbox_btns)
        
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #1f2937;")
        control_layout.addWidget(line)
        
        control_layout.addWidget(QLabel("<span style='color: #ffffff; font-weight: bold;'>Công Cụ Kiểm Định:</span>"))
        
        self.btn_verify = QPushButton("🛡️ Verify Chain ")
        self.btn_verify.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_verify.setStyleSheet("background-color: #78350f; color: #fbbf24; font-weight: bold; padding: 9px; border-radius: 4px; border: none;")
        self.btn_verify.clicked.connect(self.handle_verify_chain)
        control_layout.addWidget(self.btn_verify)
        
        self.btn_reset = QPushButton("🔄 Reset / Khôi Phục")
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.setStyleSheet("background-color: #374151; color: #d1d5db; padding: 8px; border-radius: 4px; border: none;")
        self.btn_reset.clicked.connect(self.handle_reload_chain)
        control_layout.addWidget(self.btn_reset)
        
        control_layout.addStretch()
        body_layout.addWidget(control_panel)
        
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: #0b0f19; border: 1px solid #1f2937; border-radius: 8px; }")
        
        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background-color: #0b0f19;")
        
        self.chain_layout = QHBoxLayout(self.scroll_content)
        self.chain_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.chain_layout.setContentsMargins(20, 10, 20, 10)
        self.chain_layout.setSpacing(0) 
        
        self.scroll_area.setWidget(self.scroll_content)
        body_layout.addWidget(self.scroll_area)
        
        main_layout.addLayout(body_layout)

    
    def refresh_dashboard(self):
        """Hàm then chốt vẽ lại chuỗi xích và tự động xử lý đứt xích dây chuyền"""
        while self.chain_layout.count():
            item = self.chain_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
            
        audit_res = self.blockchain.is_chain_valid()
        self.lbl_total_blocks.setText(f"Blocks: {len(self.blockchain.chain)}")
        
        if audit_res["valid"]:
            self.lbl_chain_badge.setText(" ✔️ CHAIN VALID ")
            self.lbl_chain_badge.setStyleSheet("background-color: #064e3b; color: #10b981; font-weight: bold; border: 1px solid #10b981; border-radius: 4px; padding: 4px 8px;")
        else:
            self.lbl_chain_badge.setText(" ❌ CHAIN CORRUPTED ")
            self.lbl_chain_badge.setStyleSheet("background-color: #7f1d1d; color: #f87171; font-weight: bold; border: 1px solid #f87171; border-radius: 4px; padding: 4px 8px;")
            
        chain_has_broken = False
        
        for i, block in enumerate(self.blockchain.chain):
            is_corrupted = False
            if i > 0:
                self_corrupted = any(err["block_index"] == i for err in audit_res["errors"])
                if self_corrupted or chain_has_broken:
                    is_corrupted = True
                    chain_has_broken = True 
                
            card = BlockCard(block, is_corrupted=is_corrupted)
            card.btn_card_attack.clicked.connect(lambda checked, idx=block.index: self.trigger_attack_on_block(idx))
            self.chain_layout.addWidget(card)
            
            if i < len(self.blockchain.chain) - 1:
                lbl_arrow = QLabel(" ➔ ")
                arrow_color = "#ef4444" if chain_has_broken else "#10b981"
                lbl_arrow.setStyleSheet(f"color: {arrow_color}; font-size: 22px; font-weight: bold; border: none; padding: 0px 4px;")
                self.chain_layout.addWidget(lbl_arrow)

    def handle_add_log_click(self):
        msg = self.txt_log_input.text().strip()
        if not msg:
            QMessageBox.warning(self, "Thông báo", "Vui lòng nhập nội dung sự kiện log!")
            return
        
        
        self.log_handler.generate_dummy_log(msg)
        logs_content = self.log_handler.fetch_logs_for_batching()
        
        
        if len(self.blockchain.chain) == 0:
            
            new_block = Block(
                index=0,
                log_data=logs_content,
                previous_hash="0"
            )
        else:
            
            new_block = Block(
                index=len(self.blockchain.chain),
                log_data=logs_content,
                previous_hash=self.blockchain.get_last_block().hash
            )
            
        self.blockchain.add_block(new_block)
        self.storage_manager.save_chain(self.blockchain.to_dict())
        
        self.txt_log_input.clear()
        self.refresh_dashboard()

    def handle_random_log_click(self):
        """Sinh chuỗi log ngẫu nhiên chuẩn cấu hình máy chủ phục vụ test nhanh"""
        samples = [
            "USER - Admin login successful from IP 192.168.1.100",
            "DB_SYS - Backup database operation completed in 142ms",
            "NETWORK - Port 443 detected high incoming connections",
            "AUTH_ERR - User 'guest_9' failed password verification"
        ]
        self.txt_log_input.setText(random.choice(samples))

    def trigger_attack_on_block(self, block_index):
        """Kích hoạt tấn công can thiệp dữ liệu bằng cách nhấn trực tiếp nút Attack dưới chân card"""
        if block_index == 0:
            QMessageBox.warning(self, "Lỗi can thiệp", "Genesis Block là khối khởi thủy, không cho phép can thiệp chỉnh sửa!")
            return
            
        res = self.blockchain.tamper_block(block_index, "⚠️ Hacker can thiệp - Nhật ký log đã bị xóa sửa!")
        if res["success"]:
            self.refresh_dashboard()

    def handle_verify_chain(self):
        """Quét đối soát tính toàn vẹn và đẩy lên hộp thoại thông báo chi tiết lỗi"""
        audit_res = self.blockchain.is_chain_valid()
        self.refresh_dashboard()
        
        if audit_res["valid"]:
            QMessageBox.information(self, "Kết quả Audit", f"Hệ thống an toàn tuyệt đối!\nĐã xác thực thành công cấu trúc liên kết của {audit_res['blocks_checked']} Khối.")
        else:
            err_msg = f"🛑 PHÁT HIỆN SỬA ĐỔI DỮ LIỆU LOG (Tổng cộng {len(audit_res['errors'])} vị trí lỗi):\n\n"
            for err in audit_res["errors"]:
                err_msg += f"📍 [Khối số #{err['block_index']}]: Dữ liệu bị thay đổi gây lệch mã Hash!\n\n"
            QMessageBox.critical(self, "Cảnh Báo Tính Toàn Vẹn", err_msg)

    def handle_reload_chain(self):
        """Cơ chế cứu hộ: Tải lại chuỗi sạch từ file json để ép các khối đỏ hóa xanh trở lại"""
        saved_data = self.storage_manager.load_chain()
        if saved_data:
            self.blockchain.chain = []
            for block_dict in saved_data:
                self.blockchain.chain.append(Block.from_dict(block_dict))
            self.refresh_dashboard()
            QMessageBox.information(self, "Đồng bộ", "Hệ thống tự động phát hiện sai lệch và khôi phục chuỗi log sạch thành công!")
        else:
            QMessageBox.warning(self, "Thông báo", "Chưa có dữ liệu sạch nào được lưu dưới ổ cứng.")