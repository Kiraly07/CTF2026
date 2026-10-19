# Public Offering — De Monne Breach (75 pts)

The rogue Kali device sent a ZIP archive outside the corporate network. Which public IP and TCP port received it?

## How I solved it

There's exactly one external TCP flow from the attacker box (10.77.10.66) in the whole capture — tcp.stream 45, 164 packets, to `167.172.132.224`.

Check what's in the stream:

```
tshark -r demonne.pcap -Y "tcp.stream==45" -T fields -e frame.number -e data.data | head
```

The first payload bytes are `504b0304` — `PK\x03\x04`, the ZIP local file header magic — and the entry name inside decodes to `annual_report.pdf`. So this is the exfiltrated ZIP of the stolen executive documents.

Destination: `167.172.132.224:4815` (source port 34174). Flag format wants IP_PORT:

```
deadface{167.172.132.224_4815}
```

## Flag

```
deadface{167.172.132.224_4815}
```
