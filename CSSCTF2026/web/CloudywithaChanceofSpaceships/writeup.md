---
title: "Cloudy with a Chance of Spaceships"
ctf: "CSSCTF"
date: 2026-10-01
category: web
flag_format: "CSSCTF{...}"
---

The ship temperature endpoint fetches a URL from the `X-Resolver` header. The frontend JS at `/_app/immutable/nodes/2.CftUi-UM.js` has the default header value:

```js
const e = "XeyJyZXNvbHZlciI6Imh0dHBzOi8vZW4ud2lraXBlZGlhLm9yZy93aWtpL1NwYWNlX3dlYXRoZXIifQ==";
fetch(`/api/v1/ship/${encodeURIComponent(r)}/temperature`, { headers: { "X-Resolver": e } });
```

Drop the leading `X` and Base64-decode it to get `{"resolver":"https://en.wikipedia.org/wiki/Space_weather"}`. The endpoint returns response-body length divided by 10 (`https://example.com/` returned `71.3`), so I replaced the resolver with a callback URL and captured the outbound request's `Authorization: Bearer ...` token. Its tokeninfo showed `cloud-platform` scope for `meteorologist@css-ctf-2026.iam.gserviceaccount.com`, project `613713115850`. Metadata endpoints did not work because the fetch did not send `Metadata-Flavor: Google`.

Use the captured token with Secret Manager. Storage and Compute access were denied, but this secret was readable:

```text
GET /v1/projects/613713115850/secrets
-> goog_encryption_secret

GET /v1/projects/613713115850/secrets/goog_encryption_secret/versions/latest:access
-> payload.data = Q1NTQ1RGe3lvdXJfZm9yZWNhc3Rfc2F5c19sb3ZlX2lzX29uX2l0c193YXl9
```

My `solve.py` serves the callback on port 8888, triggers the request to `/api/v1/ship/Voyager%201/temperature`, then fetches and decodes the secret. Start a tunnel to port 8888 and set `CALLBACK` to its public URL first.

## Flag

```text
CSSCTF{your_forecast_says_love_is_on_its_way}
```
