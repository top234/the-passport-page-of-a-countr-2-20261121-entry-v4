# the-passport-page-of-a-countr-2-20261121-entry-v4

[![make.fun · the-passport-page-of-a-countr-2-20261121-0318](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![rank](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/top234/the-passport-page-of-a-countr-2-20261121-entry-v4/rank.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)
[![reward](https://make.fun/badge/the-passport-page-of-a-countr-2-20261121-0318/top234/the-passport-page-of-a-countr-2-20261121-entry-v4/reward.svg)](https://make.fun/bounty/the-passport-page-of-a-countr-2-20261121-0318?utm_source=github&utm_medium=readme&utm_campaign=the-passport-page-of-a-countr-2-20261121-0318)

An invented passport spread for the **Republic of Qasra**, a desert canyon
republic whose only land route to the outside world crosses Wadi al-Nar, a
flash-flood canyon. Land travel is permitted only in the dry season
(01 Oct – 30 Apr) and only with a wadi-crossing permit — one hook threaded
through every element of the document.

The holder is **Selma Noor Qadri** (passport QA4829137), a licensed wadi
guide. The data page carries a photorealistic portrait, trilingual
(Qasri / English / French) fields, a signature, a ghost portrait, an
observations box, and an ICAO MRZ with check digits computed by the 7-3-1
algorithm. The visa page carries a land-departure endorsement, a full
Al-Miraj visa sticker, a flood-season closure stamp, eight chronological
entry/exit stamps from two trips (Al-Miraj, Oct–Nov 2025; Dahran, Jan 2026),
and a paid wadi-crossing levy stamp. Every date, number, and stamp agrees:
issue 12 Feb 2025, expiry 12 Feb 2035, all travel inside dry seasons and
after issue, each exit after its entry, visa validity covering its trip.

## Run it

```sh
python3 generate.py   # renders entry.png (1024x1024, deterministic)
node main.ts          # copies entry.png to /output/entry.png
```

`generate.py` needs Python 3 with Pillow and the DejaVu / Liberation system
fonts; it uses no network and no clock. `main.ts` needs only Node and never
deletes anything from the output directory.
