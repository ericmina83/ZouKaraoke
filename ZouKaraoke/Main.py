from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QFont
import sys

from ZouKaraoke.MainWindow import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setFont(QFont("Times", 18))
    # app.setStyleSheet("QComboBox{font-size: 18pt;}\n\
    #                     QLabel{font-size: 18pt;}\n\
    #                     QListView{font-size: 18pt;}\n\
    #                     QButton{font-size: 18pt;}")
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
