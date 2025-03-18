from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from database import Database
from PyQt5.QtWidgets import *
from info_input import EntryDialog
from info_seacher import QueryDialog


class MainWindow(QWidget):
    """主界面类"""

    def __init__(self, user_table):
        super().__init__()
        self.entry_window = None
        self.query_btn = None
        self.entry_btn = None
        self.table = None
        self.db = Database(user_table)
        self.set_style()  # 应用样式
        self.init_ui()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('智能信息管理系统')
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)
        self.setWindowIcon(QIcon('./background.jpg'))  # Windows优先使用
        self.resize(1200, 1000)  # 设置窗口大小
        self.center()  # 调用居中方法
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)

        # 功能按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)
        self.entry_btn = QPushButton('📷 信息录入')
        self.query_btn = QPushButton('🔍 信息查询')
        self.entry_btn.setStyleSheet("font-size: 30px;font-weight: bold;")
        self.query_btn.setStyleSheet("font-size: 30px;font-weight: bold;")
        for btn in [self.entry_btn, self.query_btn]:
            btn.setFixedSize(200, 100)
        btn_layout.addWidget(self.entry_btn)
        btn_layout.addWidget(self.query_btn)

        # 数据显示表格
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['姓名', '性别', '民族', '身份证号'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # 新增此行
        self.load_table_data()

        # 组装界面
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(QLabel("已录入人员信息列表:"))
        main_layout.addWidget(self.table)

        self.setLayout(main_layout)

        # 连接信号
        self.entry_btn.clicked.connect(self.show_entry_window)
        self.query_btn.clicked.connect(lambda: self.show_query_dialog(self))

    def set_style(self):
        """设置界面样式"""
        self.setStyleSheet("""
            /* 表格标题样式 */
            QHeaderView::section {

                background-color: rgba(22, 65, 124, 0.8);  /* 半透明深绿色 */
                color: white;
                font-weight: bold;
                padding: 4px;
                border: 1px solid #1F5C3A;
            }

            /* 表格背景透明 */
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.2);  /* 半透明白色 */

                gridline-color: #E0E0E0;  /* 网格线颜色 */
                font-size: 25px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #2E8B57;  /* 表格角落颜色 */
            }
            /* 按钮样式 */
            QPushButton {
                background-color: rgba(46, 139, 87, 0.8);  /* 半透明按钮 */
                color: white;
                border-radius: 5px;
                padding: 10px;
                font-size: 20px;
            }
            QPushButton:hover {
                background-color: rgba(35, 110, 70, 1);  /* 悬停颜色 */
            }
        """)

    def load_table_data(self):
        """加载表格数据"""
        data = self.db.get_all_users()
        self.table.setRowCount(len(data))
        for row, (name, gender, nation, id_num) in enumerate(data):
            # 创建单元格并设置居中
            def create_centered_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)  # 设置水平和垂直居中
                return item

            self.table.setItem(row, 0, create_centered_item(name))
            self.table.setItem(row, 1, create_centered_item(gender))
            self.table.setItem(row, 2, create_centered_item(nation))
            self.table.setItem(row, 3, create_centered_item(id_num))

    def refresh_table(self):
        """刷新表格数据"""
        self.table.clearContents()  # 清除现有内容
        self.load_table_data()  # 重新加载数据

    def show_entry_window(self, ):
        """显示信息录入窗口"""
        dialog = EntryDialog(self.db, self)
        dialog.exec_()  # 使用模态对话框

    def show_query_dialog(self, main_window):
        """显示查询对话框"""
        dialog = QueryDialog(self.db, main_window)
        dialog.exec_()

    def center(self):
        """将窗口居中到屏幕中心"""
        qr = self.frameGeometry()  # 获取窗口几何形状
        cp = QDesktopWidget().availableGeometry().center()  # 获取屏幕中心点
        qr.moveCenter(cp)  # 将窗口中心移动到屏幕中心
        self.move(qr.topLeft())  # 移动窗口到新位置
