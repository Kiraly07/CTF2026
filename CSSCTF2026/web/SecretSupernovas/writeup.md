---
title: "SecretSupernovas"
ctf: "CSSCTF"
date: 2026-09-30
category: web
flag_format: "CSSCTF{...}"
---

`/` redirects to `/login`; the page hints at `cadet/star`. After logging in, the SvelteKit app sends a GraphQL query to `POST /graphql` for the stars' public fields. Introspection shows `Star.owner` has a `Person.description`, so I requested that field too. The flag is in the owner description for star id 5, “Black Canary” (Laurel Lance). The “Secret Supernova” is star id 11 in the Whirlpool galaxy, but it is not where the flag is stored.

```graphql
query {
  stars {
    id
    name
    owner { id first_name last_name description }
  }
}
```

Log in with `username=cadet&password=star`, keep the returned `session` cookie, and send the query to `/graphql`.

## Flag

```text
CSSCTF{we_l000ve_grafs}
```
