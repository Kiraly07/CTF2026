# Hooked — Forensics (25 pts)

A Chrome profile dump (History, Login Data, Cache) for DEMONNE-WS04, user Fletcher Kampeter. We need the URL he got hooked on — the phishing link.

## How I solved it

Parsed the History SQLite (Chrome timestamps are microseconds since 1601). The 2025-03-14 timeline tells the whole story:

- 10:22:15 — opens the Gmail message *"[URGENT] De Monne VPN Migration - Action Required"*
- 10:23:44 — visits `http://demonne-secure-portal.net/login?ref=vpn_auth&token=df4e91bc` (transition = LINK, came from the inbox)
- 10:23:44 — Login Data records a new saved credential for f.kampeter@demonne.com against that login page

The cache confirms it: `f_000006` holds the phishing page ("VPN Migration Notice: Please re-authenticate", hidden token df4e91bc) and `f_000009` has the JS POSTing the stolen credentials to `185.220.101.47/collect`. The later /auth/redirect hit is a server-side redirect, not a second click.

The flag is the phishing URL itself.

## Flag

```
deadface{http://demonne-secure-portal.net/login?ref=vpn_auth&token=df4e91bc}
```
