# The Original Reading — Database (70 pts)

Aurora Health again — this time the clinical trials EDC audit trail. Someone changed a primary efficacy result during the Veltrexa Phase III trial, and we need the *original* value.

## How I solved it

`aurora_trials.data_changes` is the audit trail. Almost every row is a routine subject correction at 09:30 — but one stands out:

```
change_id 500001
table: results, record: VELT-0137
field: primary_efficacy_delta
old_value: 2.3 -> new_value: 6.0
changed_by: mreyes at 2025-12-06 23:14:00
reason: "Query resolution per monitor"
```

It's the only change touching a primary efficacy endpoint, done at 11pm by mreyes (the same guy from The Attending, for those following the saga).

Original value: **2.3**.

## Flag

```
deadface{2.3}
```
