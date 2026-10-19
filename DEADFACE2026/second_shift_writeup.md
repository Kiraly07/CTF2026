# Second Shift — Cryptography (90 pts)

ZeroTrace pulled several files off a DEADFACE relay server used by mort1cia: one transmission preserved **before AND after** processing, plus a second outbound message only in its processed form. Figure out the relay's transformation, undo it, and read the plan.

## How I solved it

The ZIP holds three files:

- `relay-heartbeat.json` — 251 bytes, plaintext
- `relay-heartbeat.enc` — 250 bytes, the same message after the relay processed it
- `relay-tasking.enc` — 220 bytes, second message, processed form only

Giveaway first: both .enc files start with the **identical 9 bytes** — because both plaintexts start `{"type":"`. Identical ciphertext prefixes on different messages means one-time-pad-style keystream reuse.

So the relay is a stream cipher (CTR-style) XOR with a fixed keystream — and it reuses the keystream/nonce for every message. Classic two-time pad. With a known plaintext/ciphertext pair you just recover the keystream outright:

```python
keystream = plaintext XOR heartbeat.enc        # 250 bytes, position-based
tasking = relay_tasking.enc XOR keystream[:220]
```

Decoded tasking:

```json
{"type":"tasking","target":"aurora-vpn","action":"stage-access",
 "window":"00:30Z","operator":"mort1cia",
 "note":"Use the backup tunnel. Archive bundle under DEADFACE{ctr_nonce_reuse_breaks_confidentiality} before exfil."}
```

The flag is literally the lesson: CTR nonce reuse breaks confidentiality.

## Flag

```
deadface{ctr_nonce_reuse_breaks_confidentiality}
```
