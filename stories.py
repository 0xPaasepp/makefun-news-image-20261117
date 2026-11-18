# The day's news, verified from live reporting on 18 Nov 2026.
# Every headline is true as reported; wording is shortened only to fit,
# never to change a fact. Each story is (headline, icon) — no deck line
# under any story except the lead, so the bigger headlines fit.
# Headlines are kept to <=22 chars for one line (condensed scale),
# or <=44 chars for two lines. 41 stories: the original 36 + 5 new
# ones verified 18 Nov (Norway/Denmark, Ireland/Kosovo, Thailand
# trade deal, Jay Shah, measles status).

LEAD_HEAD = "UKRAINE STRIKES KERCH BRIDGE AGAIN"
LEAD_DECK = ("Second hit in under 24 hours; traffic suspended "
             "as Russia hits Kyiv crossings.")

# Each column: list of (section_header, icon_or_None, [(headline, icon), ...])
COLUMNS = [
    [
        ("EUROPE", None, [
            ("Zaporizhzhia strike kills 40", "explosion"),
            ("Estonia shuts Russia border 1 Dec", "flag"),
            ("Germany 5-0 Dutch", "ball"),
            ("Scotland 0-4 Swiss", "ball"),
            ("Norway bans Russians", "doc"),
            ("Lukaku quits Belgium", "ball"),
            ("Norway 3-2 Denmark", "ball"),
            ("Ireland 3-0 Kosovo", "ball"),
        ]),
        ("MIDDLE EAST", "tanker", [
            ("4th tanker mined in Hormuz", "tanker"),
            ("Bahrain stops Iranian attacks", "shield"),
            ("Iran refuses UN checks", "no"),
            ("Israel hits Gaza tents, 3 dead", "explosion"),
        ]),
    ],
    [
        ("ASIA-PACIFIC", "cyclone", [
            ("China confirms Xi-Trump-Putin summit", "globe"),
            ("Trump, Quad in Manila", "globe"),
            ("Cyclone Akvan nears", "storm"),
            ("Delhi chokes on smog", "cloud"),
            ("India edge Pakistan", "trophy"),
            ("Alcaraz beats Tiafoe", "ball"),
            ("Bear closes schools", "bear"),
            ("Malaysia's Queen arrives for COP31", "crown"),
            ("Dhoni ends IPL career", "trophy"),
            ("Trump signs Thai deal", "flag"),
            ("Shah stays ICC chief", "trophy"),
        ]),
        ("AFRICA & OCEANIA", None, [
            ("AFCON: five winners", "trophy"),
            ("Argentina merger rules", "doc"),
            ("Australia: puberty-blocker advice", "plus"),
        ]),
    ],
    [
        ("MARKETS & TECH", "chip", [
            ("Nvidia beats estimates", "chip"),
            ("S&P 500 falls 1.4%", "chart"),
            ("Bitcoin near $64,000", "coin"),
            ("JPMorgan outage ends", "bolt"),
            ("Microsoft explains outage", "bolt"),
            ("NSA network down", "lock"),
            ("US curbs chip exports", "chip"),
            ("Hackers hit 178 sites", "warn"),
            ("Anthropic IPO in focus", "chart"),
        ]),
        ("AMERICAS", None, [
            ("Grey Cup: Elks 37-30", "trophy"),
            ("FEMA tests US alert", "warn"),
            ("US measles-free ends", "virus"),
        ]),
        ("CLIMATE", None, [
            ("COP31: $120bn fund", "leaf"),
            ("ECO: Vision 2035 adopted", "globe"),
        ]),
    ],
]


def story_count():
    n = 1  # the lead
    for col in COLUMNS:
        for _hdr, _icon, stories in col:
            n += len(stories)
    return n
