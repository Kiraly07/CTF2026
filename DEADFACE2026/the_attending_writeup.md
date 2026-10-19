# The Attending — Database (40 pts)

The VIP patient (is_vip = 1) had exactly one inpatient admission in November 2025. Which physician signed off on that stay?

## How I solved it

Three-table chain in `aurora_ehr`: patients (find the VIP) → encounters (the November 2025 admission) → providers (the attending's username).

```sql
SELECT e.encounter_id, e.encounter_type, e.department, e.admit_date, e.discharge_date,
       pr.first_name, pr.last_name, pr.username
FROM encounters e
JOIN providers pr ON pr.provider_id = e.attending_provider_id
WHERE e.patient_id = (SELECT patient_id FROM patients WHERE is_vip = 1)
  AND e.admit_date >= '2025-11-01' AND e.admit_date < '2025-12-01'
  AND e.encounter_type = 'Inpatient';
```

One row:

```
encounter 5017 | Inpatient | Pain Clinic | admit 2025-11-14, discharge 2025-11-17
attending: Marcus Reyes (provider_id 5), username: mreyes, specialty: Pain Management
```

A cross-check without the encounter_type filter confirms it's the VIP's only November encounter.

Remember that name — mreyes keeps showing up across the whole Aurora storyline (he's the star of Heavy Hand and The Original Reading).

## Flag

```
deadface{mreyes}
```
