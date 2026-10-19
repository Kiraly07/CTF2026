# Twilight Zone Transfer — Traffic Analysis (50 pts)

A misconfigured DNS server let someone pull an unauthorized zone transfer (AXFR). The capture contains the whole transfer — read the records.

## How I solved it

The story plays out in two steps in the pcap:

1. **Enumeration:** attacker 10.10.14.9 probes 16 hostnames over UDP/53.
2. **The transfer:** zone transfer over **TCP/53** (that's where AXFR lives) — request frame 36, response frame 37, transaction 0x1234, answered by ns1.deadface-cc.net (192.168.56.10).

The response carries the full zone: NS records, A records for www/mail/vpn/git/backup/admin/intranet/dev, an SPF TXT... and:

```
_flag.deadface-cc.net  TXT  "deadface{dns_zone_transfer}"
```

If AXFR filtering were on, an attacker couldn't dump the internal hostnames (git, backup, admin, intranet...) or the flag record sitting right in the zone. They named this one well.

(One oddity: the challenge blurb says "submit the flag with the dog's name" — that line is copy-pasted from chal 34 Hail Caesar. There's no dog anywhere in this capture; the `_flag` TXT record is the only flag in it.)

## Flag

```
deadface{dns_zone_transfer}
```
