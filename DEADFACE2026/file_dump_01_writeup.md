# File Dump 01 — Steganography (10 pts)

The ZIP has someone's personal documents (notes.docx, resume.docx, reminders.docx). We need the DEADFACE alias of whoever exfiltrated them.

## How I solved it (including the trap)

The obvious first move is the OOXML metadata: `docProps/core.xml` in each file says

```
creator: ghostwriter404
lastModifiedBy: GHOST404-PC
```

I submitted `deadface{ghostwriter404}` — **rejected**, three times. The metadata spelling is a decoy.

The actual DEADFACE alias is their **GhostTown forum handle**. Checking the forum member list, there's a member `gh0st404` (zero instead of 'o', matching the machine name GHOST404-PC) with 84 posts in the Havoc threads. That's the alias.

## Flag

```
deadface{gh0st404}
```
