# Sri Lanka Horoscope Desktop — Phase 2

Phase 2 adds:
- Rashi / zodiac sign conversion
- Nakshatra and Pada
- Rashi lord
- Whole-sign Vedic houses
- House/sign/planet summary
- D1 / Rashi chart display
- Planet placement by house

Phase 1 Sri Lanka time handling and Lahiri sidereal calculations are retained.

Run:
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py

For the GitHub Actions EXE build:
pyinstaller --noconfirm --clean --windowed --name SriLankaHoroscope --collect-all swisseph main.py
