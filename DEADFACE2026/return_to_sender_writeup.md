# Return to Sender — Traffic Analysis (80 pts)

A compromised host is shipping stolen data out disguised as ordinary web traffic. Find it and piece it back together.

## How I solved it

The pcap has ~170 HTTP requests to legitimate-looking hosts — but sorting the request hosts by destination IP, the crowd sits at 93.184.x.x while **5 POSTs** go elsewhere:

```
telemetry.deadface-cc.net (45.66.77.88:80) /api/upload?seq=1..5
```

The decoys carry harmless form noise (`comment=nice+post`, `q=weather+today`). The five real ones post raw `application/octet-stream`, 8 bytes each:

```
ZGVhZGZh  Y2V7aHR0  cF9leGZp  bF9zbmVh  a3lf
```

Base64-decode and concatenate: `deadface{http_exfil_sneaky_`

...which is incomplete. The last piece is smuggled somewhere else on those same requests: every exfil POST carries a constant

```
X-Session-Id: YnVzaW5lc3N9
```

Base64 → `business}`.

Body chunks + header chunk = the whole flag. Two channels, one message — and 165 decoy requests of camouflage around it.

## Flag

```
deadface{http_exfil_sneaky_business}
```
