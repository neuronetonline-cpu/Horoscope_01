from datetime import datetime, timezone, timedelta
import swisseph as swe

SIGNS=[
("Mesha","මේෂ","Aries","Mars"),("Vrishabha","වෘෂභ","Taurus","Venus"),
("Mithuna","මිථුන","Gemini","Mercury"),("Kataka","කටක","Cancer","Moon"),
("Simha","සිංහ","Leo","Sun"),("Kanya","කන්‍යා","Virgo","Mercury"),
("Thula","තුලා","Libra","Venus"),("Vrischika","වෘශ්චික","Scorpio","Mars"),
("Dhanus","ධනු","Sagittarius","Jupiter"),("Makara","මකර","Capricorn","Saturn"),
("Kumbha","කුම්භ","Aquarius","Saturn"),("Meena","මීන","Pisces","Jupiter")]

NAK=[
("Ashwini","අස්විද","Ketu"),("Bharani","බෙරණ","Venus"),("Krittika","කැති","Sun"),
("Rohini","රෙහෙන","Moon"),("Mrigashira","මුවසිරස","Mars"),("Ardra","අද","Rahu"),
("Punarvasu","පුනාවස","Jupiter"),("Pushya","පුෂ","Saturn"),("Ashlesha","අස්ලිස","Mercury"),
("Magha","මා","Ketu"),("Purva Phalguni","පුවපල්","Venus"),("Uttara Phalguni","උත්‍රපල්","Sun"),
("Hasta","හත","Moon"),("Chitra","සිත","Mars"),("Swati","සුවණ","Rahu"),
("Vishakha","විසා","Jupiter"),("Anuradha","අනුර","Saturn"),("Jyeshtha","දෙට","Mercury"),
("Mula","මුල","Ketu"),("Purva Ashadha","පුවසල","Venus"),("Uttara Ashadha","උත්‍රසල","Sun"),
("Shravana","සුවණ","Moon"),("Dhanishtha","දෙනට","Mars"),("Shatabhisha","සියාවස","Rahu"),
("Purva Bhadrapada","පුවපුටුප","Jupiter"),("Uttara Bhadrapada","උත්‍රපුටුප","Saturn"),
("Revati","රේවතී","Mercury")]

DSEQ=["Ketu","Venus","Sun","Moon","Mars","Rahu","Jupiter","Saturn","Mercury"]
DY={"Ketu":7,"Venus":20,"Sun":6,"Moon":10,"Mars":7,"Rahu":18,"Jupiter":16,"Saturn":19,"Mercury":17}
TZ=timezone(timedelta(hours=5,minutes=30),name="Asia/Colombo")
PLANETS=[("Sun",swe.SUN),("Moon",swe.MOON),("Mercury",swe.MERCURY),("Venus",swe.VENUS),
         ("Mars",swe.MARS),("Jupiter",swe.JUPITER),("Saturn",swe.SATURN),("Rahu",swe.MEAN_NODE)]

def sign(lon):
    x=lon%360; i=int(x//30); s=SIGNS[i]
    return {"index":i,"name":s[0],"sinhala":s[1],"english":s[2],"lord":s[3],"degree":x%30}

def nak(lon):
    x=lon%360; span=360/27; i=min(26,int(x//span)); p=min(4,int((x-i*span)/(span/4))+1)
    n=NAK[i]
    return {"index":i,"name":n[0],"sinhala":n[1],"lord":n[2],"pada":p}

def navamsa(lon):
    x=lon%360; ri=int(x//30); part=min(8,int((x%30)/(30/9)))
    start=ri if ri in (0,3,6,9) else (ri+8)%12 if ri in (1,4,7,10) else (ri+4)%12
    ni=(start+part)%12; s=SIGNS[ni]
    return {"index":ni,"name":s[0],"sinhala":s[1],"english":s[2],"lord":s[3],"number":part+1}

def local_utc(ds,ts):
    local=datetime.fromisoformat(f"{ds}T{ts}").replace(tzinfo=TZ)
    return local,local.astimezone(timezone.utc)

def dasha(birth,moon_lon):
    nk=nak(moon_lon); first=nk["lord"]; span=360/27
    balance=DY[first]*(1-(moon_lon%span)/span)
    idx=DSEQ.index(first); md=[]; cur=birth
    for i in range(18):
        lord=DSEQ[(idx+i)%9]; years=balance if i==0 else DY[lord]
        end=cur+timedelta(days=years*365.2425)
        md.append({"lord":lord,"start":cur,"end":end,"years":years}); cur=end
        if (cur-birth).days>120*365: break
    ad=[]
    for m in md:
        mi=DSEQ.index(m["lord"]); cur=m["start"]
        for j in range(9):
            lord=DSEQ[(mi+j)%9]; years=DY[m["lord"]]*DY[lord]/120
            end=min(cur+timedelta(days=years*365.2425),m["end"])
            ad.append({"maha":m["lord"],"lord":lord,"start":cur,"end":end,"years":years})
            cur=end
    return {"birth_nakshatra":nk,"first_lord":first,"balance":balance,"maha":md,"antar":ad}

def current_dasha(d):
    now=datetime.now(TZ)
    m=next((x for x in d["maha"] if x["start"]<=now<x["end"]),None)
    a=next((x for x in d["antar"] if x["start"]<=now<x["end"]),None)
    return m,a

def calculate(ds,ts,lat,lon):
    local,utc=local_utc(ds,ts)
    h=utc.hour+utc.minute/60+utc.second/3600+utc.microsecond/3.6e9
    jd=swe.julday(utc.year,utc.month,utc.day,h)
    swe.set_sid_mode(swe.SIDM_LAHIRI)
    flags=swe.FLG_SWIEPH|swe.FLG_SPEED|swe.FLG_SIDEREAL
    ps=[]
    for name,pid in PLANETS:
        xx,_=swe.calc_ut(jd,pid,flags); lo=xx[0]%360
        ps.append({"name":name,"longitude":lo,"latitude":xx[1],"speed":xx[3],
                   "sign":sign(lo),"nak":nak(lo),"nav":navamsa(lo)})
    r=next(p for p in ps if p["name"]=="Rahu"); kl=(r["longitude"]+180)%360
    ps.append({"name":"Ketu","longitude":kl,"latitude":-r["latitude"],"speed":-r["speed"],
               "sign":sign(kl),"nak":nak(kl),"nav":navamsa(kl)})
    _,asc=swe.houses_ex(jd,lat,lon,b"P",flags=swe.FLG_SIDEREAL)
    al=asc[0]%360; asg=sign(al)
    houses=[]
    for n in range(1,13):
        si=(asg["index"]+n-1)%12; s=SIGNS[si]
        houses.append({"house":n,"sign_index":si,"sinhala":s[1],"english":s[2],"lord":s[3],"planets":[]})
    for p in ps:
        hn=((p["sign"]["index"]-asg["index"])%12)+1; p["house"]=hn; houses[hn-1]["planets"].append(p["name"])
    return {"local":local,"utc":utc,"jd":jd,"planets":ps,"asc":al,"asc_sign":asg,
            "asc_nak":nak(al),"asc_nav":navamsa(al),"houses":houses,
            "dasha":dasha(local,next(p for p in ps if p["name"]=="Moon")["longitude"])}
