# Sri Lanka Horoscope Desktop — Phase 1 FIX 2

This version removes the Windows `zoneinfo/tzdata` dependency for Sri Lanka.
The app uses the Sri Lanka civil offset UTC+05:30 directly, so the packaged EXE
does not depend on a Windows timezone database for `Asia/Colombo`.

It also keeps:
- Local Sri Lanka birth time -> UTC
- Lahiri sidereal calculations
- Planetary longitude, latitude and speed
- Rahu/Ketu
- Ascendant/Lagna foundation
- Sri Lankan place presets
- SQLite database migration

Run:
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
python main.py

GitHub Actions PyInstaller:
pyinstaller --noconfirm --clean --windowed --name SriLankaHoroscope --collect-all swisseph main.py
