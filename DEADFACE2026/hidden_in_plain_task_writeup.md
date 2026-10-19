# Hidden in Plain Task — De Monne Breach (75 pts)

The attacker left persistence on Nathan's workstation: a registered scheduled task. What's its exact name?

## How I solved it

The attacker's PowerShell console history/transcript blob survives in memory (a big chunk at byte offset ~1.3GB in the image, mirrored a couple of times). It contains the whole registration sequence, verbatim:

```powershell
$action = New-ScheduledTaskAction -Execute 'powershell.exe' \
    -Argument '-NoProfile -File C:\ProgramData\WindowsCache\telemetry.ps1'
$trigger = New-ScheduledTaskTrigger -Daily -At '23:59'
$principal = New-ScheduledTaskPrincipal -UserId 'SYSTEM' -LogonType ServiceAccount -RunLevel Highest
Register-ScheduledTask -TaskName 'WindowsTelemetryCheck' -Action $action -Trigger $trigger -Principal $principal -Force
Start-ScheduledTask -TaskName 'WindowsTelemetryCheck'
```

The task is called **WindowsTelemetryCheck** — dressed up as a Windows telemetry job, running daily at 23:59 as SYSTEM.

One warning if you're grepping memory yourself: tons of "schtasks" and "net use" hits in the image are just Windows Defender signature strings, not attacker activity. The transcript blob stands out because it has the attacker's actual commands next to each other.

## Flag

```
deadface{WindowsTelemetryCheck}
```
