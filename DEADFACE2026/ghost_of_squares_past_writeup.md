# Ghost of Squares Past — OSINT (150 pts)

Five clues around Savannah's historic squares, arranged as a compass (N/E/S/W + center). First four: the year each square was established. Fifth: the surname on the center square's monument. Flag: `deadface{Y1-Y2-Y3-Y4-surname}`.

## The riddle points

**Point 1 (riddle):** "First of them all, where the city began... A Quaker from Rhode Island sleeps under stone here" — **Johnson Square**, Savannah's first square, laid out **1733**. The Quaker from Rhode Island is Nathanael Greene, whose monument stands there.

**Point 3 (riddle):** "A battle of a northern frontier gave its name to this ground eighteen-twelve... Where a feather once drifted" — **Chippewa Square**, named for the Battle of Chippewa (War of 1812), laid out **1815**. The feather is Forrest Gump's bus-bench scene, and the "founder stands tall" is the Oglethorpe statue on that square.

## The photos

Both are cropped Google Street View panoramas, so reverse image search was mostly useless (Lens/Bing CAPTCHA'd me, Yandex just said "Savannah"). What worked:

- **Photo 2** (Point 2, East): a quiet residential row of houses with no statue or monument — rules out Reynolds (John Wesley statue), Columbia (Wormsloe fountain), Franklin (Haitian Monument). Matches **Oglethorpe Square**, laid out **1742**.
- **Photo 4** (Point 4, West): formal hedges plus a white-columned building — matches **Telfair Square** (the columned Telfair Academy sits on it), laid out **1733** (as St. James Square, renamed 1883).

## The geometry check

The four squares have to form a real compass. On the Savannah grid:

- Johnson (N) and Chippewa (S) both sit on Bull Street — the N/S axis
- Wright Square (row 2 on Bull) is forced as the center between them
- Oglethorpe and Telfair are the clean E/W pair flanking it on President Street

The geometry only closes one way — which is also the cross-check that the photo identifications are right.

## Point 5 (center)

**Wright Square** (Bull & President). Its central monument is the William Washington Gordon Monument — a 47-ft granite obelisk erected 1883 for the Central of Georgia Railroad founder. Surname engraved: **Gordon**.

## Flag

```
deadface{1733-1742-1815-1733-Gordon}
```
