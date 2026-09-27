from datetime import datetime
from zoneinfo import ZoneInfo
import swisseph as swe

PLANETS = [
    ("Sun", swe.SUN), ("Moon", swe.MOON), ("Mercury", swe.MERCURY),
    ("Venus", swe.VENUS), ("Mars", swe.MARS), ("Jupiter", swe.JUPITER),
    ("Saturn", swe.SATURN), ("Rahu", swe.MEAN_NODE),
]

def local_to_utc(date_text, time_text, timezone_name="Asia/Colombo"):
    local = datetime.fromisoformat(f"{date_text}T{time_text}").replace(
        tzinfo=ZoneInfo(timezone_name)
    )
    return local, local.astimezone(ZoneInfo("UTC"))

def calculate_chart(date_text, time_text, latitude, longitude,
                    timezone_name="Asia/Colombo"):
    local_dt, utc_dt = local_to_utc(date_text, time_text, timezone_name)
    hour_ut = (utc_dt.hour + utc_dt.minute / 60.0 +
               utc_dt.second / 3600.0 +
               utc_dt.microsecond / 3600000000.0)
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_ut)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

    planets = []
    for name, planet in PLANETS:
        xx, _ = swe.calc_ut(jd_ut, planet, flags)
        planets.append({
            "name": name,
            "longitude": xx[0] % 360.0,
            "latitude": xx[1],
            "speed": xx[3],
        })

    rahu = next(p for p in planets if p["name"] == "Rahu")
    planets.append({
        "name": "Ketu",
        "longitude": (rahu["longitude"] + 180.0) % 360.0,
        "latitude": -rahu["latitude"],
        "speed": -rahu["speed"],
    })

    cusps, ascmc = swe.houses_ex(
        jd_ut, float(latitude), float(longitude), b"P",
        flags=swe.FLG_SIDEREAL
    )
    return {
        "local": local_dt,
        "utc": utc_dt,
        "jd_ut": jd_ut,
        "planets": planets,
        "ascendant": ascmc[0] % 360.0,
        "cusps": [float(x) % 360.0 for x in cusps],
    }
