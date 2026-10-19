# It But A Wee Bit Reverse — Reverse Engineering (15 pts)

A small x86-64 ELF, not stripped, built from `crackme2.c`.

## How I solved it

Two symbols do all the work: `pw_enc` at 0x4010 and `flag_enc` at 0x4020. `main` checks:

- `strlen(input) == 10`
- `input[i] ^ 0x42 == pw_enc[i]` for every i

`pw_enc` is `"17,1*+,'vp"` — XOR each byte with 0x42 and you get the password: **sunshine42**.

After that, the flag is just `flag_enc[i] ^ password[i % 10]` — the password doubles as the key. Easiest way to confirm:

```
echo "sunshine42" | ./80_rev_binary
```

## Flag

```
deadface{x0r_1s_not_encryption}
```
