---
title: "Dead Faction Servers"
ctf: "CSS CTF 2026: Return of Nexus"
date: 2026-09-30
category: osint
flag_format: "CSSCTF{...}"
---

Starting with the handle `bobdev508`, I checked its public GitHub repos. `decoy-project` has `CTF{th1s_1s_n0t_th3_r34l_fl4g}`; the visible `app.py` and `utils.py` in `dashboard-app` have `CTF{n0t_qu1t3_1t}` and `CTF{4ls0_n0t_r34l}`.

The real flag is split across Git history and a non-default branch. Commit `be82c694633ce352b79eb1a7c51a5801be545ba7` adds a deleted `.env.local` with `SECRET_PART=Q1NTQ1RGe3VfZzA=`, which decodes to `CSSCTF{u_g0`. The `experimental/auth-rework` branch has `auth_notes.md` with suffix `t_130d_508}`.

```bash
git clone https://github.com/bobdev508/dashboard-app.git
cd dashboard-app
git show be82c694633ce352b79eb1a7c51a5801be545ba7:.env.local
printf '%s' 'Q1NTQ1RGe3VfZzA=' | base64 -d
git show origin/experimental/auth-rework:auth_notes.md
```

Join the decoded prefix and branch suffix.

## Flag

```text
CSSCTF{u_g0t_130d_508}
```
