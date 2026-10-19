# Chatty Cathy — OSINT (15 pts)

Find what lamia415 is blabbing about on GhostTown.

## How I solved it

GhostTown thread 20 ("Travel Destinations") has lamia415 linking her travel blog — *"Wander with Alice"* at https://170.187.156.131:8443/ (pseudonym Alice).

First I checked the TLS cert (classic mistake) — it has a flag-looking string in the Org field: `Deadface{c@tch_m3_if_y0u_c@n}`. That one gets rejected. Decoy.

The real flag is in `robots.txt`:

```
User-agent: *
Disallow: /secret_members
# deadface{y0u_m3ddling_k!ds}
```

Bonus: the cert also leaks her real email, alicehankerty@gmail.com (Alice Hankerty) — that intel comes in handy for other challenges.

## Flag

```
deadface{y0u_m3ddling_k!ds}
```
