from PySide6.QtWidgets import *
from PySide6.QtCore import QDate,QTime,Qt
from PySide6.QtGui import QFont
from .db import init_db,add_horoscope,search_horoscopes
from .astro import calculate,SIGNS,current_dasha

PLACES={"Colombo":(6.9271,79.8612),"Kandy":(7.2906,80.6337),"Galle":(6.0329,80.2168),
"Matara":(5.9549,80.5550),"Negombo":(7.2083,79.8358),"Kurunegala":(7.4863,80.3623),
"Jaffna":(9.6615,80.0255),"Batticaloa":(7.7310,81.6747),"Anuradhapura":(8.3114,80.4037),
"Ratnapura":(6.6828,80.3992),"Badulla":(6.9934,81.0550),"Nuwara Eliya":(6.9497,80.7891),
"Maharagama":(6.8494,79.9265),"Battaramulla":(6.8964,79.9181)}
GRID={0:(0,0),1:(0,1),2:(0,2),3:(0,3),4:(1,3),5:(2,3),6:(3,3),7:(3,2),8:(3,1),9:(3,0),10:(2,0),11:(1,0)}

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); init_db(); self.setWindowTitle("Sri Lanka Horoscope — Phase 3"); self.resize(1350,900); self.ui()
    def ui(self):
        t=QTabWidget()
        t.addTab(self.new_tab(),"නව කේන්දරය / New Horoscope"); t.addTab(self.d1_tab(),"කේන්දරය / D1 Chart")
        t.addTab(self.d9_tab(),"නවාංශය / D9"); t.addTab(self.dasha_tab(),"දශා / Vimshottari Dasha")
        t.addTab(self.saved_tab(),"සුරැකි කේන්දර / Saved"); self.setCentralWidget(t)
    def new_tab(self):
        w=QWidget(); o=QVBoxLayout(w); g=QGroupBox("උපන් විස්තර / Birth Details"); f=QFormLayout(g)
        self.name=QLineEdit(); self.gender=QComboBox(); self.gender.addItems(["","Male / පුරුෂ","Female / ස්ත්‍රී"])
        self.date=QDateEdit(QDate.currentDate()); self.date.setCalendarPopup(True)
        self.time=QTimeEdit(QTime(12,0)); self.time.setDisplayFormat("HH:mm:ss")
        self.place=QComboBox(); self.place.setEditable(True); self.place.addItems(PLACES); self.place.currentTextChanged.connect(self.place_change)
        self.lat=QDoubleSpinBox(); self.lat.setRange(-90,90); self.lat.setDecimals(6)
        self.lon=QDoubleSpinBox(); self.lon.setRange(-180,180); self.lon.setDecimals(6)
        self.tz=QLineEdit("Asia/Colombo"); self.utc=QLabel("-"); self.jd=QLabel("-")
        for a,b in [("නම / Name",self.name),("ස්ත්‍රී/පුරුෂ / Gender",self.gender),("උපන් දිනය / Date",self.date),
                    ("උපන් වේලාව / Local Time",self.time),("උපන් ස්ථානය / Place",self.place),("Latitude",self.lat),
                    ("Longitude",self.lon),("Timezone",self.tz),("UTC verification",self.utc),("Julian Day (UT)",self.jd)]: f.addRow(a,b)
        self.place_change(self.place.currentText())
        r=QHBoxLayout()
        for s,fn in [("Calculate Horoscope",self.calc),("Save",self.save),("Clear",self.clear)]: b=QPushButton(s); b.clicked.connect(fn); r.addWidget(b)
        r.addStretch()
        self.asc=QLabel("Lagna / Ascendant: -"); self.moon=QLabel("Moon Nakshatra: -"); self.cur=QLabel("Current Dasha: -")
        self.tbl=QTableWidget(0,8); self.tbl.setHorizontalHeaderLabels(["Planet","Longitude°","Sign","House","Nakshatra","Pada","D9 / Navamsa","Speed°/day"]); self.tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        o.addWidget(g); o.addLayout(r); o.addWidget(self.asc); o.addWidget(self.moon); o.addWidget(self.cur); o.addWidget(self.tbl); return w
    def base_chart(self,title):
        w=QWidget(); o=QVBoxLayout(w); lab=QLabel(title); lab.setAlignment(Qt.AlignCenter); q=QFont(); q.setBold(True); q.setPointSize(12); lab.setFont(q)
        grid=QTableWidget(4,4); grid.horizontalHeader().setVisible(False); grid.verticalHeader().setVisible(False); grid.setEditTriggers(QAbstractItemView.NoEditTriggers); grid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); grid.verticalHeader().setSectionResizeMode(QHeaderView.Stretch); grid.setMinimumHeight(480)
        o.addWidget(lab); o.addWidget(grid); return w,lab,grid
    def d1_tab(self):
        w,l,g=self.base_chart("D1 / Rashi Chart — Calculate a horoscope first"); self.d1title=l; self.d1grid=g
        self.houses=QTableWidget(0,5); self.houses.setHorizontalHeaderLabels(["House","Sign","Lord","Planets","Range"]); self.houses.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); w.layout().addWidget(QLabel("Whole-sign Houses")); w.layout().addWidget(self.houses); return w
    def d9_tab(self):
        w,l,g=self.base_chart("D9 / Navamsa Chart — Calculate a horoscope first"); self.d9title=l; self.d9grid=g
        self.d9tbl=QTableWidget(0,5); self.d9tbl.setHorizontalHeaderLabels(["Planet","D1 Rashi","D9 Rashi","Navamsa No.","D9 Lord"]); self.d9tbl.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); w.layout().addWidget(QLabel("Navamsa Planet Placements")); w.layout().addWidget(self.d9tbl); return w
    def dasha_tab(self):
        w=QWidget(); o=QVBoxLayout(w); self.dsummary=QLabel("Vimshottari Dasha — Calculate a horoscope first"); self.dsummary.setWordWrap(True); o.addWidget(self.dsummary)
        self.md=QTableWidget(0,4); self.md.setHorizontalHeaderLabels(["Mahadasha","Start","End","Years"]); self.md.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); o.addWidget(QLabel("Mahadasha")); o.addWidget(self.md)
        self.ad=QTableWidget(0,5); self.ad.setHorizontalHeaderLabels(["Mahadasha","Antardasha","Start","End","Years"]); self.ad.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); o.addWidget(QLabel("Antardasha")); o.addWidget(self.ad); return w
    def saved_tab(self):
        w=QWidget(); o=QVBoxLayout(w); r=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Search name or birth place..."); b=QPushButton("Search"); b.clicked.connect(self.refresh); r.addWidget(self.search); r.addWidget(b)
        self.saved=QTableWidget(0,7); self.saved.setHorizontalHeaderLabels(["ID","Name","Gender","Birth Date","Birth Time","Place","UTC"]); self.saved.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); o.addLayout(r); o.addWidget(self.saved); return w
    def place_change(self,x):
        if x in PLACES: self.lat.setValue(PLACES[x][0]); self.lon.setValue(PLACES[x][1])
    def calc(self):
        try:
            d=self.date.date().toString("yyyy-MM-dd"); ts=self.time.time().toString("HH:mm:ss")
            self.c=calculate(d,ts,self.lat.value(),self.lon.value())
            self.utc.setText(self.c["utc"].strftime("%Y-%m-%d %H:%M:%S UTC")); self.jd.setText(f'{self.c["jd"]:.8f}')
            a=self.c["asc_sign"]; n=self.c["asc_nak"]; nv=self.c["asc_nav"]
            self.asc.setText(f'Lagna: {a["sinhala"]} / {a["english"]} — {self.c["asc"]:.8f}° | Lord: {a["lord"]} | Nakshatra: {n["sinhala"]} ({n["name"]}) Pada {n["pada"]} | D9: {nv["sinhala"]} / {nv["english"]}')
            m=next(p for p in self.c["planets"] if p["name"]=="Moon"); self.moon.setText(f'Moon Nakshatra: {m["nak"]["sinhala"]} ({m["nak"]["name"]}) — Pada {m["nak"]["pada"]} — Lord: {m["nak"]["lord"]}')
            M,A=current_dasha(self.c["dasha"]); self.cur.setText(f'Current Vimshottari: {M["lord"]} Mahadasha | {A["lord"]} Antardasha' if M and A else "Current Vimshottari: outside generated range")
            self.tbl.setRowCount(0)
            for p in self.c["planets"]:
                r=self.tbl.rowCount(); self.tbl.insertRow(r); vals=[p["name"],f'{p["longitude"]:.6f}',f'{p["sign"]["sinhala"]} / {p["sign"]["english"]}',str(p["house"]),f'{p["nak"]["sinhala"]} / {p["nak"]["name"]}',str(p["nak"]["pada"]),f'{p["nav"]["sinhala"]} / {p["nav"]["english"]}',f'{p["speed"]:.6f}']
                for j,v in enumerate(vals): self.tbl.setItem(r,j,QTableWidgetItem(v))
            self.update_d1(); self.update_d9(); self.update_dasha()
        except Exception as e: QMessageBox.critical(self,"Calculation Error",str(e))
    def grid_fill(self,grid,items):
        for r in range(4):
            for c in range(4): grid.setItem(r,c,QTableWidgetItem(""))
        for i,(r,c) in GRID.items():
            s=SIGNS[i]; lines=[s[1],s[2]]
            if items.get(i): lines.append(" / ".join(items[i]))
            it=QTableWidgetItem("\n".join(lines)); it.setTextAlignment(Qt.AlignCenter); grid.setItem(r,c,it)
    def update_d1(self):
        by={i:[] for i in range(12)}
        for p in self.c["planets"]: by[p["sign"]["index"]].append(p["name"])
        by[self.c["asc_sign"]["index"]].insert(0,"LAGNA"); self.grid_fill(self.d1grid,by)
        self.d1title.setText(f'D1 / Rashi Chart — {self.name.text().strip() or "Horoscope"} — Lagna: {self.c["asc_sign"]["sinhala"]} / {self.c["asc_sign"]["english"]}')
        self.houses.setRowCount(0)
        for h in self.c["houses"]:
            r=self.houses.rowCount(); self.houses.insertRow(r); vals=[str(h["house"]),f'{h["sinhala"]} / {h["english"]}',h["lord"],", ".join(h["planets"]) or "-","0°–30°"]
            for j,v in enumerate(vals): self.houses.setItem(r,j,QTableWidgetItem(v))
    def update_d9(self):
        by={i:[] for i in range(12)}
        for p in self.c["planets"]: by[p["nav"]["index"]].append(p["name"])
        by[self.c["asc_nav"]["index"]].insert(0,"D9 LAGNA"); self.grid_fill(self.d9grid,by)
        self.d9title.setText(f'D9 / Navamsa Chart — {self.name.text().strip() or "Horoscope"} — Lagna: {self.c["asc_nav"]["sinhala"]} / {self.c["asc_nav"]["english"]}')
        self.d9tbl.setRowCount(0)
        for p in self.c["planets"]:
            r=self.d9tbl.rowCount(); self.d9tbl.insertRow(r); vals=[p["name"],f'{p["sign"]["sinhala"]} / {p["sign"]["english"]}',f'{p["nav"]["sinhala"]} / {p["nav"]["english"]}',str(p["nav"]["number"]),p["nav"]["lord"]]
            for j,v in enumerate(vals): self.d9tbl.setItem(r,j,QTableWidgetItem(v))
    def fmt(self,x): return x.strftime("%Y-%m-%d %H:%M")
    def update_dasha(self):
        d=self.c["dasha"]; M,A=current_dasha(d); self.dsummary.setText(f'Birth Nakshatra: {d["birth_nakshatra"]["sinhala"]} / {d["birth_nakshatra"]["name"]} — Lord: {d["first_lord"]} | First Mahadasha balance: {d["balance"]:.3f} years')
        self.md.setRowCount(0)
        for x in d["maha"]:
            r=self.md.rowCount(); self.md.insertRow(r); vals=[x["lord"],self.fmt(x["start"]),self.fmt(x["end"]),f'{x["years"]:.3f}']
            for j,v in enumerate(vals): self.md.setItem(r,j,QTableWidgetItem(v))
        self.ad.setRowCount(0)
        for x in d["antar"]:
            r=self.ad.rowCount(); self.ad.insertRow(r); vals=[x["maha"],x["lord"],self.fmt(x["start"]),self.fmt(x["end"]),f'{x["years"]:.4f}']
            for j,v in enumerate(vals): self.ad.setItem(r,j,QTableWidgetItem(v))
    def save(self):
        if not self.name.text().strip(): QMessageBox.warning(self,"Required","Name is required."); return
        if not hasattr(self,"c"): self.calc()
        if not hasattr(self,"c"): return
        d=self.date.date(); t=self.time.time()
        add_horoscope({"name":self.name.text().strip(),"gender":self.gender.currentText(),"birth_date":d.toString("yyyy-MM-dd"),"birth_time":t.toString("HH:mm:ss"),"birth_place":self.place.currentText(),"latitude":self.lat.value(),"longitude":self.lon.value(),"timezone":self.tz.text(),"utc_time":self.c["utc"].strftime("%Y-%m-%d %H:%M:%S UTC"),"julian_day":self.c["jd"]})
        self.refresh(); QMessageBox.information(self,"Saved","Horoscope saved.")
    def refresh(self):
        if not hasattr(self,"saved"): return
        rows=search_horoscopes(self.search.text()); self.saved.setRowCount(0)
        for x in rows:
            r=self.saved.rowCount(); self.saved.insertRow(r)
            vals=[x["id"],x["name"],x["gender"],x["birth_date"],x["birth_time"],x["birth_place"],x["utc_time"]]
            for j,v in enumerate(vals): self.saved.setItem(r,j,QTableWidgetItem(str(v or "")))
    def clear(self):
        self.name.clear(); self.gender.setCurrentIndex(0); self.place.setCurrentText("Colombo"); self.place_change("Colombo")
        self.tbl.setRowCount(0); self.asc.setText("Lagna / Ascendant: -"); self.moon.setText("Moon Nakshatra: -"); self.cur.setText("Current Dasha: -")
        self.utc.setText("-"); self.jd.setText("-")
