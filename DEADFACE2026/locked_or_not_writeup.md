# Locked... or Not? — Mobile (150 pts)

A tiny APK (`df-securenotes.apk`, ~11KB) with a "secure notes" app. The note dialog shows "Access denied" no matter what password you type.

## How I solved it

jadx decompiles it in seconds — only three classes. The password check in the note dialog is fake: it always denies. But `MainActivity` has an unused method, `getSecureBackupText()`, with a hardcoded Base64 string:

```
ZGVhZGZhY2V7ZXotbW9iaWxlLXRvLXN0YXJ0fQ==
```

Decode it:

```
deadface{ez-mobile-to-start}
```

Never even had to run the app. The lock screen is theater — the backup text is the flag.

## Flag

```
deadface{ez-mobile-to-start}
```
