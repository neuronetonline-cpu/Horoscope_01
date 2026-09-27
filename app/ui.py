from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QTabWidget,
    QDoubleSpinBox, QGroupBox, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import QDate, QTime, Qt
from PySide6.QtGui import QFont
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

# South Indian fixed-sign 4x4 layout.
# Corners are blank; the 12 perimeter cells are the 12 Rashis.
SIGN_GRID = {
    0: (0, 0),   # Aries
    1: (0, 1),   # Taurus
    2: (0, 2),   # Gemini
    3: (0, 3),   # Cancer
    4: (1, 3),   # Leo
    5: (2, 3),   # Virgo
    6: (3, 3),   # Libra
    7: (3, 2),   # Scorpio
    8: (3, 1),   # Sagittarius
    9: (3, 0),   # Capricorn
    10: (2, 0),  # Aquarius
    11: (1, 0),  # Pisces
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Sri Lanka Horoscope — Phase 2 Fixed")
        self.resize(1280, 860)
        self.build_ui()
        self.refresh_search()

    def build_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.new_horoscope_tab(), "නව කේන්දරය / New Horoscope")
        tabs.addTab(self.chart_tab(), "කේන්දරය / D1 Chart")
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

        self.result = QTableWidget(0, 7)
        self.result.setHorizontalHeaderLabels([
            "Planet", "Longitude°", "Sign", "House",
            "Nakshatra", "Pada", "Speed°/day"
        ])
        self.result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.result.verticalHeader().setDefaultSectionSize(30)

        self.asc_label = QLabel("Lagna / Ascendant: -")
        self.moon_label = QLabel("Moon Nakshatra: -")

        outer.addWidget(box)
        outer.addLayout(buttons)
        outer.addWidget(self.asc_label)
        outer.addWidget(self.moon_label)
        outer.addWidget(QLabel("Sidereal planetary positions — Lahiri"))
        outer.addWidget(self.result)
        return w

    def chart_tab(self):
        w = QWidget()
        layout = QVBoxLayout(w)

        self.chart_title = QLabel("D1 / Rashi Chart — Calculate a horoscope first")
        self.chart_title.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        self.chart_title.setFont(title_font)

        self.chart_grid = QTableWidget(4, 4)
        self.chart_grid.horizontalHeader().setVisible(False)
        self.chart_grid.verticalHeader().setVisible(False)
        self.chart_grid.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.chart_grid.setSelectionMode(QAbstractItemView.NoSelection)
        self.chart_grid.setMinimumHeight(500)
        self.chart_grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.chart_grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Proper South Indian chart has 12 perimeter cells and 4 blank corners.
        for r in range(4):
            for c in range(4):
                item = QTableWidgetItem("")
                item.setTextAlignment(Qt.AlignCenter)
                self.chart_grid.setItem(r, c, item)

        layout.addWidget(self.chart_title)
        layout.addWidget(self.chart_grid)

        layout.addWidget(QLabel("Whole-sign Houses"))
        self.house_table = QTableWidget(0, 5)
        self.house_table.setHorizontalHeaderLabels([
            "House", "Sign", "Lord", "Planets", "Sign Degree Range"
        ])
        self.house_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.house_table.verticalHeader().setDefaultSectionSize(28)
        self.house_table.setMinimumHeight(350)
        layout.addWidget(self.house_table)

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
        self.saved.setHorizontalHeaderLabels([
            "ID", "Name", "Gender", "Birth Date",
            "Birth Time", "Place", "UTC"
        ])
        self.saved.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
                self.tz.text().strip()
            )

            self.utc_preview.setText(
                chart["utc"].strftime("%Y-%m-%d %H:%M:%S UTC")
            )
            self.jd_preview.setText(f'{chart["jd_ut"]:.8f}')

            a = chart["asc_sign"]
            nak = chart["asc_nakshatra"]
            self.asc_label.setText(
                f'Lagna: {a["sinhala"]} / {a["english"]} — '
                f'{chart["ascendant"]:.8f}° | Lord: {a["lord"]} | '
                f'Nakshatra: {nak["sinhala"]} ({nak["name"]}) Pada {nak["pada"]}'
            )

            moon = next(p for p in chart["planets"] if p["name"] == "Moon")
            self.moon_label.setText(
                f'Moon Nakshatra: {moon["nakshatra"]["sinhala"]} '
                f'({moon["nakshatra"]["name"]}) — Pada {moon["nakshatra"]["pada"]} — '
                f'Lord: {moon["nakshatra"]["lord"]}'
            )

            self.result.setRowCount(0)
            for p in chart["planets"]:
                r = self.result.rowCount()
                self.result.insertRow(r)
                values = [
                    p["name"],
                    f'{p["longitude"]:.6f}',
                    f'{p["sign"]["sinhala"]} / {p["sign"]["english"]}',
                    str(p["house"]),
                    f'{p["nakshatra"]["sinhala"]} / {p["nakshatra"]["name"]}',
                    str(p["nakshatra"]["pada"]),
                    f'{p["speed"]:.6f}',
                ]
                for c, value in enumerate(values):
                    item = QTableWidgetItem(value)
                    item.setTextAlignment(Qt.AlignCenter)
                    self.result.setItem(r, c, item)

            self.last_chart = chart
            self.update_chart()

        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", str(e))

    def update_chart(self):
        chart = self.last_chart

        self.chart_title.setText(
            f'D1 / Rashi Chart — {self.name.text().strip() or "Horoscope"} — '
            f'Lagna: {chart["asc_sign"]["sinhala"]} / {chart["asc_sign"]["english"]}'
        )

        # Group planets by fixed zodiac sign.
        by_sign = {i: [] for i in range(12)}
        for p in chart["planets"]:
            by_sign[p["sign"]["index"]].append(p["name"])

        # Fill the 12 perimeter cells; keep the 4 corners blank.
        for sign_index, (row, col) in SIGN_GRID.items():
            sign = chart["houses"][((sign_index - chart["asc_sign"]["index"]) % 12)]
            # sign metadata from fixed sign index
            from .astro import SIGNS
            fixed = SIGNS[sign_index]

            lines = [
                f'{fixed[1]}',
                f'{fixed[2]}'
            ]

            if sign_index == chart["asc_sign"]["index"]:
                lines.append("LAGNA")

            if by_sign[sign_index]:
                lines.append(" / ".join(by_sign[sign_index]))

            item = QTableWidgetItem("\n".join(lines))
            item.setTextAlignment(Qt.AlignCenter)
            font = item.font()
            font.setPointSize(10)
            item.setFont(font)
            self.chart_grid.setItem(row, col, item)

        # Keep four corner cells genuinely blank.
        for row, col in [(0, 0), (0, 3), (3, 0), (3, 3)]:
            item = QTableWidgetItem("")
            self.chart_grid.setItem(row, col, item)

        self.house_table.setRowCount(0)
        for h in chart["houses"]:
            r = self.house_table.rowCount()
            self.house_table.insertRow(r)
            values = [
                str(h["house"]),
                f'{h["sinhala"]} / {h["english"]}',
                h["lord"],
                ", ".join(h["planets"]) or "-",
                "0°–30°",
            ]
            for c, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignCenter)
                self.house_table.setItem(r, c, item)

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

        term = self.search.text() if hasattr(self, "search") else ""
        rows = search_horoscopes(term)

        self.saved.setRowCount(0)
        for row in rows:
            r = self.saved.rowCount()
            self.saved.insertRow(r)
            values = [
                row["id"], row["name"], row["gender"],
                row["birth_date"], row["birth_time"],
                row["birth_place"], row["utc_time"]
            ]
            for c, value in enumerate(values):
                self.saved.setItem(r, c, QTableWidgetItem(str(value or "")))

    def clear_form(self):
        self.name.clear()
        self.gender.setCurrentIndex(0)
        self.place.setCurrentText("Colombo")
        self.place_changed("Colombo")

        self.result.setRowCount(0)
        self.asc_label.setText("Lagna / Ascendant: -")
        self.moon_label.setText("Moon Nakshatra: -")
        self.utc_preview.setText("-")
        self.jd_preview.setText("-")

        self.chart_title.setText("D1 / Rashi Chart — Calculate a horoscope first")
        self.house_table.setRowCount(0)

        for r in range(4):
            for c in range(4):
                self.chart_grid.setItem(r, c, QTableWidgetItem(""))

        if hasattr(self, "last_chart"):
            del self.last_chart
