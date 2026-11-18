# The day's news, verified from live reporting on 18 Nov 2026.
# Every headline is true as reported; wording is shortened only to fit,
# never to change a fact. (headline, deck) — deck may be ''.
# Decks are kept to one line (<=25 chars) so all 36 stories fit.

LEAD_HEAD = "UKRAINE STRIKES KERCH BRIDGE AGAIN"
LEAD_DECK = ("Second hit in under 24 hours; traffic suspended "
             "as Russia hits Kyiv crossings.")

# Each column: list of (section_header, icon_or_None, [(headline, deck), ...])
COLUMNS = [
    [
        ("EUROPE", None, [
            ("Russian strike kills 40 in Zaporizhzhia",
             "Aid centre hit kills 26"),
            ("Estonia to shut Russia border on 1 Dec",
             "Move follows foiled plot"),
            ("Germany thrash Netherlands 5-0",
             "Wirtz scores twice"),
            ("Scotland 0-4 Switzerland",
             "Robertson wins 103rd cap"),
            ("Norway bans Russian athletes",
             "Belarusians included"),
            ("Lukaku retires from internationals", ""),
        ]),
        ("MIDDLE EAST", "tanker", [
            ("Fourth tanker mined in Hormuz in 24h",
             "US-Iran war escalates"),
            ("Bahrain stops Iranian attacks at US base",
             "Third try in five days"),
            ("Iran refuses UN nuclear inspections",
             "Not until the war ends"),
            ("Israeli strike on Gaza tents kills 3", ""),
        ]),
    ],
    [
        ("ASIA-PACIFIC", "cyclone", [
            ("China confirms Xi-Trump-Putin summit",
             "Thursday in Shenzhen"),
            ("Trump in Manila for Quad summit",
             "Modi: a 'tough man'"),
            ("Cyclone Akvan nears Andhra coast",
             "Odisha evacuates first"),
            ("Delhi chokes as pollution deepens", ""),
            ("India edge Pakistan in U19 final",
             "Last-ball thriller"),
            ("Alcaraz beats Tiafoe in ATP opener",
             "6-2, 6-2 in Turin"),
            ("Bear on loose shuts Japan schools",
             "Maebashi closes schools"),
            ("Malaysia's Queen arrives for COP31", ""),
            ("Dhoni ends IPL career, mentors Chennai", ""),
        ]),
        ("AFRICA & OCEANIA", None, [
            ("AFCON qualifiers: five nations win", ""),
            ("Argentina merger regime takes effect", ""),
            ("Australia drafts puberty-blocker advice",
             "For under-18s"),
        ]),
    ],
    [
        ("MARKETS & TECH", "chip", [
            ("Nvidia beats estimates after the bell",
             "First since Huang's ouster"),
            ("S&P 500 falls 1.4% to June low", ""),
            ("Bitcoin steadies near $64,000",
             "After slide to $62,000"),
            ("JPMorgan outage ends", ""),
            ("Microsoft explains global outage",
             "Defect hit 80% of servers"),
            ("NSA classified network reported down", ""),
            ("US tightens chip export rules", ""),
            ("Hackers hit 178 top sites",
             "Via Optimizely: BBC, CNN"),
            ("Anthropic IPO in focus on Wall Street", ""),
        ]),
        ("AMERICAS", None, [
            ("Edmonton Elks win Grey Cup 37-30", ""),
            ("FEMA tests alert nationwide", ""),
        ]),
        ("CLIMATE", None, [
            ("COP31 draft: $120bn climate finance", ""),
            ("ECO summit adopts Vision 2035", ""),
        ]),
    ],
]


def story_count():
    n = 1  # the lead
    for col in COLUMNS:
        for _hdr, _icon, stories in col:
            n += len(stories)
    return n
