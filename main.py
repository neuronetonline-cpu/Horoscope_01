import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont

from app.ui import MainWindow

app = QApplication(sys.argv)
app.setApplicationName("Sri Lanka Horoscope")

# Prefer a Sinhala-capable font when installed; Qt will fall back if unavailable.
app.setFont(QFont("Noto Sans Sinhala", 10))

window = MainWindow()
window.show()
sys.exit(app.exec())
