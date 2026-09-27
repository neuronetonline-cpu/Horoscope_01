# Sri Lanka Horoscope Desktop — Phase 2 Fixed

Phase 2 includes:
- Sri Lanka UTC+05:30 handling without Windows timezone database dependency
- Lahiri sidereal planetary calculations
- Rashi / Zodiac conversion
- Rashi lord
- Nakshatra and Pada
- Whole-sign Vedic houses
- Planet-to-house placement
- Proper 12-sign South Indian style D1 / Rashi chart
- Clear Lagna marking
- Saved horoscope search
- Existing SQLite database migration

Run:
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py

GitHub Actions EXE:
pyinstaller --noconfirm --clean --windowed --name SriLankaHoroscope --collect-all swisseph main.py
