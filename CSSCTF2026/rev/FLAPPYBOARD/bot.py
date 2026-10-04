#!/usr/bin/env python3
"""FLAPPY BOARD deterministic physics bot + API client."""

from __future__ import annotations

import argparse
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

BASE = "http://34.116.80.78:8765"

GRAVITY = 0x43
FLAP_VY = -0x6BC  # 0xfffff944
MAX_VY = 0x800
PIPE_DX = 0x2CD
PIPE_STEP = 0x10E
PIPE_BASE = 0x410
GAP_HALF = 0x57
Y_MIN = 0xC00
Y_MAX = 0x1D3FF
SCORE_X = 0x77FF
COLLIDE_LO = 0x7800
COLLIDE_HI = 0xD3FF
BIRD_HALF = 0xBFF
TICK_CAP = 0x8C9F
RECYCLE_X = -0x4400


def xorshift32(state: int) -> int:
    state &= 0xFFFFFFFF
    state ^= (state << 13) & 0xFFFFFFFF
    state ^= (state >> 17) & 0xFFFFFFFF
    state ^= (state << 5) & 0xFFFFFFFF
    return state & 0xFFFFFFFF


def rand_gap(state: int) -> Tuple[int, int]:
    state = xorshift32(state)
    return state, (state % 0xE7) + 0x7D


def to_signed32(x: int) -> int:
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x >= 0x80000000 else x


@dataclass
class Pipe:
    x: int
    gap: int
    scored: bool = False


@dataclass
class Game:
    y: int = 0xF000
    vy: int = 0
    score: int = 0
    ticks: int = 0
    dead: bool = False
    rng: int = 1
    pipes: List[Pipe] = field(default_factory=list)

    @classmethod
    def from_seed(cls, seed: int) -> "Game":
        g = cls(rng=(seed & 0xFFFFFFFF) or 1)
        for i in range(5):
            x = ((i * PIPE_STEP) + PIPE_BASE) << 8
            g.rng, gap = rand_gap(g.rng)
            g.pipes.append(Pipe(x=x, gap=gap))
        return g

    def clone(self) -> "Game":
        g = Game(
            y=self.y,
            vy=self.vy,
            score=self.score,
            ticks=self.ticks,
            dead=self.dead,
            rng=self.rng,
        )
        g.pipes = [Pipe(p.x, p.gap, p.scored) for p in self.pipes]
        return g

    def step(self, do_flap: bool = False) -> bool:
        if self.dead or self.ticks > TICK_CAP:
            self.dead = True
            return False

        if do_flap:
            self.vy = FLAP_VY

        self.vy += GRAVITY
        if self.vy > MAX_VY:
            self.vy = MAX_VY

        self.y = (self.y + self.vy) & 0xFFFFFFFF
        self.ticks += 1

        for p in self.pipes:
            p.x = (p.x - PIPE_DX) & 0xFFFFFFFF

        y = self.y
        if y <= Y_MIN or y > Y_MAX:
            self.dead = True

        old_score = self.score
        for p in self.pipes:
            px = to_signed32(p.x)
            # collision window uses unsigned compares in asm:
            # cmp x, 0xd3ff; jg skip; cmp x, 0x7800; jle skip
            if p.x <= COLLIDE_HI and p.x > COLLIDE_LO:
                gap_lo = (p.gap - GAP_HALF) << 8
                gap_hi = (p.gap + GAP_HALF) << 8
                bird_lo = (self.y - BIRD_HALF) & 0xFFFFFFFF
                bird_hi = (self.y + BIRD_HALF) & 0xFFFFFFFF
                if not (bird_lo > gap_lo and bird_hi < gap_hi):
                    self.dead = True

            if (not p.scored) and p.x <= SCORE_X:
                p.scored = True
                if not self.dead:
                    self.score += 1

        # recycle
        for p in self.pipes:
            if to_signed32(p.x) < RECYCLE_X:
                max_x = max(to_signed32(q.x) for q in self.pipes)
                new_x = (max_x + 0x10E00) & 0xFFFFFFFF
                self.rng, gap = rand_gap(self.rng)
                p.x = new_x
                p.gap = gap
                p.scored = False

        return self.score != old_score


def survives(g: Game, flaps_ahead: List[bool], horizon: int) -> bool:
    s = g.clone()
    for i in range(horizon):
        flap = flaps_ahead[i] if i < len(flaps_ahead) else False
        s.step(flap)
        if s.dead:
            return False
    return True


def would_die_without_flap(g: Game, horizon: int = 90) -> bool:
    s = g.clone()
    for _ in range(horizon):
        s.step(False)
        if s.dead:
            return True
        # if we cleared the next pipe scoring line, short-circuit success for horizon
    return False


def nearest_pipe(g: Game) -> Optional[Pipe]:
    best = None
    for p in g.pipes:
        # pipe still relevant if not far past bird
        if to_signed32(p.x) > -0x2000:
            if best is None or to_signed32(p.x) < to_signed32(best.x):
                # prefer pipes still ahead of score line or in collision
                if p.x > 0x4000 or not p.scored:
                    if best is None or p.x < best.x:
                        best = p
    # fallback: minimum positive-ish x
    if best is None:
        for p in g.pipes:
            if best is None or to_signed32(p.x) < to_signed32(best.x):
                best = p
    return best


def solve(seed: int, target: int, max_ticks: int = 25000) -> Optional[Tuple[List[int], int, int]]:
    """Greedy controller: flap when coasting dies within horizon, with gap aiming."""
    g = Game.from_seed(seed)
    flaps: List[int] = []

    while not g.dead and g.score < target and g.ticks < max_ticks:
        pipe = nearest_pipe(g)
        do_flap = False

        # Predict: if we never flap, do we die soon?
        # Also aim: if bird center is below (gap - bias), flap.
        if pipe is not None:
            gap_center = pipe.gap << 8
            # y increases downward; want y near gap_center
            # flap if too low (y too large) relative to gap, especially when approaching
            dist = to_signed32(pipe.x) - COLLIDE_HI
            ticks_to_col = max(0, dist // PIPE_DX) if dist > 0 else 0

            # Simulate coasting until pipe collision zone / a bit beyond
            horizon = min(120, ticks_to_col + 40)
            coast = g.clone()
            dies_coast = False
            min_clearance = 10**9
            for h in range(horizon):
                coast.step(False)
                if coast.dead:
                    dies_coast = True
                    break
                # track clearance vs this pipe if in window
                for p in coast.pipes:
                    if p.x <= COLLIDE_HI and p.x > COLLIDE_LO and abs(p.gap - pipe.gap) < 2:
                        bird_lo = (coast.y - BIRD_HALF) & 0xFFFFFFFF
                        bird_hi = (coast.y + BIRD_HALF) & 0xFFFFFFFF
                        gap_lo = (p.gap - GAP_HALF) << 8
                        gap_hi = (p.gap + GAP_HALF) << 8
                        clear = min(bird_lo - gap_lo, gap_hi - bird_hi)
                        min_clearance = min(min_clearance, clear)

            # If coasting dies, see if flapping NOW helps
            if dies_coast:
                with_flap = g.clone()
                with_flap.step(True)
                # check if immediate flap + coast survives longer / lives
                alive = True
                for _ in range(min(30, horizon)):
                    with_flap.step(False)
                    if with_flap.dead:
                        alive = False
                        break
                # flap if it helps, or if we're below gap
                if alive or g.y > gap_center:
                    do_flap = True

            # Proactive aiming when approaching pipe
            if ticks_to_col < 80:
                # target slightly above center (smaller y)
                target_y = gap_center - (6 << 8)
                if g.y > target_y and g.vy >= 0:
                    # falling / below target
                    do_flap = True
                elif g.y > gap_center + (GAP_HALF - 20) << 8:
                    do_flap = True

            # Don't flap if too high (near ceiling relative to gap)
            if g.y < gap_center - ((GAP_HALF - 15) << 8) and ticks_to_col < 50:
                # only suppress if coasting is safe for a bit
                probe = g.clone()
                safe = True
                for _ in range(15):
                    probe.step(False)
                    if probe.dead:
                        safe = False
                        break
                if safe:
                    do_flap = False
        else:
            if g.y > 0x14000 and g.vy > 0:
                do_flap = True

        # Ceiling protection: never flap if very high
        if g.y < 0x3000:
            do_flap = False
        # Floor emergency
        if g.y > 0x1A000:
            do_flap = True

        if do_flap:
            flaps.append(g.ticks)
        g.step(do_flap)

        if g.score >= target and not g.dead:
            return flaps, g.score, g.ticks

    if g.score >= target and not g.dead:
        return flaps, g.score, g.ticks
    return None


def solve_search(seed: int, target: int, max_ticks: int = 30000) -> Optional[Tuple[List[int], int, int]]:
    """Better solver: at each tick, flap iff not flapping leads to death before
    next pipe is cleared, while flapping does not immediately die."""
    g = Game.from_seed(seed)
    flaps: List[int] = []

    def death_in(state: Game, n: int, first_flap: bool = False) -> int:
        s = state.clone()
        for i in range(n):
            s.step(first_flap if i == 0 else False)
            if s.dead:
                return i
        return n

    while not g.dead and g.score < target and g.ticks < max_ticks:
        pipe = nearest_pipe(g)
        horizon = 100
        if pipe is not None:
            dist = to_signed32(pipe.x) - 0x6000
            horizon = max(40, min(150, dist // PIPE_DX + 50))

        die_coast = death_in(g, horizon, False)
        die_flap = death_in(g, horizon, True)

        do_flap = False
        if die_coast < horizon:
            # will die if we coast; flap if that improves
            if die_flap > die_coast:
                do_flap = True
            elif die_flap == die_coast and pipe is not None:
                # both die same time — flap if below gap
                if g.y > (pipe.gap << 8):
                    do_flap = True
        else:
            # safe for horizon; still aim toward gap when close
            if pipe is not None:
                ticks_to = max(0, (to_signed32(pipe.x) - COLLIDE_HI) // PIPE_DX)
                if ticks_to < 70:
                    target_y = (pipe.gap - 8) << 8
                    # flap if below target and not rising fast
                    if g.y > target_y and g.vy > -0x200:
                        # ensure flap doesn't kill sooner
                        if die_flap >= min(20, die_coast):
                            do_flap = True

        if g.y < 0x2800:
            do_flap = False
        if g.y > 0x1A800:
            do_flap = True

        if do_flap:
            flaps.append(g.ticks)
        scored = g.step(do_flap)
        if g.score >= target and not g.dead:
            return flaps, g.score, g.ticks

    if not g.dead and g.score >= target:
        return flaps, g.score, g.ticks
    return None


def verify_local(seed: int, flaps: List[int], target: int) -> Tuple[int, int, bool]:
    flap_set = set(flaps)
    g = Game.from_seed(seed)
    while not g.dead and g.score < target and g.ticks < 40000:
        g.step(g.ticks in flap_set)
    return g.score, g.ticks, g.dead


def http_post(path: str, body: str = "", token: Optional[str] = None) -> Tuple[int, str]:
    url = BASE + path
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    data = body.encode() if body is not None else b""
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()


def parse_form(s: str) -> dict:
    out = {}
    for part in s.split("&"):
        if not part or "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k] = urllib.parse.unquote_plus(v)
    return out


def solve_beam(seed: int, target: int, beam_width: int = 80, max_depth_per: int = 600) -> Optional[Tuple[List[int], int, int]]:
    """Beam search pipe-by-pipe until target score."""
    g = Game.from_seed(seed)
    all_flaps: List[int] = []
    while g.score < target and not g.dead:
        start_score = g.score
        beam: List[Tuple[Game, List[int]]] = [(g.clone(), [])]
        found = None
        for _ in range(max_depth_per):
            new_beam: List[Tuple[Game, List[int]]] = []
            seen = set()
            for state, fl in beam:
                for do in (False, True):
                    s = state.clone()
                    flaps = fl + ([s.ticks] if do else [])
                    s.step(do)
                    if s.dead:
                        continue
                    key = (s.y, s.vy, s.score, tuple(p.x for p in s.pipes))
                    if key in seen:
                        continue
                    seen.add(key)
                    if s.score > start_score:
                        found = (flaps, s)
                        break
                    new_beam.append((s, flaps))
                if found:
                    break
            if found:
                break
            if not new_beam:
                return None

            def rank(item: Tuple[Game, List[int]]):
                s, _ = item
                up = None
                for p in s.pipes:
                    if not p.scored:
                        if up is None or to_signed32(p.x) < to_signed32(up.x):
                            up = p
                if up is None:
                    return (abs(s.y - 0xF000),)
                return (abs(s.y - (up.gap << 8)), abs(s.vy), to_signed32(up.x))

            new_beam.sort(key=rank)
            beam = new_beam[:beam_width]
        if not found:
            return None
        fl, g = found
        all_flaps.extend(fl)
    if g.dead or g.score < target:
        return None
    return all_flaps, g.score, g.ticks


def try_solve(seed: int, target: int) -> Optional[Tuple[List[int], int, int]]:
    for bw in (80, 120, 200, 300):
        sol = solve_beam(seed, target, beam_width=bw)
        if not sol:
            continue
        flaps, score, ticks = sol
        s2, t2, dead = verify_local(seed, flaps, target)
        if s2 >= target and not dead:
            return flaps, s2, t2
    for fn in (solve_search, solve):
        sol = fn(seed, target)
        if not sol:
            continue
        flaps, score, ticks = sol
        s2, t2, dead = verify_local(seed, flaps, target)
        if s2 >= target and not dead:
            return flaps, s2, t2
    return None


def practice_test(target: int = 10) -> None:
    code, body = http_post("/api/attempt")
    print("attempt", code, body)
    form = parse_form(body)
    token = form["token"]
    code, body = http_post("/api/practice", "", token)
    print("practice", code, body)
    form = parse_form(body)
    ptoken = form["token"]
    seed = int(form["seed"])
    print("seed", seed)
    sol = try_solve(seed, target)
    print("sol", None if not sol else (len(sol[0]), sol[1], sol[2]))
    if not sol:
        # dump a short dry-run
        g = Game.from_seed(seed)
        for i in range(200):
            g.step(i % 18 == 0)
            if g.dead:
                print("period18 dead at", g.ticks, "score", g.score, "y", hex(g.y))
                break
        else:
            print("period18 survived 200 score", g.score)
        return
    flaps, score, ticks = sol
    body = (
        f"sequence=0&ticks={ticks}&final=1&score={score}&flaps="
        + ",".join(str(t) for t in flaps)
    )
    # practice/check: ticks field is chunk size (number of practice ticks covered),
    # not flap count. For a full run, ticks should be total practice frames = game ticks
    # after last frame... After solving, g.ticks is frames simulated. Practice counter
    # increments once per frame too, ending at same value.
    code, resp = http_post("/api/practice/check", body, ptoken)
    print("check", code, resp)


def play_challenge() -> None:
    code, body = http_post("/api/attempt")
    print("attempt", code, body)
    form = parse_form(body)
    token = form["token"]

    # Begin challenge: second attempt with bearer rotates token and arms seed/wait
    code, body = http_post("/api/attempt", "", token)
    print("attempt2", code, body)
    form = parse_form(body)
    if form.get("token"):
        token = form["token"]

    for _ in range(6):
        if form.get("error"):
            print("error", form)
            return
        if "flag" in form:
            print("FLAG", form["flag"])
            return

        round_n = int(form["round"])
        if round_n >= 4:
            print("done?", form)
            return

        seed = int(form["seed"])
        target = int(form["target"])
        wait_s = int(form["wait_seconds"])
        print(f"=== round {round_n} seed={seed} target={target} wait={wait_s}s ===")

        sol = try_solve(seed, target)
        if not sol:
            print("solve failed")
            return
        flaps, score, ticks = sol
        print(f"solved flaps={len(flaps)} score={score} ticks={ticks}")

        # Server accepts wait_ms in-body (virtual timer); no real sleep needed
        body_data = (
            f"round={round_n}&wait_ms={wait_s * 1000}&ticks={ticks}&score={score}&flaps="
            + ",".join(str(t) for t in flaps)
        )
        code, body = http_post("/api/complete", body_data, token)
        print("complete", code, body)
        form = parse_form(body)
        if form.get("token"):
            token = form["token"]
        if form.get("error"):
            code, body = http_post("/api/attempt", "", token)
            print("refresh", code, body)
            form = parse_form(body)
            if form.get("token"):
                token = form["token"]
            if form.get("error"):
                return
        if "flag" in form:
            print("FLAG", form["flag"])
            return


def main() -> None:
    global BASE
    ap = argparse.ArgumentParser()
    ap.add_argument("--server", default=BASE)
    ap.add_argument("--practice", action="store_true")
    ap.add_argument("--play", action="store_true")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--target", type=int, default=10)
    ap.add_argument("--solve-only", action="store_true")
    args = ap.parse_args()
    BASE = args.server.rstrip("/")

    if args.solve_only:
        seed = args.seed if args.seed is not None else 1355401025
        sol = try_solve(seed, args.target)
        print(sol if sol else "fail")
        return
    if args.practice:
        practice_test(args.target)
        return
    if args.play:
        play_challenge()
        return
    print("need --practice / --play / --solve-only")


if __name__ == "__main__":
    main()
