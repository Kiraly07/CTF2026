# Live Boot — Brain Scans (50 pts)

"Hospitals staff insists there's no way to access the device's OS. DEADFACE utilized keys that aren't in the Field Manual."

## How I solved it

The keys story is a red herring — the boot itself needs no key at all. The Field Manual only says USB-A "accepts maintenance media", and that's exactly what the toolkit has:

```json
POST /api/connect {"tool":"live-linux","port":"usb-a"}
```

That opens a terminal window. Shell access is line-by-line via `POST /api/shell {"token":..., "line":...}`:

```
sudo mount /dev/sda2 /mnt        # exit 0, not even a password asked
cat /mnt/opt/scanworks/config.yaml
```

And there are the "hardcoded keys" the challenge meant — right in the config:

```yaml
# Upstream API key (service account). TODO: move to secrets store before GA.
api_key: deadface{h4rdc0d3d_k3ys_1n_th3_c0nf1g}
```

Same config.yaml also holds `integrity.salt: EM-2019` and the debug_console block — remember those for Bad Calibration (54) and Dump It (55). The data partition also has `/mnt/opt/scanworks/calibration/{calib.json, calib.json.sig, verify.py}` and patient .dcm files, which matter for the later challenges.

## Flag

```
deadface{h4rdc0d3d_k3ys_1n_th3_c0nf1g}
```
