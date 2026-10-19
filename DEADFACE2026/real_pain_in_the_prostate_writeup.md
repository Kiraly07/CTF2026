# Real Pain in the Prostate (2 of 4 series) — Web (50 pts)

We're inside Health Spark (http://45.79.200.170:3000) from Doctor Appointment. Now get data we shouldn't see.

## How I solved it

Part 1 (SQLi on `POST /api/login`) gave us john.smith. But the same endpoint is a boolean oracle — you can enumerate users with it:

```json
{"username":"' OR username <> 'john.smith' --", "password":"x"}
```

That walks the table: 5 users total, including **maria.holloway, departmentid 18432** and a hidden `grant.whitfield`.

The dashboard fetches member PHI via `POST /api/patients` with a `departmentid` in the body — and the server trusts that number from the request instead of the JWT claim. Classic IDOR: just change the department:

```json
POST /api/patients
{"departmentid": 18432}
```

That dumps another department's patient records. One row jumps out — "Patient Zero", HS-8820343, with the diagnosis field set to the flag.

(My first attempt at this challenge grabbed `oh_you_shouldnt_be_here` from the internal admin console — and it got rejected. That string is a decoy: it shows up in the internal console reachable via mass-assignment + SSRF, but it's not part 3's flag either. The real part 3 answer lives in an IDOR'd PDF — see the Do People Still Fax writeup.)

## Flag

```
deadface{hipaa_exposure_is_bad}
```
