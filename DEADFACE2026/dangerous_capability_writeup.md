# Dangerous Capability — Hostbusters (300 pts)

lilith left "crypto tooling" lying around charon. One of those tools was granted a Linux capability it should never have had. Use it to become the next user.

## How I solved it

The recon payload from the cron trick (On Schedule) already dumped `getcap -r /`:

```
/opt/crypto/cryptctl cap_setuid=ep
```

A root-owned, world-executable static ELF with **cap_setuid**. Strings tell the whole story:

```
"[cryptctl] assuming the crypto service identity."
cryptctl: setuid / cryptctl: chdir / cryptctl: exec
hardcoded "/home/spookyboi", sets HOME/USER, execl("/bin/bash", ...)
```

It setuids to uid 1006 (spookyboi — the "crypto service identity"), chdirs into /home/spookyboi, and execs a bash. Because the capability lives on the **file**, it works from any account on the box — even plain svc-deploy:

```
/opt/crypto/cryptctl
$ id      # uid=1006(spookyboi) gid=1001(svc-deploy)
$ cat ~/flag.txt
```

(Note the gid doesn't change — setuid only — but that doesn't matter, the flag reads fine.) spookyboi's home also has a `.backup` directory worth poking for future challenges.

cap_setuid on a world-executable binary cuts deep.

## Flag

```
deadface{c4p_s3tu1d_cuts_d33p}
```
