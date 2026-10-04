---
title: "FLAPPYBOARD"
ctf: "CSSCTF"
date: 2026-09-30
category: reverse
flag_format: "CSSCTF{...}"
---

The stripped X11 game sends a replay to a remote verifier. `POST /api/attempt` returns a session token, round, seed, target, and `wait_seconds`. A second `/api/attempt` with that Bearer token rotates it and arms the round, so `/api/complete` needs the new token. Submit `round`, `wait_ms=wait_seconds*1000`, `ticks`, `score`, and `flaps=<tick list>`; the wait is virtual, so no sleep is needed. Round targets are 10, 20, and 30, and round 4 returns the flag.

I reproduced the game physics and pipe RNG, then beam-searched flap timings. The RNG is xorshift32 (`x ^= x << 13; x ^= x >> 17; x ^= x << 5`) and chooses `gap = (x % 0xe7) + 0x7d`. The world uses 8-bit fixed point: flap impulse `vy = -0x6bc`, gravity `vy += 0x43` (clamped at `0x800`), and pipe movement `x -= 0x2cd`. A flap tick is recorded before `world.ticks` increments. Practice endpoints `/api/practice` and `/api/practice/check` helped verify the simulation (`verified_score=10`, `cheated=0`).

```bash
python3 bot.py --play
```

`bot.py` solves each round, then posts the replay to `/api/complete`. It uses the rotated token for the submit.

## Flag

```text
CSSCTF{birdddd}
```
