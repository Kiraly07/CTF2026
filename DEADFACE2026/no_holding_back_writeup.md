# No Holding Back — De Monne Slayer (210 pts)

Same De Monne APK. "Details from pretty much any user they want, without knowing the user or their password" — that sentence *is* an IDOR.

## How I solved it

`ApiService` exposes:

```
GET api/accounts/{id}/statements
GET api/accounts/{id}/transactions
```

where `{id}` is a raw account id from an Intent extra. The backend (`http://dmf.dctf.io:8081`) **never checks ownership** — any authenticated session can read any account.

I logged in with the hardcoded audit account from Inside Man (audit@demonne-financial.local / demonnefinancial) to get a bearer token. Nice touch: the audit user owns zero accounts, so anything you read is somebody else's data.

Enumerated `/api/accounts/{id}/statements` for id 1..3000. Only 1001–1007 have data. Account **1007**:

```
{"period":"Q1 2026 Internal Audit Summary",
 "reference":"AUD-2026-Q1-99001",
 "summary":"RESTRICTED - De Monne Financial Internal Audit Division | Ref: deadface{IDOR_u_2_f1nD_m0r3_Fl4gz} | ..."}
```

## Flag

```
deadface{IDOR_u_2_f1nD_m0r3_Fl4gz}
```
