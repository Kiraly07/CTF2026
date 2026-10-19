# Data Go Brrrrr — Traffic Analysis (25 pts)

Small pcap (about 3KB). Someone's pinging 10.10.14.7 from 192.168.1.50 — a lot.

## How I solved it

ICMP echo requests with id 0x0539, and the payloads aren't just padding — each one carries 8 ASCII bytes of base64 in the echo data field (replies just say "OK"). Pull them out:

```
tshark -r 31_data_go_brrrrr.pcap -Y icmp -T fields -e data.data
```

Concatenate the request payloads in sequence order:

```
ZGVhZGZhY2V7aWNtcF8zeGZpbF93aDNuX3RoM3lfbGVhc3Rfc3VzcDNjdH0=
```

Base64-decode and there it is.

## Flag

```
deadface{icmp_3xfil_wh3n_th3y_least_susp3ct}
```
