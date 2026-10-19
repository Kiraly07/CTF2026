# Looking Back — Hostbusters (30 pts)

*Note: Charon was reset for the final wave — same solve, new flag text (the original flag was `deadface{h1st0ry_r3m3mb3rs_4ll}`).*

Same Charon box (the disposable web shell at hostbusters.dctf.io, landing as svc-deploy). "The DEADFACE member who used the svc-deploy account last was sloppy. Access one of their accounts and read the flag in their home directory."

## How I solved it

"Looking back" = look at the shell history. The service account's home has a `.bash_history` sitting right there:

```
charon:~$ cat ~/.bash_history
...
deephax : Sk4t3rB0y_S1nce_2011
```

Somebody typed their real login into the service account's shell and it stuck in history. Since every web-shell session is a fresh copy, re-run everything in one session:

```
charon:~$ su - deephax
Password: <REDACTED_CTF_PASSWORD>
deephax@charon:~$ ls
flag.txt  notes.txt  kingmaker-scraper/
deephax@charon:~$ cat ~/flag.txt
```

History remembers all — that's exactly what the flag says.

(A GhostTown thread about mort1cia's past is a red herring for this one — it feeds a later challenge in the series, not this.)

## Flag

```
deadface{sh3ll_h1st0ry_t3lls_4ll}
```
