# The Typo That Bit — De Monne Breach (75 pts)

Nathan's workstation tried to reach the executive share through a misspelled server name. Find the mistyped hostname in memory.

## How I solved it

The legit file server is `dmf-field-01` (share `executive`). Hunting the UTF-16 strings around the share traffic, the typo shows up 86 times:

```
rundll32.exe C:\Windows\system32\davclnt.dll,DavSetCookie dmf-fiels-01 http://dmf-fiels-01/executive
\\dmf-fiels-01\exec
Enter your credentials to connect to: dmf-fiels-01
dmf-fiels-01.local   (plus HTTP/dmf-fiels-01.local SPNs)
```

**`dmf-fiels-01`** — the "ie" is transposed. You can even see the correct and wrong forms sitting 400 bytes apart in memory (DavSetCookie dmf-fiels-01 at one offset, dmf-field-01 right after it).

That typo matters because the poisoned-name game from Uninvited Guest works best when the real server never answers — a misspelled name never resolves legitimately, so whatever answers it is the attacker.

## Flag

```
deadface{dmf-fiels-01}
```
