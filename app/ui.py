from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QDateEdit, QTimeEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QTabWidget,
    QDoubleSpinBox, QGroupBox, QHeaderView
)
from PySide6.QtCore import QDate, QTime, Qt
from .db import init_db, add_horoscope, search_horoscopes
from .astro import calculate_chart

PLACES = {
    "Colombo": (6.9271, 79.8612), "Kandy": (7.2906, 80.6337),
    "Galle": (6.0329, 80.2168), "Matara": (5.9549, 80.5550),
    "Negombo": (7.2083, 79.8358), "Kurunegala": (7.4863, 80.3623),
    "Jaffna": (9.6615, 80.0255), "Batticaloa": (7.7310, 81.6747),
    "Anuradhapura": (8.3114, 80.4037), "Ratnapura": (6.6828, 80.3992),
    "Badulla": (6.9934, 81.0550), "Nuwara Eliya": (6.9497, 80.7891),
    "Maharagama": (6.8494, 79.9265), "Battaramulla": (6.8964, 79.9181),
}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        init_db()
        self.setWindowTitle("Sri Lanka Horoscope — Phase 2")
        self.resize(1250, 820)
        self.build_ui()
        self.refresh_search()

    def build_ui(self):
        tabs = QTabWidget()
        tabs.addTab(self.new_horoscope_tab(), "නව කේන්දරය / New Horoscope")
        tabs.addTab(self.chart_tab(), "කේන්දරය / D1 Chart")
        tabs.addTab(self.saved_tab(), "සුරැකි කේන්දර / Saved")
        self.setCentralWidget(tabs)

    def new_horoscope_tab(self):
        w = QWidget(); outer = QVBoxLayout(w)
        box = QGroupBox("උපන් විස්තර / Birth Details"); form = QFormLayout(box)
        self.name = QLineEdit()
        self.gender = QComboBox(); self.gender.addItems(["", "Male / පුරුෂ", "Female / ස්ත්‍රී"])
        self.date = QDateEdit(QDate.currentDate()); self.date.setCalendarPopup(True)
        self.time = QTimeEdit(QTime(12, 0)); self.time.setDisplayFormat("HH:mm:ss")
        self.place = QComboBox(); self.place.setEditable(True); self.place.addItems(list(PLACES.keys()))
        self.place.currentTextChanged.connect(self.place_changed)
        self.lat = QDoubleSpinBox(); self.lat.setRange(-90,90); self.lat.setDecimals(6)
        self.lon = QDoubleSpinBox(); self.lon.setRange(-180,180); self.lon.setDecimals(6)
        self.tz = QLineEdit("Asia/Colombo")
        self.utc_preview = QLabel("-"); self.jd_preview = QLabel("-")
        for label, widget in [
            ("නම / Name", self.name), ("ස්ත්‍රී/පුරුෂ / Gender", self.gender),
            ("උපන් දිනය / Date", self.date), ("උපන් වේලාව / Local Time", self.time),
            ("උපන් ස්ථානය / Place", self.place), ("Latitude", self.lat),
            ("Longitude", self.lon), ("Timezone", self.tz),
            ("UTC verification", self.utc_preview), ("Julian Day (UT)", self.jd_preview)
        ]: form.addRow(label, widget)
        self.place_changed(self.place.currentText())

        buttons = QHBoxLayout()
        for text, slot in [("Calculate Horoscope", self.calculate), ("Save", self.save), ("Clear", self.clear_form)]:
            b = QPushButton(text); b.clicked.connect(slot); buttons.addWidget(b)
        buttons.addStretch()

        self.result = QTableWidget(0, 7)
        self.result.setHorizontalHeaderLabels(
            ["Planet","Longitude°","Sign","House","Nakshatra","Pada","Speed°/day"]
        )
        self.result.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.asc_label = QLabel("Lagna / Ascendant: -")
        self.moon_label = QLabel("Moon Nakshatra: -")

        outer.addWidget(box); outer.addLayout(buttons)
        outer.addWidget(self.asc_label); outer.addWidget(self.moon_label)
        outer.addWidget(QLabel("Sidereal planetary positions — Lahiri"))
        outer.addWidget(self.result)
        return w

    def chart_tab(self):
        w = QWidget(); layout = QVBoxLayout(w)
        self.chart_title = QLabel("D1 / Rashi Chart — Calculate a horoscope first")
        self.chart_title.setAlignment(Qt.AlignCenter)
        self.chart_grid = QTableWidget(4, 4)
        self.chart_grid.horizontalHeader().setVisible(False)
        self.chart_grid.verticalHeader().setVisible(False)
        self.chart_grid.setEditTriggers(QTableWidget.NoEditTriggers)
        self.chart_grid.setMinimumHeight(420)
        self.chart_grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.chart_grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.chart_title); layout.addWidget(self.chart_grid)

        self.house_table = QTableWidget(0, 5)
        self.house_table.setHorizontalHeaderLabels(["House","Sign","Lord","Planets","Sign Degree Range"])
        self.house_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(QLabel("Whole-sign Houses"))
        layout.addWidget(self.house_table)
        return w

    def saved_tab(self):
        w = QWidget(); layout = QVBoxLayout(w); row = QHBoxLayout()
        self.search = QLineEdit(); self.search.setPlaceholderText("Search name or birth place...")
        btn = QPushButton("Search"); btn.clicked.connect(self.refresh_search)
        row.addWidget(self.search); row.addWidget(btn)
        self.saved = QTableWidget(0,7)
        self.saved.setHorizontalHeaderLabels(["ID","Name","Gender","Birth Date","Birth Time","Place","UTC"])
        self.saved.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addLayout(row); layout.addWidget(self.saved)
        return w

    def place_changed(self, name):
        if name in PLACES:
            lat, lon = PLACES[name]; self.lat.setValue(lat); self.lon.setValue(lon)

    def calculate(self):
        try:
            d = self.date.date(); t = self.time.time()
            chart = calculate_chart(
                d.toString("yyyy-MM-dd"), t.toString("HH:mm:ss"),
                self.lat.value(), self.lon.value(), self.tz.text().strip()
            )
            self.utc_preview.setText(chart["utc"].strftime("%Y-%m-%d %H:%M:%S UTC"))
            self.jd_preview.setText(f'{chart["jd_ut"]:.8f}')
            a = chart["asc_sign"]
            self.asc_label.setText(
                f'Lagna: {a["sinhala"]} / {a["english"]} — '
                f'{chart["ascendant"]:.8f}° | Lord: {a["lord"]} | '
                f'Nakshatra: {chart["asc_nakshatra"]["sinhala"]} '
                f'({chart["asc_nakshatra"]["name"]}) Pada {chart["asc_nakshatra"]["pada"]}'
            )
            moon = next(p for p in chart["planets"] if p["name"] == "Moon")
            self.moon_label.setText(
                f'Moon Nakshatra: {moon["nakshatra"]["sinhala"]} '
                f'({moon["nakshatra"]["name"]}) — Pada {moon["nakshatra"]["pada"]} — '
                f'Lord: {moon["nakshatra"]["lord"]}'
            )

            self.result.setRowCount(0)
            for p in chart["planets"]:
                r = self.result.rowCount(); self.result.insertRow(r)
                vals = [
                    p["name"], f'{p["longitude"]:.6f}',
                    f'{p["sign"]["sinhala"]} / {p["sign"]["english"]}',
                    str(p["house"]),
                    f'{p["nakshatra"]["sinhala"]} / {p["nakshatra"]["name"]}',
                    str(p["nakshatra"]["pada"]),
                    f'{p["speed"]:.6f}'
                ]
                for c,v in enumerate(vals): self.result.setItem(r,c,QTableWidgetItem(v))

            self.last_chart = chart
            self.update_chart()
        except Exception as e:
            QMessageBox.critical(self, "Calculation Error", str(e))

    def update_chart(self):
        chart = self.last_chart
        self.chart_title.setText(
            f'D1 / Rashi Chart — {self.name.text().strip() or "Horoscope"} — '
            f'Lagna {chart["asc_sign"]["sinhala"]}'
        )
        # South Indian style: fixed signs, planets move by sign.
        positions = [None]*12
        for p in chart["planets"]:
            positions[p["sign"]["index"]] = (
                (positions[p["sign"]["index"]] + "\n" if positions[p["sign"]["index"]] else "")
                + p["name"]
            )
        for idx in range(12):
            sign = chart["houses"][((idx - chart["asc_sign"]["index"]) % 12)]
            text = f'{sign["sinhala"]}\n{sign["english"]}\n'
            if idx == chart["asc_sign"]["index"]:
                text += "LAGNA\n"
            text += positions[idx] or ""
            self.chart_grid.setItem(idx // 4, idx % 4, QTableWidgetItem(text))

        self.house_table.setRowCount(0)
        for h in chart["houses"]:
            r = self.house_table.rowCount(); self.house_table.insertRow(r)
            vals = [
                str(h["house"]), f'{h["sinhala"]} / {h["english"]}',
                h["lord"], ", ".join(h["planets"]) or "-",
                "0°–30°"
            ]
            for c,v in enumerate(vals): self.house_table.setItem(r,c,QTableWidgetItem(v))

    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Required", "Name is required."); return
        if not hasattr(self, "last_chart"):
            self.calculate()
            if not hasattr(self, "last_chart"): return
        d = self.date.date(); t = self.time.time(); chart = self.last_chart
        add_horoscope({
            "name": self.name.text().strip(), "gender": self.gender.currentText(),
            "birth_date": d.toString("yyyy-MM-dd"), "birth_time": t.toString("HH:mm:ss"),
            "birth_place": self.place.currentText().strip(), "latitude": self.lat.value(),
            "longitude": self.lon.value(), "timezone": self.tz.text().strip(),
            "utc_time": chart["utc"].strftime("%Y-%m-%d %H:%M:%S UTC"),
            "julian_day": chart["jd_ut"],
        })
        self.refresh_search(); QMessageBox.information(self, "Saved", "Horoscope saved.")

    def refresh_search(self):
        if not hasattr(self, "saved"): return
        rows = search_horoscopes(self.search.text() if hasattr(self,"search") else "")
        self.saved.setRowCount(0)
        for row in rows:
            r = self.saved.rowCount(); self.saved.insertRow(r)
            vals = [row["id"],row["name"],row["gender"],row["birth_date"],
                    row["birth_time"],row["birth_place"],row["utc_time"]]
            for c,v in enumerate(vals): self.saved.setItem(r,c,QTableWidgetItem(str(v or "")))

    def clear_form(self):
        self.name.clear(); self.gender.setCurrentIndex(0)
        self.place.setCurrentText("Colombo"); self.place_changed("Colombo")
        self.result.setRowCount(0); self.asc_label.setText("Lagna / Ascendant: -")
        self.moon_label.setText("Moon Nakshatra: -")
        self.utc_preview.setText("-"); self.jd_preview.setText("-")
        self.chart_title.setText("D1 / Rashi Chart — Calculate a horoscope first")
        self.house_table.setRowCount(0)
        for r in range(4):
            for c in range(4):
                self.chart_grid.setItem(r,c,QTableWidgetItem(""))
        if hasattr(self,"last_chart"): del self.last_chart
