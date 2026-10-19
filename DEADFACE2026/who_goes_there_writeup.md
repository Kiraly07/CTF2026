# Who Goes There? — De Monne Breach (25 pts)

DEADFACE slipped a rogue Kali box onto De Monne Financial's network, then someone used a legitimate employee account to hit the file share. From an 8GB memory image, name the compromised employee.

## How I solved it

No volatility3 on the box, so I went old-school: targeted UTF-16LE strings extraction over the image (`strings -e l` + grep, plus a byte-offset scan for the interesting terms).

The image is a Windows 10/11 workstation, `COMPUTERNAME=DMF-WS11-042`. Two things pop out:

**1. The file share mapping.** Someone ran, via `mshta` + PowerShell:

```
net use h: \\filecl01fsh\users$
```

Key detail: `net use` was issued **without any `/user:` override**, which means it authenticated as the *currently logged-on* user. That's the compromised account.

**2. Who's logged on.** `USERNAME=nkessler` appears 100+ times across the image (`USERPROFILE=C:\Users\nkessler`, OneDrive path, everything). It's the only interactive user in there. There's even the origin of the SSH key that shows up in strings:

```
ssh-keygen.exe -t ed25519 -C nkessler@demonnefinancial.com
```

Scanning the whole image for other `@demonnefinancial.com` addresses or other `USERNAME=` values turned up nothing. One employee, one account: **nkessler**.

## Flag

```
deadface{nkessler}
```
