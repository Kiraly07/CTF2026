# Cereal Killer 02 — Reverse Engineering (150 pts)

A 7z that opens with password **KlippyAI** (contents: the Linux binary, a Windows one, and a "surprise" KlippyAI .NET exe — I never ran that, static analysis of the Linux ELF was enough).

## How I solved it

`re03-lin-x86.bin` copies two blobs to the stack: 257 bytes ("key") and 256 bytes ("ciphertext"), then computes `out[i] = key[i] ^ blob[i]` and searches for the magic marker "badf00d". With the shipped key it fails and the binary taunts you: *"TIME is REVERSIBLE, but the KEY is NOT... Go Back!"*

So reverse it: XOR `key[i] ^ blob[255-i]` instead. That yields clean ASCII art (241/256 printable):

```
* f e e d . . .*
* f a c e . . .*
* d e a d b eef*
* d e a d . . .*
* f a c e { . .*
* N 0 r d i c s*
...
* badf00d......*
```

Strip the filler spaces/dots/asterisks and the art literally spells the flag.

## Flag

```
deadface{N0rdics-R3ally-like-Frank3nb3rry-cuz-bro-is-tall-like-they-are!}
```
