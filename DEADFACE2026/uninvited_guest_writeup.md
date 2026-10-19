# Uninvited Guest — De Monne Breach (25 pts)

"Nathan's workstation asked the local network to resolve a file-server name. Which corporate IPv4 address supplied the suspicious answer?"

## How I solved it

The pcap has Nathan's workstation (10.77.10.20 — its mDNS announcements confirm it's DMF-WS11-042, the machine from Who Goes There?) asking the local network to resolve the file server **dmf-field-01** over and over:

- 40x mDNS queries to 224.0.0.251:5353 (`dmf-field-01.local`)
- 40x LLMNR queries to 224.0.0.252:5355
- NBNS broadcast for `DMF-FIELD-01<1C>` — the *Domain Controllers* group name, which a file server would never register

So who answered? Exactly one host, every time, on all three protocols:

```
dmf-field-01 -> 10.77.10.66
```

That's the textbook Responder-style LLMNR/NBNS/mDNS poisoning pattern: the rogue device hears a multicast name query and shouts "that's me!". No legitimate server ever responded to any of the 80 queries.

Cross-checks that seal it:

- Before poisoning, 10.77.10.66 probed unicast DNS (1.1.1.1) for `DMF-FILE-01` and got NXDOMAIN — the attacker checking whether the real name resolves.
- Right after the poisoned response, Nathan's workstation exchanges ~13,000 packets directly with 10.77.10.66 — the victim mounting the fake file share.
- 10.77.10.66 also talks to an external DigitalOcean droplet (167.172.132.224) — C2/exfil traffic. Nathan's box, by contrast, looks like a boring corporate Windows machine (Chrome, telemetry).

Everything sits in the corporate 10.77.10.0/24 subnet: .20 Nathan, .30 another server, .66 the rogue, .254 the gateway.

## Flag

```
deadface{10.77.10.66}
```
