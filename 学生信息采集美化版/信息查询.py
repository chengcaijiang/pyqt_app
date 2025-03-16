import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import *


def create_info_layout(data):
    """创建用户信息布局"""
    info_layout = QFormLayout()
    info_layout.addRow("姓名：", QLabel(data[0]))
    info_layout.addRow("性别：", QLabel(data[1]))
    info_layout.addRow("民族：", QLabel(data[2]))
    info_layout.addRow("出生日期：", QLabel(data[3]))
    info_layout.addRow("住址：", QLabel(data[4]))
    info_layout.addRow("身份证号：", QLabel(data[5]))
    return info_layout


def clear_layout(layout):
    """清除布局中的所有控件（包括嵌套布局）"""
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout:
                    clear_layout(sub_layout)  # 递归清除子布局
                    sub_layout.deleteLater()  # 删除子布局对象
        # 可选：删除布局对象本身（如果不再需要）
        layout.deleteLater()


def create_photo_label(photo_path):
    """创建照片标签"""
    photo_label = QLabel()
    if os.path.exists(photo_path):
        pixmap = QPixmap(photo_path).scaled(640, 480, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        photo_label.setPixmap(pixmap)
    else:
        photo_label.setText("照片未找到")
    photo_label.setAlignment(Qt.AlignCenter)
    photo_label.setStyleSheet("border: 1px solid #ddd; padding: 10px;")
    return photo_label


class QueryDialog(QDialog):
    """信息查询对话框"""

    def __init__(self, db, main_window):
        super().__init__()
        self.result_group = None
        self.id_input = None
        self.db = db  # 数据库连接对象
        self.main_window = main_window  # 主窗口引用
        self.init_ui()  # 初始化用户界面
        self.set_style()  # 设置样式

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('信息查询')
        self.setFixedSize(680, 1100)  # 增加窗口高度以适应新的按钮
        self.setWindowIcon(QIcon('background2.jpg'))  # Windows优先使用
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 查询输入组件
        self.setup_input(main_layout)

        # 查询结果组件
        self.result_group = QGroupBox("查询结果")
        main_layout.addWidget(self.result_group)

        self.setLayout(main_layout)

    def setup_input(self, layout):
        """设置查询输入区域"""
        input_layout = QHBoxLayout()

        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("请输入身份证号码...")
        search_btn = QPushButton('🔍 开始查询')
        search_btn.setStyleSheet("font-size: 24px;font-weight: bold;")

        input_layout.addWidget(self.id_input)
        input_layout.addWidget(search_btn)
        layout.addLayout(input_layout)

        search_btn.clicked.connect(self.do_search)

    def set_style(self):
        """设置样式"""
        self.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QGroupBox {
                margin-top: 20px;
            }
            QLabel {
                font-weight: bold;         /* 字体加粗 */
                font-size: 30px;
                color: #333;
            }
            QPushButton {
                background-color: rgba(46, 139, 87, 0.8);  /* 半透明按钮 */
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 20px;
            }
             QPushButton:hover {
                background-color: rgba(240, 135, 132, 0.9);  /* 悬停颜色 */
            }
        ''')

    def display_result(self, data):
        """显示查询结果"""
        # 清除旧的内容
        clear_layout(self.result_group.layout())

        # 创建新的内容布局
        layout = QVBoxLayout()  # 使用垂直布局以容纳更多信息

        # 照片显示
        photo_label = create_photo_label(data[6])
        layout.addWidget(photo_label)

        # 用户信息显示
        info_layout = create_info_layout(data)
        layout.addLayout(info_layout)

        # 删除按钮
        delete_button = QPushButton('删除此条记录和照片')
        delete_button.setFixedSize(640, 100)
        delete_button.clicked.connect(lambda: self.delete_data_and_image(data[5], data[6]))  # 使用身份证号和照片路径作为参数
        layout.addWidget(delete_button)

        self.result_group.setLayout(layout)

    def do_search(self):
        """执行查询操作"""
        # 清空之前的查询结果
        if self.result_group.layout():
            clear_layout(self.result_group.layout())

        id_number = self.id_input.text().strip()
        if not id_number:
            QMessageBox.warning(self, "提示", "请输入身份证号码")
            return

        result = self.db.search_user(id_number)

        if result:
            self.display_result(result)
        else:
            QMessageBox.information(self, "提示", "未找到匹配的记录")

    def delete_data_and_image(self, id_number, photo_path):
        """删除数据库记录和对应的图片"""
        try:
            # 删除数据库中的记录
            self.db.delete_user(id_number)
            # 删除图片文件
            if os.path.exists(photo_path):
                os.remove(photo_path)
            QMessageBox.information(self, "成功", "记录和照片已删除")
            # 如果主窗口存在，则刷新表格
            if self.main_window:
                self.main_window.refresh_table()
            # 清空查询结果展示
            clear_layout(self.result_group.layout())
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除过程中发生错误: {str(e)}")
