# Info Leaks — Aurora Patient Zero (25 pts)

Aurora Health is getting hit by highly targeted phishing against its patients. Where's the attacker getting accurate patient info?

## How I solved it

The challenge isn't a hosted web app — the CTFd page links a 2.5MB IPA:

```
AuroraPatientPortal.ipa.zip → Payload/aurora-patient-portal.app/
```

The app bundle contains the Mach-O binary, `Info.plist`, `aurora_meds.sqlite`, and a chest X-ray JPEG. The leak is right in `Info.plist` — a custom key `AuroraPatientBootstrap` holding base64'd JSON:

```json
{"patientName":"Mare Voss","dateOfBirth":"1988-04-17","clinic":"Westlake"}
```

The binary's Swift symbols (`PatientBootstrap`, `patientName`, `displayDateOfBirth`) confirm the app decodes this at runtime — it's a baked-in record of the last patient this build was configured for. Anyone who gets the IPA has name, DOB, and clinic: exactly the ingredients for the convincing spear-phishing wave Aurora's been seeing.

## Flag

```
deadface{mare-voss-1988-04-17}
```
