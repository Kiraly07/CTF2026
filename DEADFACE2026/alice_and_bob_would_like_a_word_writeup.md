# Alice and Bob Would Like a Word — OSINT (75 pts)

The description rants about privacy and ends with "why on earth would you just leave your keys out in the open like that?" Combined with the Alice & Bob naming, this screams *keys*. And the odd flag format note (Z and Y instead of { and }) tells you the flag is embedded in something that can't contain literal curly braces — like an SSH key blob.

## How I solved it

The companion challenge here is "The Vibes Are Freaking Me Out" (chal 65), which leads you to b1tfr34k's HIPS browser extension on GitHub (user `fr34ked0ut`). Once you're on that profile, the "keys out in the open" line clicks: GitHub exposes public SSH keys at

```
https://github.com/<user>.keys
```

So:

```
curl https://github.com/fr34ked0ut.keys
```

Six keys come back. The fifth one looks like a normal ed25519 key, but its base64 tail is doing something weird:

```
...AAAAC3NzaC1lZDI1NTE5AAAAIDdpiFW3mHOZbTkfndeadfaceZPubM34n5Publ1cDuHY
```

There it is: `deadfaceZ...Y`. Swap `Z` → `{` and the trailing `Y` → `}` exactly like the description says, and you're done. "Pub means public, duh."

## Flag

```
deadface{PubM34n5Publ1cDuH}
```
