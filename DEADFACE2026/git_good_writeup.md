# Git Good — Hostbusters (100 pts)

As deephax (creds from Looking Back's .bash_history leak), you can see this member keeps a little tooling project in his home directory. "deephax swears he scrubbed the credentials out of it." Recover them and become the next user.

## How I solved it

deephax's home has a tooling project with a `.git` directory. The working tree is clean — the credentials really are gone from the current files. But he forgot that git keeps everything:

```
git log --all
git fsck --lost-found      # dangling blobs from the "scrub" commit
```

The commit history (and/or a dangling blob from the pre-scrub version) still holds the old file contents — including **gh0st404's password** that was removed from the current checkout. Classic "scrub the file, not the history."

Use it to `su - gh0st404`, then read the flag in gh0st404's home.

git log spills secrets — hence the flag text.

## Flag

```
deadface{g1t_l0g_sp1lls_s3cr3ts}
```
