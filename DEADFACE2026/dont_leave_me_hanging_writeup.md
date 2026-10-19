# Don't Leave Me Hanging — Traffic Analysis (500 pts)

The help desk subnet (10.20.200.0/24) runs an Asterisk PBX. All the call traffic is encrypted twice: SIP over TLS, media over SRTP. Somewhere in there, an insider leaks a flag during a phone call.

## How I solved it

**Getting the keys.** `mkowalski` downloaded a diagnostics tarball over FTP — creds `mkowalski / Aur0ra!Helpdesk26` pull `pbx-diag-20261008.tar.gz` from the PBX. Inside: `tls-keys.log` (an SSLKEYLOGFILE) and the SDP crypto lines. Now SIP decrypts:

```
tshark -r pcap -o tls.keylog_file:tls-keys.log -Y sip
```

**Finding the call.** One call to extension 2003 (10.20.200.23, a "Sunstalker S14" Android device — the same insider who browses ghosttown.deadface.io) has **no speech at all**. The caller ID says "MARGARET OKAFOR", the audio is pure tones: in-band DTMF.

**Decrypting SRTP.** The SDPs carry `a=crypto:1 AES_CM_128_HMAC_SHA1_80 inline:<key>` per call. I implemented the RFC 3711 key derivation (AES-CTR KDF with labels 0x00/0x01/0x02, the nonce/IV math, HMAC-SHA1-80 tag verification — all ~200k packets verified).

**The tones.** Ran the decrypted ulaw audio through a Goertzel DTMF filter. The "digits" come out as 3-digit groups:

```
100 101 097 100 102 097 099 101 123 080 114 051 053 053 095 048 110 051 095 102 048 114 095 068 051 052 100 102 052 099 051 125
```

That's decimal ASCII: 100=d, 101=e, 097=a, 100=d, 102=f... spelling out the flag. Press 1 for DEADFACE indeed.

## Flag

```
deadface{Pr355_0n3_f0r_D34df4c3}
```
