
import os

import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import *


class EntryWindow(QWidget):
    """信息录入窗口"""

    def __init__(self, db, main_window):
        super().__init__()
        self.db = db
        self.main_window = main_window
        self.cap = None
        self.current_photo = None
        self.init_ui()
        self.start_camera()
        self.set_style()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('信息录入')
        self.setGeometry(350, 350, 900, 700)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 身份证信息区域
        self.id_info_group = QGroupBox("身份证信息（模拟数据）")
        id_layout = QFormLayout()
        id_layout.setRowWrapPolicy(QFormLayout.WrapAllRows)
        self.name_label = QLabel()
        self.gender_label = QLabel()
        self.nation_lable = QLabel()
        self.brithday_lable = QLabel()
        self.adress_lable = QLabel()
        self.id_label = QLabel()
        for label in [self.name_label, self.gender_label, self.id_label]:
            label.setMinimumWidth(300)
        id_layout.addRow("姓名:", self.name_label)
        id_layout.addRow("性别:", self.gender_label)
        id_layout.addRow("身份证号:", self.id_label)
        self.id_info_group.setLayout(id_layout)

        # 摄像头区域
        self.camera_label = QLabel()
        self.camera_label.setAlignment(Qt.AlignCenter)
        self.camera_label.setStyleSheet("border: 2px solid #ddd; border-radius: 5px;")
        self.camera_label.setFixedSize(640, 480)

        # 操作按钮
        self.capture_btn = QPushButton('📸 拍摄照片')
        self.confirm_btn = QPushButton('✅ 确认保存')
        self.retry_btn = QPushButton('🔄 重新拍摄')
        self.confirm_btn.setEnabled(False)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.retry_btn)
        btn_layout.addWidget(self.confirm_btn)

        # 组装界面
        main_layout.addWidget(self.id_info_group)
        main_layout.addWidget(self.camera_label)
        main_layout.addWidget(self.capture_btn)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # 连接信号
        self.capture_btn.clicked.connect(self.capture_photo)
        self.confirm_btn.clicked.connect(self.save_data)
        self.retry_btn.clicked.connect(self.retry_capture)

        # 模拟身份证数据
        self.read_id_card()

    def set_style(self):
        """设置界面样式"""
        self.setStyleSheet('''
            QPushButton {
                min-width: 120px;
                padding: 12px;
                font-size: 14px;
            }
            QLabel {
                font-size: 14px;
                color: #333;
            }
        ''')

    def read_id_card(self):
        """模拟读取身份证信息（需连接真实读卡器）"""
        self.name_label.setText("蒋成财")
        self.gender_label.setText("男")
        self.nation_lable.setText("汉")
        self.brithday_lable.setText("2000-01-01")
        self.adress_lable.setText("北京市朝阳区")
        self.id_label.setText("123456")

    def start_camera(self):
        """启动摄像头"""
        self.cap = cv2.VideoCapture(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        """更新摄像头画面"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 转换为RGB格式显示
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = frame.shape
                bytes_per_line = ch * w
                image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                self.camera_label.setPixmap(QPixmap.fromImage(image))

    def capture_photo(self):
        """拍摄照片"""
        if self.cap and self.cap.isOpened():
            ret, frame = self.cap.read()
            if ret:
                # 确保photos目录存在
                os.makedirs('photos', exist_ok=True)

                # 生成文件名并保存
                filename = f"{self.id_label.text()}.jpg"
                self.current_photo = os.path.join('photos', filename)
                cv2.imwrite(self.current_photo, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

                # 显示拍摄结果
                self.show_captured_image(frame)

                # 停止摄像头
                self.timer.stop()
                self.cap.release()
                self.cap = None

                # 启用确认按钮
                self.confirm_btn.setEnabled(True)

    def show_captured_image(self, frame):
        """显示拍摄后的静态图片"""
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.camera_label.setPixmap(QPixmap.fromImage(image).scaled(
            640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def save_data(self):
        """保存数据到数据库"""
        if self.current_photo and os.path.exists(self.current_photo):
            try:
                user_data = (
                    self.name_label.text(),
                    self.gender_label.text(),
                    self.nation_lable.text(),  # 民族
                    self.brithday_lable.text(),  # 出生日期
                    self.adress_lable.text(),  # 地址
                    self.id_label.text(),
                    self.current_photo
                )
                self.db.insert_user(user_data)
                self.main_window.load_table_data()
                self.main_window.show()
                self.close()
                QMessageBox.information(self, "成功", "信息保存成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")

    def retry_capture(self):
        """重新拍摄"""
        self.current_photo = None
        self.confirm_btn.setEnabled(False)
        self.start_camera()

    def closeEvent(self, event):
        """关闭窗口时释放摄像头资源"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)

