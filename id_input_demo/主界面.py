from PyQt5.QtWidgets import *
# 假设其他导入保持不变
from 数据库 import Database
from 信息录入 import EntryWindow
from 信息查询 import QueryDialog


class MainWindow(QWidget):
    """主界面类"""

    def __init__(self):
        super().__init__()
        self.db = Database()
        self.init_ui()
        self.set_style()  # 应用样式

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('智能信息管理系统')
        self.setGeometry(300, 300, 1000, 800)

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(30)

        # 功能按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(40)
        self.entry_btn = QPushButton('📷 信息录入')
        self.query_btn = QPushButton('🔍 信息查询')
        for btn in [self.entry_btn, self.query_btn]:
            btn.setFixedSize(200, 60)
        btn_layout.addWidget(self.entry_btn)
        btn_layout.addWidget(self.query_btn)

        # 数据显示表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['姓名', '性别', '身份证号'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
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
            /* 样式规则保持不变 */
        """)

    def load_table_data(self):
        """加载表格数据"""
        data = self.db.get_all_users()
        self.table.setRowCount(len(data))
        for row, (name, gender, id_num) in enumerate(data):
            self.table.setItem(row, 0, QTableWidgetItem(name))
            self.table.setItem(row, 1, QTableWidgetItem(gender))
            self.table.setItem(row, 2, QTableWidgetItem(id_num))

    def refresh_table(self):
        """刷新表格数据"""
        self.table.clearContents()  # 清除现有内容
        self.load_table_data()  # 重新加载数据

    def show_entry_window(self):
        """显示信息录入窗口"""
        self.entry_window = EntryWindow(self.db, self)
        self.entry_window.show()
        self.hide()

    def show_query_dialog(self, main_window):
        """显示查询对话框"""
        dialog = QueryDialog(self.db, main_window)
        dialog.exec_()
