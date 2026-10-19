# Down the Rabbit Hole — Aurora Patient Zero (10 pts)

Continue examining the Patient Portal app (same IPA as Info Leaks). "The application relies heavily on a unique..." — find the patient's ID.

## How I solved it

The app bundle includes a chest X-ray: `aurora_chest_xray.jpg`. Check its metadata:

```
exiftool -b -XMP aurora_chest_xray.jpg
→ <dc:identifier>PID-847261</dc:identifier>
```

The Patient ID lives in the **XMP of the bundled image**. Cross-check: grep the Mach-O for 847261 — zero hits. The binary has no hardcoded ID; the app cross-references the patient by reading the identifier out of the imaging file it displays. (The bundled `aurora_meds.sqlite` keys meds by pid, but only holds demo rows 101001–313252 — the real patient is the one in the X-ray.)

So the "unique identifier" the app leans on is hiding inside the picture it shows the patient.

## Flag

```
deadface{847261}
```
