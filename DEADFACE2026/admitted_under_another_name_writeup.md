# Admitted Under Another Name — Database (15 pts)

Aurora Health's dumped patient registry hides a VIP who checked in under a fake name. Find their real MRN.

## How I solved it

Access is via the database shell at aurora.dctf.io — heads up, the challenge text says "MSSQL" but it's actually **MySQL/MariaDB** (reached through a ttyd websocket; the client banner says MariaDB monitor).

The schema hint is right there in `aurora_ehr.patients`: an `alias` column and an `is_vip` flag. So:

```sql
SELECT patient_id, mrn, first_name, last_name, alias, dob, is_vip
FROM aurora_ehr.patients WHERE is_vip = 1;
```

Exactly one row comes back:

```
mrn: AH-0044719 | Gregory Halloran | alias: "George Harmon" | dob 1971-05-09
```

Gregory Halloran checked in as "George Harmon", quietly flagged `is_vip = 1`, registered 2025-11-14 22:41. The MRN is the flag.

(Keep that MRN — AH-0044719 gets reused in Prying Eyes.)

## Flag

```
deadface{AH-0044719}
```
