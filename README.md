# Sri Lanka Horoscope Desktop V1

Windows desktop starter for a Sinhala/Vedic horoscope application.

## V1
- New horoscope entry
- SQLite customer/horoscope storage
- Search saved horoscopes
- Basic Vedic calculation foundation using Swiss Ephemeris
- Sinhala/English UI labels
- PDF report foundation

## Run
1. Install Python 3.11+.
2. Open Command Prompt in this folder.
3. `python -m venv .venv`
4. `.venv\Scripts\activate`
5. `pip install -r requirements.txt`
6. `python main.py`

Note: V1 deliberately separates astronomical calculations from interpretation/prediction rules. The prediction engine will be added after calculation outputs are validated against a reference.
