from datetime import datetime, timezone
import swisseph as swe

# V1: astronomical calculation foundation.
# Interpretation is intentionally kept separate.
PLANETS = [
    ("Sun", swe.SUN),
    ("Moon", swe.MOON),
    ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS),
    ("Mars", swe.MARS),
    ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN),
    ("Rahu", swe.MEAN_NODE),
]

def calculate_planets(year, month, day, hour_decimal, ayanamsa=swe.SIDM_LAHIRI):
    swe.set_sid_mode(ayanamsa)
    jd_ut = swe.julday(year, month, day, hour_decimal)
    result = []
    for name, planet in PLANETS:
        xx, flags = swe.calc_ut(jd_ut, planet, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
        result.append({
            "name": name,
            "longitude": xx[0],
            "latitude": xx[1],
            "distance": xx[2],
            "speed": xx[3],
        })
    # Ketu is opposite Rahu.
    rahu = next(x for x in result if x["name"] == "Rahu")
    result.append({
        "name": "Ketu",
        "longitude": (rahu["longitude"] + 180.0) % 360.0,
        "latitude": -rahu["latitude"],
        "distance": rahu["distance"],
        "speed": -rahu["speed"],
    })
    return result
