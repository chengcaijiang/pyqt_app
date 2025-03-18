# 登录窗口
import re
import sqlite3

from PyQt5.QtWidgets import *


def setup_database():
    """初始化系统用户表"""
    conn = sqlite3.connect('user_info.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS system_users 
                    (username TEXT PRIMARY KEY, password TEXT)''')
    conn.commit()
    conn.close()


class LoginDialog(QDialog):
    """登录/注册对话框"""

    def __init__(self):
        super().__init__()
        self.register_confirm = None
        self.register_password = None
        self.login_password = None
        self.login_username = None
        self.register_username = None
        self.register_tab = None
        self.login_tab = None
        self.tab_widget = None
        self.current_user_table = None
        self.init_ui()
        setup_database()
        self.set_style()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('login')
        self.setFixedSize(500, 500)

        # 使用选项卡切换登录/注册
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(
            """
            QTabWidget {
                font-size: 40px;
                font-weight: bold;
                color: green;          /* 颜色名方式 */
            }
            """
        )
        self.login_tab = QWidget()
        self.register_tab = QWidget()

        # 添加选项卡
        self.tab_widget.addTab(self.login_tab, "登录")
        self.tab_widget.addTab(self.register_tab, "注册")

        # 登录页面布局
        self.setup_login_tab()
        # 注册页面布局
        self.setup_register_tab()

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)

    def setup_login_tab(self):
        """登录页面设置"""
        layout = QVBoxLayout()

        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("请输入用户名")
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("请输入密码")
        self.login_password.setEchoMode(QLineEdit.Password)
        login_btn = QPushButton('登录')
        login_btn.clicked.connect(self.handle_login)

        layout.addWidget(QLabel('用户名:'))
        layout.addWidget(self.login_username)

        layout.addWidget(QLabel('密码:'))
        layout.addWidget(self.login_password)
        layout.addWidget(login_btn)
        self.login_tab.setLayout(layout)

    def setup_register_tab(self):
        """注册页面设置"""
        layout = QVBoxLayout()

        self.register_username = QLineEdit()
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.Password)
        register_btn = QPushButton('注册')
        register_btn.clicked.connect(self.handle_register)

        layout.addWidget(QLabel('用户名:'))
        layout.addWidget(self.register_username)
        layout.addWidget(QLabel('密码:'))
        layout.addWidget(self.register_password)
        layout.addWidget(QLabel('确认密码:'))
        layout.addWidget(self.register_confirm)
        layout.addWidget(register_btn)
        self.register_tab.setLayout(layout)

    def handle_login(self):
        """处理登录逻辑"""
        username = self.login_username.text().strip()
        password = self.login_password.text().strip()

        if not username or not password:
            QMessageBox.warning(self, '错误', '用户名和密码不能为空')
            return

        conn = sqlite3.connect('user_info.db')
        cursor = conn.cursor()
        cursor.execute('SELECT password FROM system_users WHERE username=?', (username,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            QMessageBox.warning(self, '错误', '用户名不存在')
        elif result[0] != password:
            QMessageBox.warning(self, '错误', '密码错误')
        else:
            self.current_user_table = f'user_{username}'
            self.accept()

    def handle_register(self):
        """处理注册逻辑"""
        username = self.register_username.text().strip()
        password = self.register_password.text().strip()
        confirm = self.register_confirm.text().strip()

        if not username or not password or not confirm:
            QMessageBox.warning(self, '错误', '所有字段必须填写')
            return

        if password != confirm:
            QMessageBox.warning(self, '错误', '两次密码输入不一致')
            return

        if not re.match(r'^\w+$', username):
            QMessageBox.warning(self, '错误', '用户名只能包含字母、数字和下划线')
            return

        conn = sqlite3.connect('user_info.db')
        cursor = conn.cursor()

        try:
            # 插入系统用户表
            cursor.execute('INSERT INTO system_users VALUES (?,?)', (username, password))
            # 创建用户专属表
            table_name = f'user_{username}'
            cursor.execute(f'''CREATE TABLE {table_name} (
                name TEXT, gender TEXT, nation TEXT, 
                birth TEXT, address TEXT, id TEXT PRIMARY KEY, 
                photo_path TEXT
            )''')
            conn.commit()
            QMessageBox.information(self, '成功', '注册成功')
            self.current_user_table = table_name
            self.accept()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, '错误', '用户名已存在')
        finally:
            conn.close()

    def set_style(self):
        """设置界面样式"""
        self.setStyleSheet('''
            QLineEdit {
                padding: 8px;
                font-size: 30px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-weight: bold;      /* 加粗（或写 font-weight: 700） */
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 30px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QLabel {
                font-size: 30px;        /* 字号 */
                font-weight: bold;      /* 加粗（或写 font-weight: 700） */
                color: black;          /* 颜色名方式 */
                /* 或 color: #FFA500;  十六进制方式更精准 */
            }

        ''')

