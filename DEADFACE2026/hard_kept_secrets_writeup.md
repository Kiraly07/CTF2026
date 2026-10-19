# Hard Kept Secrets — De Monne Slayer (20 pts)

The De Monne Financial APK hides an internal API token. Straight decompilation almost works — emphasis on *almost*.

## How I solved it

jadx shows `com.demonne.financial.api.ApiClient` with an `INTERNAL_API_TOKEN` constant... that jadx renders as 64 asterisks. jadx 1.5.5 redacts long secrets in its output, so the decompiled source is useless here.

Workaround: parse the `classes.dex` **string pool directly** (uleb128-length prefixed strings). There's exactly one 64-char base64-looking secret in the pool. Confirmed it's the right one by checking the dex reference: a `const-string/jumbo` instruction in ApiClient's `<clinit>` pulls it and hands it to an `InternalTokenInterceptor`, which sends it as the `X-Internal-Token` header.

Watch out for decoys in the same APK: `deadface{Ur_N0t_A110wEd_h3r3}` in SecureVaultActivity and `deadface{flaG_ManIfesT3d}` in DiagnosticActivity are NOT this challenge (that last one is the answer to Diagnosis).

## Flag

```
deadface{zqJRlVwBA9Xm2lE5EPjgbj/4rOxlkYZgDtkdP7jV80rZgLFrlnOEn+VAu31YKQrR}
```
