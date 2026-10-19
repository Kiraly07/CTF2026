# Prying Eyes — Database (55 pts)

Aurora Health series. Someone's been snooping on a VIP patient. Challenge 18 gave us the VIP's MRN: **AH-0044719**.

## How I solved it

There's a MySQL shell into the Aurora environment (I used a ttyd websocket client to reach it). The audit database does the work:

```sql
SELECT user_id, COUNT(*) FROM aurora_audit.access_log
WHERE patient_mrn = 'AH-0044719'
GROUP BY user_id;
```

One account blows everyone else away: user_id 10 opened the VIP chart **47 times** (next highest: 5). Looking up user_id 10 in `aurora_audit.users`:

- **rborden** — Rebecca Borden, HIM clerk
- handler_ref: REVENANT-7 (worth noting for the storyline)

## Flag

```
deadface{rborden}
```
