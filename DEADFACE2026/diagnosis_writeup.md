# Diagnosis — De Monne Slayer (100 pts)

Same De Monne APK. The developer suspected a "hidden activity due to manifest misconfiguration". He was right.

## How I solved it

Decoding `AndroidManifest.xml`, there it is:

```xml
<activity android:name="com.demonne.financial.internal.DiagnosticActivity"
          android:exported="true" android:label="Diagnostics"/>
```

It's an internal activity with **no UI path** — no Intent anywhere in the app starts it — but it's exported, so any app (or adb) could reach it.

`DiagnosticActivity.onCreate()` renders a diagnostic screen into `tvDiagOutput`, and the decompiled source shows exactly what it displays:

```
diagnostic.code : deadface{flaG_ManIfesT3d}
```

No need to even run the app.

## Flag

```
deadface{flaG_ManIfesT3d}
```
