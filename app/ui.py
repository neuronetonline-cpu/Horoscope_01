from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QTabWidget,
    QDoubleSpinBox, QGroupBox
)
from PySide6.QtCore import QDate, QTime
from .db import init_db, add_horoscope, search_horoscopes
from .astro import calculate_chart

PLACES = {
    "Colombo": (6.9271, 79.8612),
    "Kandy": (7.2906, 80.6337),
    "Galle": (6.0329, 80.2168),
    "Matara": (5.9549, 80.5550),
    "Negombo": (7.2083, 79.8358),
    "Kurunegala": (7.4863, 80.3623),
    "Jaffna": (9.6615, 80.0255),
    "Batticaloa": (7.7310, 81.6747),
    "Anuradhapura": (8.3114, 80.4037),
    "Ratnapura": (6.6828, 80.3992),
    "Badulla": (6.9934, 81.0550),
    "Nuwara Eliya": (6.9497, 80.7891),
    "Maharagama": (6.8494, 79.9265),
    "Battaramulla": (6.8964, 79.9181),
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Sri Lanka Horoscope — Phase 1")
        self.resize(1120, 760)
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
        self.place = QComboBox()
        self.place.setEditable(True)
        self.place.addItems(list(PLACES.keys()))
        self.place.currentTextChanged.connect(self.place_changed)
        self.lat = QDoubleSpinBox()
        self.lat.setRange(-90, 90)
        self.lat.setDecimals(6)
        self.lon = QDoubleSpinBox()
        self.lon.setRange(-180, 180)
        self.lon.setDecimals(6)
        self.tz = QLineEdit("Asia/Colombo")
        self.utc_preview = QLabel("-")
        self.jd_preview = QLabel("-")

        for label, widget in [
            ("නම / Name", self.name),
            ("ස්ත්‍රී/පුරුෂ / Gender", self.gender),
            ("උපන් දිනය / Date", self.date),
            ("උපන් වේලාව / Local Time", self.time),
            ("උපන් ස්ථානය / Place", self.place),
            ("Latitude", self.lat),
            ("Longitude", self.lon),
            ("Timezone", self.tz),
            ("UTC verification", self.utc_preview),
            ("Julian Day (UT)", self.jd_preview),
        ]:
            form.addRow(label, widget)

        self.place_changed(self.place.currentText())

        buttons = QHBoxLayout()
        for text, slot in [
            ("Calculate Horoscope", self.calculate),
            ("Save", self.save),
            ("Clear", self.clear_form),
        ]:
            b = QPushButton(text)
            b.clicked.connect(slot)
            buttons.addWidget(b)
        buttons.addStretch()

        self.result = QTableWidget(0, 4)
        self.result.setHorizontalHeaderLabels(
            ["Planet", "Sidereal Longitude°", "Latitude°", "Speed°/day"]
        )
        self.asc_label = QLabel("Lagna / Ascendant: -")

        outer.addWidget(box)
        outer.addLayout(buttons)
        outer.addWidget(self.asc_label)
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
        self.saved = QTableWidget(0, 7)
        self.saved.setHorizontalHeaderLabels(
            ["ID", "Name", "Gender", "Birth Date", "Birth Time", "Place", "UTC"]
        )
        layout.addLayout(row)
        layout.addWidget(self.saved)
        return w

    def place_changed(self, name):
        if name in PLACES:
            lat, lon = PLACES[name]
            self.lat.setValue(lat)
            self.lon.setValue(lon)

    def calculate(self):
        try:
            d = self.date.date()
            t = self.time.time()
            chart = calculate_chart(
                d.toString("yyyy-MM-dd"),
                t.toString("HH:mm:ss"),
                self.lat.value(),
                self.lon.value(),
                self.tz.text().strip(),
            )
            self.utc_preview.setText(
                chart["utc"].strftime("%Y-%m-%d %H:%M:%S UTC")
            )
            self.jd_preview.setText(f'{chart["jd_ut"]:.8f}')
            self.asc_label.setText(
                f'Lagna / Ascendant longitude: {chart["ascendant"]:.8f}°'
            )
            self.result.setRowCount(0)
            for p in chart["planets"]:
                r = self.result.rowCount()
                self.result.insertRow(r)
                for c, v in enumerate([
                    p["name"],
                    f'{p["longitude"]:.8f}',
                    f'{p["latitude"]:.8f}',
                    f'{p["speed"]:.8f}',
                ]):
                    self.result.setItem(r, c, QTableWidgetItem(v))
            self.last_chart = chart
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", str(e))

    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Required", "Name is required.")
            return
        if not hasattr(self, "last_chart"):
            self.calculate()
            if not hasattr(self, "last_chart"):
                return
        d = self.date.date()
        t = self.time.time()
        chart = self.last_chart
        add_horoscope({
            "name": self.name.text().strip(),
            "gender": self.gender.currentText(),
            "birth_date": d.toString("yyyy-MM-dd"),
            "birth_time": t.toString("HH:mm:ss"),
            "birth_place": self.place.currentText().strip(),
            "latitude": self.lat.value(),
            "longitude": self.lon.value(),
            "timezone": self.tz.text().strip(),
            "utc_time": chart["utc"].strftime("%Y-%m-%d %H:%M:%S UTC"),
            "julian_day": chart["jd_ut"],
        })
        self.refresh_search()
        QMessageBox.information(self, "Saved", "Horoscope saved.")

    def refresh_search(self):
        if not hasattr(self, "saved"):
            return
        rows = search_horoscopes(
            self.search.text() if hasattr(self, "search") else ""
        )
        self.saved.setRowCount(0)
        for row in rows:
            r = self.saved.rowCount()
            self.saved.insertRow(r)
            vals = [
                row["id"], row["name"], row["gender"],
                row["birth_date"], row["birth_time"],
                row["birth_place"], row["utc_time"]
            ]
            for c, v in enumerate(vals):
                self.saved.setItem(r, c, QTableWidgetItem(str(v or "")))

    def clear_form(self):
        self.name.clear()
        self.gender.setCurrentIndex(0)
        self.place.setCurrentText("Colombo")
        self.place_changed("Colombo")
        self.result.setRowCount(0)
        self.asc_label.setText("Lagna / Ascendant: -")
        self.utc_preview.setText("-")
        self.jd_preview.setText("-")
        if hasattr(self, "last_chart"):
            del self.last_chart
