from datetime import datetime, timezone, timedelta
import swisseph as swe

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

SIGNS = [
    ("Mesha", "මේෂ", "Aries", "Mars"),
    ("Vrishabha", "වෘෂභ", "Taurus", "Venus"),
    ("Mithuna", "මිථුන", "Gemini", "Mercury"),
    ("Kataka", "කටක", "Cancer", "Moon"),
    ("Simha", "සිංහ", "Leo", "Sun"),
    ("Kanya", "කන්‍යා", "Virgo", "Mercury"),
    ("Thula", "තුලා", "Libra", "Venus"),
    ("Vrischika", "වෘශ්චික", "Scorpio", "Mars"),
    ("Dhanus", "ධනු", "Sagittarius", "Jupiter"),
    ("Makara", "මකර", "Capricorn", "Saturn"),
    ("Kumbha", "කුම්භ", "Aquarius", "Saturn"),
    ("Meena", "මීන", "Pisces", "Jupiter"),
]

NAKSHATRAS = [
    ("Ashwini", "අස්විද", "Ketu"),
    ("Bharani", "බෙරණ", "Venus"),
    ("Krittika", "කැති", "Sun"),
    ("Rohini", "රෙහෙන", "Moon"),
    ("Mrigashira", "මුවසිරස", "Mars"),
    ("Ardra", "අද", "Rahu"),
    ("Punarvasu", "පුනාවස", "Jupiter"),
    ("Pushya", "පුෂ", "Saturn"),
    ("Ashlesha", "අස්ලිස", "Mercury"),
    ("Magha", "මා", "Ketu"),
    ("Purva Phalguni", "පුවපල්", "Venus"),
    ("Uttara Phalguni", "උත්‍රපල්", "Sun"),
    ("Hasta", "හත", "Moon"),
    ("Chitra", "සිත", "Mars"),
    ("Swati", "සුවණ", "Rahu"),
    ("Vishakha", "විසා", "Jupiter"),
    ("Anuradha", "අනුර", "Saturn"),
    ("Jyeshtha", "දෙට", "Mercury"),
    ("Mula", "මුල", "Ketu"),
    ("Purva Ashadha", "පුවසල", "Venus"),
    ("Uttara Ashadha", "උත්‍රසල", "Sun"),
    ("Shravana", "සුවණ", "Moon"),
    ("Dhanishtha", "දෙනට", "Mars"),
    ("Shatabhisha", "සියාවස", "Rahu"),
    ("Purva Bhadrapada", "පුවපුටුප", "Jupiter"),
    ("Uttara Bhadrapada", "උත්‍රපුටුප", "Saturn"),
    ("Revati", "රේවතී", "Mercury"),
]

SRI_LANKA_TZ = timezone(timedelta(hours=5, minutes=30), name="Asia/Colombo")

def local_to_utc(date_text, time_text, timezone_name="Asia/Colombo"):
    if timezone_name.strip() not in ("Asia/Colombo", "Sri Lanka", "UTC+05:30"):
        raise ValueError("This Phase 2 build supports Sri Lanka time only. Use Asia/Colombo.")
    local = datetime.fromisoformat(f"{date_text}T{time_text}").replace(tzinfo=SRI_LANKA_TZ)
    return local, local.astimezone(timezone.utc)

def sign_from_longitude(longitude):
    value = longitude % 360.0
    index = int(value // 30.0)
    degree = value % 30.0
    name, si, en, lord = SIGNS[index]
    return {
        "index": index,
        "name": name,
        "sinhala": si,
        "english": en,
        "lord": lord,
        "degree": degree,
    }

def nakshatra_from_longitude(longitude):
    value = longitude % 360.0
    span = 360.0 / 27.0
    index = min(26, int(value // span))
    within = value - index * span
    pada = min(4, int(within / (span / 4.0)) + 1)
    name, si, lord = NAKSHATRAS[index]
    return {
        "index": index,
        "name": name,
        "sinhala": si,
        "lord": lord,
        "pada": pada,
    }

def calculate_chart(date_text, time_text, latitude, longitude, timezone_name="Asia/Colombo"):
    local_dt, utc_dt = local_to_utc(date_text, time_text, timezone_name)

    hour_ut = (
        utc_dt.hour
        + utc_dt.minute / 60.0
        + utc_dt.second / 3600.0
        + utc_dt.microsecond / 3600000000.0
    )
    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_ut)

    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED | swe.FLG_SIDEREAL

    planets = []
    for name, planet in PLANETS:
        xx, _ = swe.calc_ut(jd_ut, planet, flags)
        longitude_value = xx[0] % 360.0
        planets.append({
            "name": name,
            "longitude": longitude_value,
            "latitude": xx[1],
            "speed": xx[3],
            "sign": sign_from_longitude(longitude_value),
            "nakshatra": nakshatra_from_longitude(longitude_value),
        })

    rahu = next(p for p in planets if p["name"] == "Rahu")
    ketu_longitude = (rahu["longitude"] + 180.0) % 360.0
    planets.append({
        "name": "Ketu",
        "longitude": ketu_longitude,
        "latitude": -rahu["latitude"],
        "speed": -rahu["speed"],
        "sign": sign_from_longitude(ketu_longitude),
        "nakshatra": nakshatra_from_longitude(ketu_longitude),
    })

    cusps, ascmc = swe.houses_ex(
        jd_ut, float(latitude), float(longitude), b"P",
        flags=swe.FLG_SIDEREAL
    )
    ascendant = ascmc[0] % 360.0
    asc_sign = sign_from_longitude(ascendant)
    asc_nak = nakshatra_from_longitude(ascendant)

    # Whole-sign Vedic houses: Ascendant sign is House 1.
    houses = []
    for house_no in range(1, 13):
        sign_index = (asc_sign["index"] + house_no - 1) % 12
        sign = SIGNS[sign_index]
        houses.append({
            "house": house_no,
            "sign_index": sign_index,
            "sign": sign[0],
            "sinhala": sign[1],
            "english": sign[2],
            "lord": sign[3],
            "planets": [],
        })

    for planet in planets:
        house_no = ((planet["sign"]["index"] - asc_sign["index"]) % 12) + 1
        planet["house"] = house_no
        houses[house_no - 1]["planets"].append(planet["name"])

    return {
        "local": local_dt,
        "utc": utc_dt,
        "jd_ut": jd_ut,
        "planets": planets,
        "ascendant": ascendant,
        "asc_sign": asc_sign,
        "asc_nakshatra": asc_nak,
        "cusps": [float(x) % 360.0 for x in cusps],
        "houses": houses,
    }
