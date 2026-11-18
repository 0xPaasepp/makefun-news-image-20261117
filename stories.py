# Story data for news-image-20261117 v3. All stories happened or were first
# reported on Tuesday 17 November 2026. 45 stories total: 3 leads + 12 tiles
# + 30 ALSO briefs. Stat-band numbers are highlights of counted stories.

# Lead stories: section, strip colour, map bbox (lon0, lat0, lon1, lat1),
# map labels [(text, lon, lat, colour)], headline, deck.
LEADS = [
    {
        "section": "EUROPE - UKRAINE WAR", "color": "red",
        "bbox": (33.0, 43.8, 40.5, 47.6),
        "labels": [("RUSSIA", 36.6, 47.2, "ink"), ("CRIMEA", 34.4, 45.0, "ink"),
                   ("KERCH STRAIT", 38.4, 46.7, "navy"),
                   ("BLACK SEA", 36.2, 44.3, "navy")],
        "marks": [("bridge", 36.55, 45.35)],
        "headline": "KERCH BRIDGE SPAN FALLS",
        "deck": "Second strike in two days; a span drops into the sea and road traffic is suspended.",
    },
    {
        "section": "MIDDLE EAST - GULF WAR", "color": "red",
        "bbox": (47.0, 23.5, 59.5, 30.8),
        "labels": [("IRAN", 55.5, 30.2, "ink"), ("KUWAIT", 48.3, 29.9, "ink"),
                   ("BAHRAIN", 50.9, 26.9, "ink"), ("QESHAM", 56.3, 25.5, "ink"),
                   ("ARABIA", 49.0, 24.3, "ink"), ("GULF", 52.8, 27.6, "navy")],
        "marks": [("burst", 50.6, 26.3), ("dot", 50.6, 26.3),
                  ("dot", 56.3, 26.6), ("dot", 48.0, 29.4)],
        "headline": "IRAN DRONES HIT US BASE",
        "deck": "Bahrain intercepts Iranian attacks near the US base; third in five days as a fourth tanker is mined.",
    },
    {
        "section": "ASIA - SUMMIT EVE", "color": "navy",
        "bbox": (112.0, 13.0, 127.0, 26.5),
        "labels": [("CHINA", 114.0, 25.6, "ink"), ("SHENZHEN", 115.6, 22.9, "ink"),
                   ("MANILA", 122.4, 14.9, "ink"), ("TAIWAN", 122.6, 23.8, "ink"),
                   ("SOUTH CHINA SEA", 117.5, 15.2, "navy")],
        "marks": [("flags", 113.0, 25.6), ("dot", 114.1, 22.5),
                  ("dot", 121.0, 14.6), ("thunote", 124.0, 25.9)],
        "headline": "TRUMP HEADS TO SHENZHEN SUMMIT",
        "deck": "First Xi-Trump-Putin summit set for Thursday; Trump holds the first Quad summit in Manila.",
    },
]

# Tile stories: section, colour, icon kind, headline, deck.
TILES = [
    {"section": "EUROPE", "color": "blue", "icon": "flag",
     "headline": "ESTONIA SHUTS RUSSIA BORDER",
     "deck": "Closes from 1 December after a foiled drone-plant bomb plot."},
    {"section": "EUROPE", "color": "blue", "icon": "ball",
     "headline": "GERMANY 5-0 NETHERLANDS",
     "deck": "Wirtz scores twice in the World Cup qualifier rout."},
    {"section": "EUROPE", "color": "blue", "icon": "ball",
     "headline": "NORWAY 3-2 DENMARK",
     "deck": "Haaland and Odegaard strike in a five-goal thriller."},
    {"section": "MIDDLE EAST", "color": "red", "icon": "burst",
     "headline": "ZAPORIZHZHIA STRIKE KILLS 40",
     "deck": "Russian strike on the front-line city is the day's deadliest."},
    {"section": "MIDDLE EAST", "color": "red", "icon": "burst",
     "headline": "AID-CENTRE STRIKE KILLS 26",
     "deck": "Strike on an aid centre as the war grinds on."},
    {"section": "MIDDLE EAST", "color": "red", "icon": "atom",
     "headline": "IRAN REFUSES UN CHECKS",
     "deck": "Tehran bars nuclear inspections until the war ends."},
    {"section": "MARKETS & TECH", "color": "green", "icon": "chart",
     "headline": "NVIDIA BEATS FORECAST",
     "deck": "Revenue $115.8bn as the AI chip boom rolls on."},
    {"section": "MARKETS & TECH", "color": "green", "icon": "chart",
     "headline": "S&P 500 FALLS 1.4%",
     "deck": "Wall Street's worst day since June; Bitcoin nears $64,000."},
    {"section": "MARKETS & TECH", "color": "green", "icon": "chip",
     "headline": "MICROSOFT OUTAGE HITS",
     "deck": "A latent defect knocks out servers worldwide."},
    {"section": "ASIA-PACIFIC", "color": "orange", "icon": "storm",
     "headline": "CYCLONE AKVAN NEARS ODISHA",
     "deck": "Storm bears down on India's east coast."},
    {"section": "SPORT", "color": "orange", "icon": "trophy",
     "headline": "ALCARAZ BEATS TIAFOE",
     "deck": "World No. 1 wins 6-2, 6-2 at the ATP Finals."},
    {"section": "SPORT", "color": "orange", "icon": "trophy",
     "headline": "INDIA EDGE PAKISTAN U19",
     "deck": "Last-ball win in the Asia Cup final."},
]

# Stat band: (big number, small label). All numbers are from counted stories.
STATS = [
    ("$115.8bn", "NVIDIA REVENUE"),
    ("11,000+", "EBOLA CASES IN DR CONGO"),
    ("-1.4%", "S AND P 500"),
    ("40", "KILLED IN ZAPORIZHZHIA"),
    ("$120bn", "CLIMATE FINANCE BY 2035"),
    ("178", "SITES HIT BY HACKERS"),
]

# ALSO briefs: one short line each, two columns of 15. Keep each under 32 chars.
ALSO = [
    "Scotland 0-4 Switzerland",
    "Norway bans Russian athletes",
    "Lukaku quits internationals",
    "Ireland 3-0 Kosovo",
    "Gaza tents strike kills 3",
    "Fourth tanker mined in Hormuz",
    "Trump warns of dirty-bomb plot",
    "JPMorgan outage resolved",
    "Hackers hit 178 sites",
    "Anthropic IPO in focus",
    "US tightens chip rules on China",
    "NSA network reported down",
    "Delhi chokes on smog",
    "Bear shuts Maebashi schools",
    "Queen in Turkiye for COP31",
    "Dhoni ends IPL career",
    "Thailand trade deal signed",
    "Jay Shah re-elected ICC chief",
    "Elks win Grey Cup 37-30",
    "FEMA alert test nationwide",
    "US loses measles-free status",
    "Argentina merger rules begin",
    "Australia puberty-blocker draft",
    "AFCON: five winners qualify",
    "COP31: $120bn climate fund",
    "ECO adopts Vision 2035",
    "UK sanctions settlement firms",
    "Dhaka garment workers protest",
    "Japan scrambles Russian jets",
    "Thailand fire kills 11",
]

# World-map pins: (number, name, lon, lat, dlon, dlat) — dlon/dlat nudge the
# drawn pin (in degrees) so close pins do not overlap; the key names them.
# Nudges were laid out so every pair of drawn pins is >= ~21 map units
# apart (disc radius 8); _bottom() draws a short leader from the true
# spot (small dot) to the offset numbered pin.
PINS = [
    (1, "KERCH", 36.5, 45.3, 0.0, 0.0),
    (2, "KYIV", 30.5, 50.4, -4.0, 5.0),
    (3, "BAHRAIN", 50.5, 26.2, 1.0, 9.0),
    (4, "HORMUZ", 56.3, 26.6, 6.5, -8.0),
    (5, "GAZA", 34.5, 31.5, 6.0, -9.0),
    (6, "MANILA", 121.0, 14.6, 1.0, -7.0),
    (7, "SHENZHEN", 114.1, 22.5, 3.0, 8.0),
    (8, "DELHI", 77.2, 28.6, -2.0, 9.0),
    (9, "ODISHA", 85.8, 20.3, 1.0, -7.0),
    (10, "ANTALYA", 30.7, 36.9, -8.0, -6.0),
    (11, "WASHINGTON", -77.0, 38.9, 0.0, 0.0),
    (12, "KINSHASA", 15.3, -4.3, 0.0, 0.0),
]
