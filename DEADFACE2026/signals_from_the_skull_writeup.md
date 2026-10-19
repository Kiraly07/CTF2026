# Signals from the Skull — Brain Scans (300 pts)

The CS-9000 leaks data over BLE. Sniff it, find the maintenance-log characteristic dribbling out a few bytes at a time, reassemble and decode.

## How I solved it

The tool registry (`GET /api/device`) has the right tool: `ble-sniffer` on usb-a.

```json
POST /api/connect {"tool":"ble-sniffer","port":"usb-a"}
GET /api/capture    (Authorization: Bearer <token>)
```

96 packets come back, **shuffled**. Two characteristics by handle:

- `0x2a` — 72 packets, 6-byte binary vitals frames. This is the boring telemetry decoy.
- `0x37` — 24 packets, seq 0–23. The maintenance log.

Each 0x37 payload is hex-encoded ASCII, and that ASCII is a Base64 chunk. So the pipeline is:

```python
packets = [p for p in capture["packets"] if p["handle"] == "0x37"]
packets.sort(key=lambda p: p["seq"])                 # reassemble in seq order
b64 = "".join(bytes.fromhex(p["payload"]).decode() for p in packets)
print(base64.b64decode(b64).decode())
```

(The field service manual actually documents this — section 5: 0x2a is binary vitals, 0x37 is "Base64 text, chunked across sequence-numbered notifications. Reassemble in seq order, then Base64-decode." Reading the manual first saves you the guesswork.)

Decoded log:

```
St.Dymphna CS-9000 maint log | site=stdymphna-rmc-01 | tech=emedra-svc
last_patient: Gideon Marsh (MRN 100413)
note: telemetry unencrypted per EM-2019 default; flag deadface{un3ncrypt3d_b4bbl3_fr0m_th3_sku11}
```

"Unencrypted babble from the skull" indeed — everything on this device is plaintext by default.

## Flag

```
deadface{un3ncrypt3d_b4bbl3_fr0m_th3_sku11}
```
