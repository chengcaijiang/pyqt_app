import sys
from PyQt5.QtWidgets import *
from 主界面 import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
#     pyinstaller --onefile --windowed id_input_demo/main.py
