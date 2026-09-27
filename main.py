import sys
from PySide6.QtWidgets import QApplication
from app.ui import MainWindow

app = QApplication(sys.argv)
app.setApplicationName("Sri Lanka Horoscope")
window = MainWindow()
window.show()
sys.exit(app.exec())
