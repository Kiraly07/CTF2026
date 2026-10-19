# Name to a Face — De Monne Breach (10 pts)

After the poisoned name answer (from Uninvited Guest), Nathan's workstation tried to authenticate over SMB. Which username did it send?

## How I solved it

Filter the SMB2 NTLMSSP AUTHENTICATE messages (the NTLMSSP AUTHENTICATE step carries the actual username):

```
tshark -r demonne.pcap -Y "ntlmssp.messagetype == 0x00000003" \
  -T fields -e ntlmssp.auth.username -e ntlmssp.auth.hostname
```

First auth at frame 1489 (tcp.stream 2), repeating through frame 2326 with domain `dmf-field-01` — the poisoned name. Every one of them carries:

```
username: nkessler     hostname: DMF-WS11-042
```

The workstation helpfully sent Nathan's account to the attacker's box, no questions asked. And the attacker then *reused* it: frames 4990 and 11616 show 10.77.10.66 authenticating to the real file server (10.77.10.30) as `nkessler` against domain DMF-FILE-01.

## Flag

```
deadface{nkessler}
```
