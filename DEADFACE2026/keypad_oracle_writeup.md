# Keypad Oracle — Mobile (200 pts)

The download unzips to a macOS app bundle (`Keypad-Oracle.app`, an iOS simulator build). The main binary is a SwiftUI stub — the real logic is in `Keypad-Oracle.debug.dylib`.

## How I solved it

Reversed `PinCipherEngine` from the ARM64 disassembly (radare2). The pieces:

- `KeypadConfig.json` maps each digit 0-9 to a 27-byte hex seed
- `binarySalt = 3a91442fd0186bc3720ea95d11be8027f466399a05cc701b8842e153`
- output length 27, and per position:

```
derive(seed, digit, pos)[i] =
    rotl8(seed[i%27] ^ ((pos+1)*33 & 0xff) ^ (digit*19 & 0xff) ^ (i*7 & 0xff),
          (digit+pos+i) % 8) ^ ((i + digit + 11*pos) & 0xff)

encode(pin): acc = 27 zero bytes
    for pos in 0..3: acc = xor(acc, derive(seedTable[pin[pos]], pin[pos], pos))
    acc = xor(acc, binarySalt); return hex(acc)
```

The kicker: the app has **no comparison logic at all** — it's an "oracle" that just shows you encode() output. So the encoded output of the *correct* PIN is the flag itself.

Brute-forced all 5040 four-digit permutations (no repeated digits — the UI only accepts unique ones). Exactly one output is printable ASCII: PIN **3719** → `deadface{your-pin-is-valid}`.

## Flag

```
deadface{your-pin-is-valid}
```
