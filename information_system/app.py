import re
import sys
from PyQt5.QtWidgets import *
from login import LoginDialog
from index import MainWindow

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
