# Schedule of Concern — Database (20 pts)

Aurora Health's pharmacy formulary was leaked. Baseline question: how many of the drugs are DEA Schedule II?

## How I solved it

One query against the pharmacy formulary:

```sql
SELECT dea_schedule, COUNT(*) FROM aurora_pharmacy.drugs GROUP BY dea_schedule;
```

```
II  -> 9
III -> 4
IV  -> 5
V   -> 2
N   -> 12     (32 drugs total)
```

Nine Schedule II drugs. Not a lot of code for this one — it's the setup challenge for the pharmacy series (Heavy Hand later joins this table to the dispenses/prescribers).

## Flag

```
deadface{9}
```
