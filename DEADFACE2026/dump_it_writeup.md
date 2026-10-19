# Dump It — Brain Scans (150 pts)

Same hospital kiosk as Bedside Manner — but now we need to dump the patient data from the hidden maintenance console.

## How I solved it

Chain of steps:

1. `GET /api/device` lists the tool registry: there's a **rubber-ducky** assigned to the usb-a port. `POST /api/connect {tool:"rubber-ducky", port:"usb-a"}` gives you an HID token.
2. The kiosk ships `hidMacro-*.js` bundles, and one of them contains the default Rubber Ducky payload: **CTRL-ALT F12** opens the hidden ScanWorks maintenance console, then a STRING line types into it.
3. What to type comes from the kiosk's disk (via the Live Linux boot tool: `sudo mount /dev/sda2 /mnt`). `/mnt/opt/scanworks/config.yaml` says:

```yaml
debug_console:
  enabled: true
  function: debug.dump
  tables: [patients, calibration, audit]
```

4. Fire the macro:

```json
POST /api/kiosk/hid {"token": "...", "macro": "CTRL-ALT F12; STRING debug.dump(patients)"}
```

The console prints the patient list plus a debug token — the flag.

## Flag

```
deadface{un10ck3d_k10sk_qu4cks_b4ck}
```
