# Bad Guys Be Bad — Traffic Analysis (350 pts)

A pcap of C2 traffic. The exfil config is hiding in plain sight, the data's in DNS, and it's all wrapped up.

## How I solved it

Export HTTP objects from the pcap first — you get `staging.bin`, which is the C2 config in plain text:

```
mode=exfil, channel=dns, xor_key=Sp00ky, target=exfil.deadface-c2.net
```

So: DNS-based exfil, XOR key "Sp00ky". The DNS queries look like:

```
s00-G4KVCVANDAYB.exfil.deadface-c2.net
s01-... s02-... s03-... s04-FY
```

Five 12-character labels = one continuous base32 stream. Concatenate the label contents (50 base32 chars), pad, decode → 31 bytes, then XOR with the repeating key `Sp00ky`:

```
deadface{c2_traffic_be_bussing}
```

## Flag

```
deadface{c2_traffic_be_bussing}
```
