# Heavy Hand — Database (100 pts)

Aurora Health, part three: which prescriber is handing out way too many Schedule II drugs, and what's their DEA number?

## How I solved it

One join across the pharmacy tables — dispenses, prescriptions, drugs, prescribers:

```sql
SELECT pr.dea_number, SUM(d.quantity_dispensed) AS total
FROM dispenses d
JOIN prescriptions rx ON rx.rx_id = d.rx_id
JOIN drugs dr        ON dr.drug_id = rx.drug_id
JOIN prescribers pr  ON pr.prescriber_id = rx.prescriber_id
WHERE dr.dea_schedule = 'II'
  AND d.dispensed_at BETWEEN '2025-10-01' AND '2025-12-31'
GROUP BY pr.prescriber_id
ORDER BY total DESC;
```

The numbers aren't close: **mreyes (Marcus Reyes), DEA BR2938471, total 5220 units** of Schedule II drugs in one quarter. The next prescriber dispensed 150. Same mreyes who falsified the Veltrexa endpoint in The Original Reading.

## Flag

```
deadface{BR2938471}
```
