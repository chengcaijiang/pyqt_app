import re
import sys
from PyQt5.QtWidgets import *

# 数据库
import sqlite3


# 登录窗口
class LoginDialog(QDialog):
    """登录/注册对话框"""

    def __init__(self):
        super().__init__()
        self.login_password = None
        self.login_username = None
        self.register_username = None
        self.register_tab = None
        self.login_tab = None
        self.tab_widget = None
        self.current_user_table = None
        self.init_ui()
        self.setup_database()
        self.set_style()

    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('登录/注册')
        self.setFixedSize(600, 600)

        # 使用选项卡切换登录/注册
        self.tab_widget = QTabWidget()
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
        self.login_password = QLineEdit()
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

    def setup_database(self):
        """初始化系统用户表"""
        conn = sqlite3.connect('user_info.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS system_users 
                        (username TEXT PRIMARY KEY, password TEXT)''')
        conn.commit()
        conn.close()

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
                font-size: 14px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        ''')


class Database:
    """数据库操作类（支持多用户）"""

    def __init__(self, table_name):
        self.conn = sqlite3.connect('user_info.db')
        self.table_name = table_name
        self.create_table()

    def create_table(self):
        """创建用户专属表"""
        cursor = self.conn.cursor()
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {self.table_name}
                         (name TEXT, gender TEXT, nation TEXT, 
                          birth TEXT, address TEXT, id TEXT PRIMARY KEY, 
                          photo_path TEXT)''')
        self.conn.commit()

    def insert_user(self, user_data):
        """插入用户数据"""
        cursor = self.conn.cursor()
        cursor.execute(f'INSERT INTO {self.table_name} VALUES (?,?,?,?,?,?,?)', user_data)
        self.conn.commit()

    def get_all_users(self):
        """获取当前用户的所有数据"""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT name, gender, id FROM {self.table_name}')
        return cursor.fetchall()

    def search_user(self, id_number):
        """查询用户信息"""
        cursor = self.conn.cursor()
        cursor.execute(f'SELECT * FROM {self.table_name} WHERE id=?', (id_number,))
        return cursor.fetchone()

    def delete_user(self, id_number):
        """删除用户信息"""
        cursor = self.conn.cursor()
        cursor.execute(f'DELETE FROM {self.table_name} WHERE id=?', (id_number,))
        self.conn.commit()


# 主页面
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
        # self.setGeometry(300, 300, 1000, 800)
        self.setWindowIcon(QIcon('./background.jpg'))  # Windows优先使用
        self.resize(1000, 800)  # 设置窗口大小
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
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['姓名', '性别', '身份证号'])
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
        for row, (name, gender, id_num) in enumerate(data):
            # 创建单元格并设置居中
            def create_centered_item(text):
                item = QTableWidgetItem(str(text))
                item.setTextAlignment(Qt.AlignCenter)  # 设置水平和垂直居中
                return item

            self.table.setItem(row, 0, create_centered_item(name))
            self.table.setItem(row, 1, create_centered_item(gender))
            self.table.setItem(row, 2, create_centered_item(id_num))

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


# 信息录入
# 修改后的信息录入部分（改为对话框）
import os

import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap, QIcon
from PyQt5.QtWidgets import *


class EntryDialog(QDialog):
    """信息录入对话框"""

    def __init__(self, db, main_window):
        super().__init__()
        self.retry_btn = None
        self.confirm_btn = None
        self.capture_btn = None
        self.timer = None
        self.camera_label = None
        self.id_label = None
        self.adress_label = None
        self.brithday_label = None
        self.id_info_group = None
        self.nation_label = None
        self.gender_label = None
        self.name_label = None
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
        self.setFixedSize(680, 800)  # 固定对话框大小
        self.setWindowIcon(QIcon('background3.jpg'))  # Windows优先使用
        self.setWindowModality(Qt.ApplicationModal)  # 设置为模态对话框

        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # 身份证信息区域
        self.id_info_group = QGroupBox("身份证信息（模拟数据）")
        id_layout = QFormLayout()
        id_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)

        self.name_label = QLabel()
        self.gender_label = QLabel()
        self.nation_label = QLabel()
        self.brithday_label = QLabel()
        self.adress_label = QLabel()
        self.id_label = QLabel()

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
        self.retry_btn = QPushButton('🔄 重新拍摄')
        self.confirm_btn = QPushButton('✅ 确认保存')
        # 按钮风格
        self.capture_btn.setStyleSheet("font-size: 24px;font-weight: bold;")
        self.retry_btn.setStyleSheet("font-size: 24px;font-weight: bold;")
        self.confirm_btn.setStyleSheet("font-size: 24px;font-weight: bold;")
        #
        self.confirm_btn.setEnabled(False)
        self.retry_btn.setEnabled(False)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_layout.addWidget(self.retry_btn)
        btn_layout.addWidget(self.capture_btn)
        btn_layout.addWidget(self.confirm_btn)
        btn_layout.addStretch()

        # 组装界面
        main_layout.addWidget(self.id_info_group)
        main_layout.addWidget(self.camera_label)
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
                font-size: 20px;
            }
            QLabel {
                font-weight: bold;         /* 字体加粗 */
                font-size: 30px;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(240, 135, 132, 0.9);  /* 悬停颜色 */
            }
        ''')

    def read_id_card(self):
        """模拟读取身份证信息（需连接真实读卡器）"""
        self.name_label.setText("蒋成财")
        self.gender_label.setText("男")
        self.nation_label.setText("汉")
        self.brithday_label.setText("2000-01-01")
        self.adress_label.setText("北京市朝阳区")
        self.id_label.setText("500228200308297894")

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
                frame = cv2.flip(frame, 1)  # 1 表示水平翻转[^13^][^14^]
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
                frame = cv2.flip(frame, 1)  # 1 表示水平翻转[^13^][^14^]
                # 生成文件名并保存
                filename = f"{self.id_label.text()}.jpg"
                self.current_photo = os.path.join('photos', filename)
                # cv2.imwrite(self.current_photo, cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                cv2.imwrite(self.current_photo, frame)

                # 显示拍摄结果
                self.show_captured_image(frame)

                # 停止摄像头
                self.timer.stop()
                self.cap.release()
                self.cap = None

                # 启用确认按钮
                self.confirm_btn.setEnabled(True)
                self.retry_btn.setEnabled(True)

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
                    self.nation_label.text(),
                    self.brithday_label.text(),
                    self.adress_label.text(),
                    self.id_label.text(),
                    self.current_photo
                )
                self.db.insert_user(user_data)
                self.main_window.refresh_table()  # 直接刷新主窗口表格
                self.accept()  # 关闭对话框
                QMessageBox.information(self, "成功", "信息保存成功！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")

    def retry_capture(self):
        """重新拍摄"""
        self.current_photo = None
        self.confirm_btn.setEnabled(False)
        self.retry_btn.setEnabled(False)
        self.start_camera()

    def closeEvent(self, event):
        """关闭窗口时释放摄像头资源"""
        if self.cap and self.cap.isOpened():
            self.cap.release()
        super().closeEvent(event)

    def center(self):
        """将窗口居中到屏幕中心"""
        qr = self.frameGeometry()  # 获取窗口几何形状
        cp = QDesktopWidget().availableGeometry().center()  # 获取屏幕中心点
        qr.moveCenter(cp)  # 将窗口中心移动到屏幕中心
        self.move(qr.topLeft())  # 移动窗口到新位置


# 信息查询
import os
from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtGui import QPixmap, QIcon, QRegExpValidator
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
        self.setWindowIcon(QIcon('./background2.jpg'))  # Windows优先使用
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
        # 设置验证器，只允许输入18位数字
        validator = QRegExpValidator(QRegExp(r'\d{18}'))
        self.id_input.setValidator(validator)

        search_btn = QPushButton('🔍 开始查询')
        search_btn.setStyleSheet("font-size: 24px;font-weight: bold;")

        input_layout.addWidget(self.id_input)
        input_layout.addWidget(search_btn)
        layout.addLayout(input_layout)

        # 默认情况下，搜索按钮不可用
        search_btn.setEnabled(False)

        # 连接文本变化信号到槽函数
        self.id_input.textChanged.connect(lambda: self.on_input_changed(search_btn))
        search_btn.clicked.connect(self.do_search)

    def on_input_changed(self, search_btn):
        """当输入内容变化时，检查输入是否为18位数字，以决定搜索按钮是否可用"""
        if self.id_input.hasAcceptableInput():
            search_btn.setEnabled(True)
        else:
            search_btn.setEnabled(False)

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


# 运行代码
if __name__ == '__main__':
    app = QApplication(sys.argv)

    # 先显示登录对话框
    login_dialog = LoginDialog()
    if login_dialog.exec_() == QDialog.Accepted:
        # 登录成功后创建主窗口
        window = MainWindow(login_dialog.current_user_table)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(0)
#     pyinstaller --onefile --windowed id_input_demo/main.py
# pyinstaller -F -n yourAppName --icon=your_icon.ico my_script.py
