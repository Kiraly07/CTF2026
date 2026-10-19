# Inside Man — De Monne Slayer (20 pts)

Same De Monne APK as Hard Kept Secrets. This time: the backdoor account.

## How I solved it

In `com.demonne.financial.LoginActivity` there are hardcoded "internal" credentials:

```java
INTERNAL_ACCOUNT = "audit@demonne-financial.local"
INTERNAL_PASS    = "demonnefinancial"
```

The normal `attemptLogin()` quietly routes these into a separate `performInternalLogin()` — a hidden backdoor, with logging turned off, which matches the challenge story ("no backend logs").

Use them against the app backend:

```
POST http://dmf.dctf.io:8081/api/auth/login
{"email":"audit@demonne-financial.local","password":"demonnefinancial"}
```

Response includes the Audit System's welcome message — and that message is the flag (it also hands you a bearer token, which you'll want for No Holding Back).

## Flag

```
deadface{l3FT_b3Hind!}
```
