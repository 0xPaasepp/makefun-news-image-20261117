"""Story data for news-image-20261117 (Tuesday 17 November 2026).
All 53 stories verified 17 Nov 2026 (41 from yesterday's verified set +
12 more verified live on 18 Nov). ASCII only (the font is ASCII).
"""

TOP3 = [
    {
        "tag": "EUROPE - UKRAINE WAR",
        "tag_color": 2,
        "headline": "KERCH BRIDGE SPAN FALLS INTO THE SEA",
        "deck": "Second strike in two days; traffic suspended.",
        "map": "kerch",
    },
    {
        "tag": "MIDDLE EAST - GULF WAR",
        "tag_color": 2,
        "headline": "IRAN DRONES HIT US BASE IN BAHRAIN",
        "deck": "Bahrain intercepts Iranian attacks near US base; third in five days.",
        "map": "gulf",
    },
    {
        "tag": "ASIA - SUMMIT EVE",
        "tag_color": 3,
        "headline": "TRUMP HEADS TO SHENZHEN SUMMIT",
        "deck": "China confirms first trilateral, Thursday.",
        "map": "china",
    },
]

# sections: (name, color, [(icon, headline), ...]) -- headlines <= 31 chars
SECTIONS = [
    ("EUROPE", 3, [
        ("flag", "ESTONIA SHUTS RUSSIA BORDER"),
        ("ball", "GERMANY 5-0 NETHERLANDS"),
        ("ball", "SCOTLAND 0-4 SWITZERLAND"),
        ("flag", "NORWAY BANS RUSSIAN ATHLETES"),
        ("ball", "LUKAKU QUITS BELGIUM"),
        ("ball", "NORWAY 3-2 DENMARK"),
    ]),
    ("MIDDLE EAST", 2, [
        ("boom", "ZAPORIZHZHIA STRIKE KILLS 40"),
        ("boom", "AID-CENTRE STRIKE KILLS 26"),
        ("doc", "IRAN REFUSES UN CHECKS"),
        ("boom", "ISRAELI STRIKE KILLS 3 IN GAZA"),
        ("ship", "4TH TANKER MINED IN HORMUZ"),
        ("warn", "TRUMP WARNS OF DIRTY-BOMB PLOT"),
    ]),
    ("MARKETS & TECH", 4, [
        ("chart", "NVIDIA BEATS FORECAST"),
        ("chart", "S AND P 500 FALLS 1.4%"),
        ("coin", "BITCOIN NEAR $64,000"),
        ("bank", "JPMORGAN OUTAGE ENDS"),
        ("chip", "MICROSOFT OUTAGE HITS"),
        ("bolt", "HACKERS HIT 178 SITES"),
    ]),
    ("SPORT & CLIMATE", 5, [
        ("ball", "ALCARAZ BEATS TIAFOE"),
        ("trophy", "INDIA EDGE PAKISTAN U19"),
        ("medal", "DHONI ENDS IPL CAREER"),
        ("trophy", "GREY CUP: ELKS 37-30"),
        ("leaf", "COP31: $120BN FUND DRAFT"),
        ("leaf", "ECO: VISION 2035 ADOPTED"),
    ]),
]

# also-on list: 26 items, each <= 48 chars, one line at 10px
ALSO = [
    "Cyclone Akvan nears Odisha and Andhra",
    "Delhi chokes on smog",
    "Trump in Manila for Quad summit",
    "Trump signs Thailand trade deal",
    "Jay Shah re-elected ICC chairman",
    "Bear shuts Maebashi schools",
    "Malaysia's Queen arrives for COP31",
    "Ireland 3-0 Kosovo, Parrott double",
    "FEMA tests US emergency alert",
    "Anthropic IPO in focus",
    "US tightens chip export rules",
    "NSA network reported down",
    "AFCON: five winners qualify",
    "Argentina merger rules take effect",
    "Australia: puberty-blocker advice",
    "US loses measles-free status",
    "Ebola in DR Congo tops 11,000 cases",
    "Nepal first in line for loss-and-damage cash",
    "Pattinson named new James Bond",
    "COP31 draft: faster fossil-fuel exit",
    "Thailand building fire kills 11",
    "US judge blocks Trump student rule",
    "Japan scrambles jets at Russian planes",
    "South Africa: 17 killed in shootings",
    "UK sanctions Israeli settlement firms",
    "Dhaka garment workers protest",
]

# world map dots: (label, lon, lat)
MAP_DOTS = [
    ("KERCH", 36.0, 45.0),
    ("KYIV", 30.5, 50.5),
    ("BAHRAIN", 50.5, 26.0),
    ("HORMUZ", 57.0, 26.5),
    ("GAZA", 34.4, 31.5),
    ("MANILA", 121.0, 14.5),
    ("SHENZHEN", 114.0, 22.5),
    ("DELHI", 77.0, 28.5),
    ("ODISHA", 85.0, 20.0),
    ("ANTALYA", 30.7, 36.9),
    ("WASHINGTON", -77.0, 39.0),
    ("KINSHASA", 15.3, -4.3),
]

TOTAL = 3 + sum(len(s[2]) for s in SECTIONS) + len(ALSO)
