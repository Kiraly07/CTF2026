# Foothold on Charon — Hostbusters (10 pts)

*Note: Charon was reset for the final wave — same solve, new flag text (the original flag was `deadface{f00th0ld_0n_ch4r0n}`).*

DEADFACE runs an internal ops/staging box they call **charon** — the coordination server for their "Kingmaker" influence-operation workstream. The challenge hands you a web shell at `http://hostbusters.dctf.io` and drops you in as the `svc-deploy` service account. Find the flag that proves your foothold.

## How I solved it

"Charon is disposable" — every web-shell session is a fresh copy of the box, so flags have to be grabbed in the session you're in. Once the shell connects:

```
charon:~$ whoami
svc-deploy
charon:~$ pwd
/home/svc-deploy
charon:~$ ls -la
.bash_history   flag.txt
```

That was easy:

```
charon:~$ cat /home/svc-deploy/flag.txt
```

The "foothold" was handed to you on purpose — this challenge is the warm-up. The interesting part is what `/home` shows: real DEADFACE member accounts (deephax, gh0st404, lilith, mort1cia, spookyboi, sunstalker). That's the setup for the rest of the series (Looking Back, and later Dangerous Capability).

## Flag

```
deadface{f00th0ld_p4st_th3_v31l}
```
