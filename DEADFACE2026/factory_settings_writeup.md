# Factory Settings — Brain Scans (25 pts)

The ScanWorks kiosk login wants real technician credentials. "Nobody ever changes the defaults the vendor ships with."

## How I solved it

The kiosk app is a SPA — the real endpoints live in the JS bundle (`/assets/index-CbamKmo7.js` maps out /api/device, /api/connect, /api/kiosk/auth, etc.). But the actual hint is on the touchscreen itself: the **Asset Label** hotspot (also `GET /api/hotspot/sticker`) links to the field service manual:

```
/assets/cs9000-field-service-manual.pdf
```

The 4-page "Emedra CerebraScan CS-9000 Field Service Manual" — Section 2.3, "Default technician account":

```
emedra-svc / ChangeMe!2019
"IMPORTANT: change this on first boot"
```

They did not change it on first boot. Log in:

```json
POST /api/kiosk/auth {"username":"emedra-svc","password":"ChangeMe!2019"}
```

The auth response hands back a `maintenanceToken` — and that token is the flag.

## Flag

```
deadface{d3fault_cr3ds_n3v3r_ch4ng3d}
```
