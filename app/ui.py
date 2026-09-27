from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QTabWidget,
    QDoubleSpinBox, QGroupBox
)
from PySide6.QtCore import QDate, QTime
from .db import init_db, add_horoscope, search_horoscopes
from .astro import calculate_planets

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Sri Lanka Horoscope — V1")
        self.resize(1100, 720)
        self.build_ui()
        self.refresh_search()

    def build_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.new_horoscope_tab(), "නව කේන්දරය / New Horoscope")
        tabs.addTab(self.saved_tab(), "සුරැකි කේන්දර / Saved")
        self.setCentralWidget(tabs)

    def new_horoscope_tab(self):
        w = QWidget()
        outer = QVBoxLayout(w)

        box = QGroupBox("උපන් විස්තර / Birth Details")
        form = QFormLayout(box)

        self.name = QLineEdit()
        self.gender = QComboBox()
        self.gender.addItems(["", "Male / පුරුෂ", "Female / ස්ත්‍රී"])

        self.date = QDateEdit(QDate.currentDate())
        self.date.setCalendarPopup(True)
        self.time = QTimeEdit(QTime(12, 0))
        self.time.setDisplayFormat("HH:mm:ss")

        self.place = QLineEdit()
        self.lat = QDoubleSpinBox()
        self.lat.setRange(-90, 90)
        self.lat.setDecimals(6)
        self.lon = QDoubleSpinBox()
        self.lon.setRange(-180, 180)
        self.lon.setDecimals(6)

        self.tz = QLineEdit("Asia/Colombo")

        form.addRow("නම / Name", self.name)
        form.addRow("ස්ත්‍රී/පුරුෂ / Gender", self.gender)
        form.addRow("උපන් දිනය / Date", self.date)
        form.addRow("උපන් වේලාව / Time", self.time)
        form.addRow("උපන් ස්ථානය / Place", self.place)
        form.addRow("Latitude", self.lat)
        form.addRow("Longitude", self.lon)
        form.addRow("Timezone", self.tz)

        buttons = QHBoxLayout()
        save = QPushButton("Save & Calculate")
        clear = QPushButton("Clear")
        save.clicked.connect(self.save_and_calculate)
        clear.clicked.connect(self.clear_form)
        buttons.addWidget(save)
        buttons.addWidget(clear)
        buttons.addStretch()

        self.result = QTableWidget(0, 4)
        self.result.setHorizontalHeaderLabels(["Planet", "Longitude°", "Latitude°", "Speed"])

        outer.addWidget(box)
        outer.addLayout(buttons)
        outer.addWidget(QLabel("Sidereal planetary positions — Lahiri"))
        outer.addWidget(self.result)
        return w

    def saved_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)
        row = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search name or birth place...")
        btn = QPushButton("Search")
        btn.clicked.connect(self.refresh_search)
        row.addWidget(self.search)
        row.addWidget(btn)

        self.saved = QTableWidget(0, 6)
        self.saved.setHorizontalHeaderLabels(
            ["ID", "Name", "Gender", "Birth Date", "Birth Time", "Place"]
        )
        layout.addLayout(row)
        layout.addWidget(self.saved)
        return w

    def save_and_calculate(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Required", "Name is required.")
            return

        d = self.date.date()
        t = self.time.time()
        hour_decimal = t.hour() + t.minute()/60 + t.second()/3600

        try:
            planets = calculate_planets(d.year(), d.month(), d.day(), hour_decimal)
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", str(e))
            return

        data = {
            "name": self.name.text().strip(),
            "gender": self.gender.currentText(),
            "birth_date": d.toString("yyyy-MM-dd"),
            "birth_time": t.toString("HH:mm:ss"),
            "birth_place": self.place.text().strip(),
            "latitude": self.lat.value(),
            "longitude": self.lon.value(),
            "timezone": self.tz.text().strip(),
        }
        add_horoscope(data)

        self.result.setRowCount(0)
        for p in planets:
            r = self.result.rowCount()
            self.result.insertRow(r)
            self.result.setItem(r, 0, QTableWidgetItem(p["name"]))
            self.result.setItem(r, 1, QTableWidgetItem(f'{p["longitude"]:.6f}'))
            self.result.setItem(r, 2, QTableWidgetItem(f'{p["latitude"]:.6f}'))
            self.result.setItem(r, 3, QTableWidgetItem(f'{p["speed"]:.6f}'))

        self.refresh_search()
        QMessageBox.information(self, "Saved", "Horoscope saved and calculated.")

    def refresh_search(self):
        if not hasattr(self, "saved"):
            return
        rows = search_horoscopes(self.search.text() if hasattr(self, "search") else "")
        self.saved.setRowCount(0)
        for row in rows:
            r = self.saved.rowCount()
            self.saved.insertRow(r)
            vals = [row["id"], row["name"], row["gender"], row["birth_date"], row["birth_time"], row["birth_place"]]
            for c, v in enumerate(vals):
                self.saved.setItem(r, c, QTableWidgetItem(str(v or "")))

    def clear_form(self):
        self.name.clear()
        self.gender.setCurrentIndex(0)
        self.place.clear()
        self.lat.setValue(0)
        self.lon.setValue(0)
        self.result.setRowCount(0)
