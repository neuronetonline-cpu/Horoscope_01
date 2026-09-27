# Sri Lanka Horoscope — Phase 4

Desktop Vedic/Jyotish horoscope software targeted to Sri Lankan usage.

## Phase 4
- Professional birth-details entry layout inspired by Sri Lankan horoscope software workflows.
- Sri Lanka country selection.
- Sri Lankan city/town presets with latitude and longitude.
- 12-hour birth-time display with AM/PM while calculations remain internally 24-hour.
- Sri Lanka Standard Time: Asia/Colombo / UTC+05:30.
- A.D. Gregorian calendar indicator.
- Calculation verification: UTC and Julian Day.
- Existing D1/Rashi, D9/Navamsa, Vimshottari Dasha and Saved Horoscope features retained.

## Build
```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm --clean --windowed --name SriLankaHoroscope --collect-all swisseph main.py
```
