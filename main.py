import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from app.ui import MainWindow

app = QApplication(sys.argv)
app.setApplicationName("Sri Lanka Horoscope")
app.setFont(QFont("Noto Sans Sinhala", 10))
w = MainWindow()
w.show()
sys.exit(app.exec())
