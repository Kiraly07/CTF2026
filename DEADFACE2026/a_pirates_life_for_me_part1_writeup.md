# A Pirate's Life for Me: Part 1 — Traffic Analysis (25 pts)

We got a pcap from a university cafe, and the description drops a weird detail: the barista saw someone using "a browser they've never seen before". That's basically a flashing sign saying *check the User-Agents*.

## How I solved it

After extracting the 7z (~500MB compressed), I listed all HTTP User-Agents:

```
tshark -r pirateslife.pcap -Y http.request -T fields -e http.user_agent | sort | uniq -c
```

Almost everything was boring except one client at 172.16.14.43 running:

```
SunstalkerDFBrower/2.0 (Linux; Android 14)
```

(Yeah, "Brower". Nice typo.)

So I pulled every request from that client:

```
tshark -r pirateslife.pcap -Y 'http.user_agent contains "Sunstalker"' \
  -T fields -e http.host -e http.request.line
```

The flag wasn't in any response — it was smuggled in **custom request headers**, split into three pieces and sent to three different sites (the ones DEADFACE had breached):

- `X-1-Trace-Part: deadface{X-M4rk5_` → nightvaleuniversity.edu
- `X-2-Mark: th3_sp0t_` → aurorahhs.com
- `X-3-Spot: I_gu355}` → birdsarejustbirds.gov

Concatenate them and you get "X marks the spot, I guess" in leetspeak.


## Flag

```
deadface{X-M4rk5_th3_sp0t_I_gu355}
```
