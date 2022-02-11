from PyQt5.QtWidgets import QApplication
import sys
from mainwindow import MainWindow

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("QLabel{font-size: 18pt;}\n\
                        QListView{font-size: 18pt;}\n\
                        QButton{font-size: 18pt;}")
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
