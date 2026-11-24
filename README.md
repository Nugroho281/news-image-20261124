# news-image-20261124

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/Nugroho281/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/Nugroho281/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

A one-page newspaper front page that sums up the world news of **Tuesday 24 November 2026** in a single 1024×1024 image: 44 stories — 16 drawn as picture panels, 28 more in brief — under one giant date line, with a day-in-numbers rail, a UTC timeline of how the day unfolded, and a date check. The hero story is Nvidia soaring 31.5% and adding about $950bn of value in a single day after its board reinstated Jensen Huang as chief executive, with Asia's chip stocks following — Korea's Kospi closing above 5,000 and TSMC jumping 10%. The pictured panels cover the Russian strike on Zaporizhzhia that killed two and injured 22, the US blacklisting Megaspeed at the centre of the Nvidia chip scandal, the EU proposing its 22nd sanctions package on Russia, a Ukraine–Germany deal on more interceptor missiles, a US appeals court giving Trump a new path to erase his hush-money conviction, three tankers ablaze after hitting mines in the Strait of Hormuz, Iran flogging singer Parastoo Ahmadi 74 times for performing without a hijab, Israeli strikes in Gaza killing three including a UN worker, Russian jets sparking a shelter alert on South Korea's Ulleung island, the Solomon Islands dropping its China security pact for Australia, the Banten factory-fire toll reaching 26 body bags, Trump ordering faster federal executions, Spain's PP leading the polls five days before its snap election, the COP31 fallout leaving Pacific island states empty-handed, and the Washington Commanders stunning the Cincinnati Bengals 22–20 at the death.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=scz7tdtw&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>

## How it is made

`main.py` is a pure Python 3 standard-library program — no Pillow, no
numpy, no network. It draws the whole page at 2048×2048 (2×
supersample) with flat saturated shapes and a hand-built 5×7 pixel
font, then box-downscales to 1024×1024 so every letter and edge stays
sharp and the colours stay vivid. Two layouts were built and judged
against each other (a warm-paper front page with a red masthead and a
numbers strip, and a dark-masthead page with a day-in-numbers rail);
the dark-masthead layout won the blind self-judge on thumbnail
legibility and visual hierarchy, and it is the layout this program
draws by default. It writes `entry.png` (38,331 bytes, well under the
1 MiB gate) in about five seconds, deterministically: two runs produce
byte-identical output. The `entry.png` committed in this repository
is the program's exact output.

## Story credits — all first reported on Tuesday 24 November 2026

Pictured (16):

- Nvidia jumps 31.5%, adding about $950bn of market value in one day
  — its biggest jump — after the board reinstates Jensen Huang as CEO;
  Korea's Kospi closes at 5,006, TSMC jumps 10%, Japan's Nikkei climbs
  4.6% — Seoul Economic Daily; TradingView; Finwire; Korea Exchange,
  24 Nov.
- Russian strike on Zaporizhzhia kills two and injures 22, partly
  collapsing a five-storey block — h.ua; Ukraine Monitor, 24 Nov.
- US adds Singapore-based Megaspeed, the firm at the centre of the
  Nvidia scandal, to its export blacklist over AI chips bound for
  China — BBC; Reuters via Daily Summary Of, 24 Nov.
- European Commission proposes a 22nd sanctions package: 60 more
  Russian banks, 70-plus shadow-fleet ships, a sports ban — Euronews;
  Reuters; EU Today, 24 Nov.
- Ukraine and Germany reach a preliminary deal on more interceptor
  missiles in Berlin — h.ua; ISW, 24 Nov.
- US appeals court gives Trump a new path to erase his hush-money
  conviction, moving the case toward federal court — AP via
  MyCentralOregon; MEAWW, 24 Nov.
- Three oil tankers catch fire after hitting mines in the Strait of
  Hormuz; the UN counts 25 seafarers killed around the strait —
  CNBC; Starlit Daily, 24 Nov.
- Iran flogs singer Parastoo Ahmadi and four colleagues with 74
  lashes for a concert performed without a hijab — Reuters; BBC;
  Starlit Daily, 24 Nov.
- Israeli strikes in Gaza kill at least three, including UNRWA worker
  Adel al-Helo; a nine-month-old baby dies of cold in a Khan Younis
  tent — Al Jazeera; Starlit Daily, 24 Nov.
- Russian warplanes enter South Korea's air defence zone; Seoul
  briefly warns Ulleung island residents to shelter — Yonhap; The
  Independent, 24 Nov.
- Solomon Islands tells China it will not renew its 2022 security
  pact and plans a new treaty with Australia — Reuters via SRN News,
  24 Nov.
- Rescuers recover 26 body bags from the Banten candy-factory fire;
  Prabowo names Sugiono and Amran Sulaiman as vice-presidential
  picks — ANTARA via jawawa.id; EIN Presswire, 24 Nov.
- Trump orders faster federal executions at the Justice Department
  and attacks Newsom for commuting 548 California death sentences —
  Colombo Today, 24 Nov.
- Spain's PP leads the polls five days before Sunday's snap election;
  a coalition with far-right Vox looks likely — El País; Euronews;
  EU Today, 24 Nov.
- COP31 fallout: Pacific island states leave Antalya empty-handed on
  finance; focus shifts to COP32 in Addis Ababa — PINA; The
  Conversation via Evening Report; BBC, 24 Nov.
- Washington Commanders stun Cincinnati Bengals 22–20 on a last-play
  field goal; 49ers rout Vikings 35–10 in Mexico City — The Sporting
  Base, 24 Nov.

In brief (28): Zelensky calling for four-party talks and hacked
Rosstat data putting Russian war dead above 490,000 (Daily Summary
Of; Ukraine Monitor) · German intelligence warning Russia may put a
nuclear weapon in space and NATO sending AWACS planes to Poland
(The Independent; FrogNews) · the US Treasury exposing about $15bn
in Iranian shadow banking and Iran seeking $290bn in damages from
the US (Huddleworld; Pakistan TV) · the US and Qatar opening their
eighth strategic dialogue (Pakistan TV) · China sentencing an
official to death for spying and warning chip risks remain after
Huang's return (Daily Summary Of; Monolith) · Singapore and
Australia signing two pacts (The Daily Feeder) · oil falling 3% as
the Libyan pipeline restarts (The Daily Feeder) · fighting in Ituri
trapping DRC Ebola responders and 14 nations backing the ICJ
Rohingya ruling (PANA; France 24) · South Africa mourning former
deputy president Mlambo-Ngcuka and a US envoy regretting the
continuing Sudan violence (PANA) · a car bomb hitting a governor's
office in Colombia and Pennsylvania's ninth measles death
(Multnews) · a Danish court backing the 'ghetto law' evictions and
the WHO chief visiting Cuba (Multnews) · the FDA approving a new
breast-cancer drug and the NHS starting an AI breast-screening trial
(Morning Glory Sciences; TSN Media) · Rangers beating Motherwell
2–1 late and West Ham beating Wolves 4–2 (Archyworldys) · Trump's
approval at 45%, a second-term low (Morning Consult) · Seoul naming
a new foreign minister and Russia expanding a base near Finland
(Monolith) · an Indian party leader barred from a UK flight and
Australia planning 5% revenue fines for platforms (Multnews).

Day in numbers: Nvidia +31.5%, $950bn value added, Kospi 5,006, 74
lashes for the singer, 26 body bags in Banten — Seoul Economic
Daily; Reuters; BBC; ANTARA, 24 Nov.

## License

MIT — see `LICENSE`.
