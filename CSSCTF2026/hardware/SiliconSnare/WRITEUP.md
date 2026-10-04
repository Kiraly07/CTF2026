# SiliconSnare — Writeup

**Flag:** `CSSCTF{01010000010000010101001101010011}`

## Challenge

Optical routing matrix drawn as a Matplotlib SVG (`schematic.svg` / `schematic.png`). Trace wires through proprietary gates to find the unique 32-bit input that drives the centre **OVERRIDE** node high. Submit bits clockwise from `I00` (12 o’clock) through `I31`.

## Legend (from sheet)

| Gate   | Function |
|--------|----------|
| Flow `f**` | `Y = A AND B` |
| Negate `n**` | `Y = NOT A` |
| Merge `m**` | `Y = A XOR B` |
| Shift `s**` | pointed end: `A` in / `Y0=A OR B` out; flat end: `B` in / `Y1=A AND NOT B` out |

Filled coloured dots are fan-out nodes (same net).

## Method

1. Parse SVG `line2d_*` coloured paths and `patch_*` gate polygons.
2. Map input stub colours → `I00..I31` by angle around the ring centre.
3. Outer ring: each merge `m{j}` = `I[j] XOR I[(j+7) mod 32]`.
4. Trace internal nets by endpoint proximity to gate patches.
5. For each shift, classify tip (sharp vertex) vs flat (opposite); attach inputs/outputs to the nearest edge. Tip-side output ⇒ `Y0`; flat-side output ⇒ `Y1`.

### Shift polarity used

- **Y1** (flat out): `s00,s01,s02,s03,s04,s05,s09,s0b,s0c`
- **Y0** (tip out): `s06,s07,s08,s0a`

## Netlist (condensed)

```
m[j] = I[j] ⊕ I[(j+7)%32]

f00 = m08 ∧ m18
s00 = m10 ∧ ¬m00          # Y1
f01 = s00 ∧ f00
f02 = m0c ∧ m1c
s01 = m14 ∧ ¬m04          # Y1
s02 = s01 ∧ ¬f02          # Y1
m20 = s01 ⊕ s02
f03 = m20 ∧ f01
f04 = m02 ∧ m12
f05 = m0a ∧ m1a
s03 = f04 ∧ ¬f05          # Y1
m21 = s03 ⊕ f04
s04 = m16 ∧ ¬m06          # Y1
s05 = m1e ∧ ¬m0e          # Y1
f06 = s04 ∧ s05
f07 = f06 ∧ m21
f08 = f03 ∧ f07
f09 = m01 ∧ m11
f0a = m09 ∧ m19
n00 = ¬f09 ; n01 = ¬f0a
s06 = n00 ∨ n01           # Y0
n02 = ¬s06
s07 = m05 ∨ m15           # Y0
n03 = ¬s07
s08 = m0d ∨ m1d           # Y0
n04 = ¬s08
f0b = n03 ∧ n04
f0c = f0b ∧ n02
f0d = m03 ∧ m13
s09 = m1b ∧ ¬m0b          # Y1
f0e = s09 ∧ f0d
s0a = m07 ∨ m17           # Y0
n05 = ¬s0a
s0b = m1f ∧ ¬m0f          # Y1
s0c = n05 ∧ ¬s0b          # Y1
m22 = s0c ⊕ n05
f0f = m22 ∧ f0e
f10 = f0f ∧ f0c
f11 = f08 ∧ f10
f12 = I01 ∧ I03           # direct inputs
f13 = f12 ∧ f11
OVERRIDE = f13
```

Also: `f04` fans out into both `s03` and `m21`; `n05` fans into both `s0c` and `m22`.

## Solving

Require `OVERRIDE=1` and push constraints backward through the ANDs / forced shift outputs. That yields a complete set of forced merge values (XORs of input pairs). Propagating those linear equations with `I01=I03=1` fixes every bit:

```
I = 01010000010000010101001101010011
```

Forward evaluation confirms `OVERRIDE=1`. No other assignment satisfies the forced system.

## Flag

```
CSSCTF{01010000010000010101001101010011}
```
