#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run a Monte Carlo simulation to predict the winning bracket for 2024 Men's March Madness
according to the unusual scoring rules documented in
[this doc](https://docs.google.com/document/d/14sse_vjS4rY2HIZoRnVe0yTre26LaVx7D8gjDX__vqE/edit)
and tracked in
[this ESPN group](https://fantasy.espn.com/games/tournament-challenge-bracket-2024/group?id=e36d9c96-95c1-4b9d-bd38-f0fab939c538)
"""

from collections import defaultdict
from math import inf
from random import randint, random

from config import ODDS, ORDERED_TEAMS, TOURNAMENT
from tqdm import tqdm

N_PLAYERS = 17
N_SIMS = 100000


ROUND_SEED_AUTOWINS = {
    2: 16,
    3: 14,
    4: 12,
    5: 9,
    6: 6,
    7: 4,
}
ROUND_SEED_SCORES = {
    2: ({e: e for e in range(1, 17)}, 0),
    3: ({1: 8, 2: 12, 3: 16, 4: 16, 5: 24, 6: 24}, 48),
    4: ({1: 16, 2: 24, 3: 32, 4: 32, 5: 48, 6: 48}, 96),
    5: ({1: 8, 2: 26, 3: 32, 4: 48, 5: 96}, 192),
    6: ({1: 16, 2: 32, 3: 64, 4: 96, 5: 196}, 384),
    7: ({1: 48, 2: 196, 3: 384}, 768),
}


def convert_odds_to_probabilities(odds):
    """Convert odds to probabilities according to the formulas explained in [my blogpost](https://zswaff.com/blog/betting-odds-to-probabilities)."""
    prob_mults = {k: (v / 100) + 1 for k, v in odds.items()}
    prob_mult_recips = {k: 1 / v for k, v in prob_mults.items()}
    prob_mult_recip_tot = sum(prob_mult_recips.values())
    key_1, key_2 = list(prob_mult_recips.keys())[:2]
    prob_mult_1 = prob_mults[key_1]
    prob_1 = prob_mults[key_2] / (
        prob_mult_1 + (prob_mult_1 * prob_mults[key_2] * (prob_mult_recip_tot - prob_mult_recips[key_2]))
    )
    return {k: prob_1 if k == key_1 else prob_1 * prob_mult_1 / v for k, v in prob_mults.items()}


SEEDS = {e: i // 4 for i, e in enumerate(ORDERED_TEAMS, 4)}
PROBS = convert_odds_to_probabilities(ODDS)


def score(candidate, golden):
    """Score a candidate bracket against the golden bracket according to the rules."""
    if any(
        SEEDS[e] >= min_seed and candidate[e] >= rnd and golden[e] >= rnd
        for min_seed, rnd in ROUND_SEED_AUTOWINS.items()
        for e in ORDERED_TEAMS
    ):
        return inf

    return sum(
        ROUND_SEED_SCORES[rnd][0].get(SEEDS[team], ROUND_SEED_SCORES[rnd][1])
        for team, elim_rnd in candidate.items()
        for rnd in range(2, elim_rnd)
    )


def get_random_bracket():
    """Get a random bracket in the format {team: elimination round}."""
    res = {}
    curr = TOURNAMENT
    for i in range(1, 7):
        ncurr = []
        for j in range(0, len(curr), 2):
            d = randint(0, 1)
            ncurr.append(curr[j + d])
            res[curr[j + 1 - d]] = i
        curr = ncurr
    res[curr[0]] = 7
    return res


def get_golden_bracket():
    """Get a probabilistic golden bracket in the format {team: elimination round}."""
    res = {}
    curr = TOURNAMENT
    for i in range(1, 7):
        ncurr = []
        for j in range(0, len(curr), 2):
            p1 = PROBS[curr[j]]
            p2 = PROBS[curr[j + 1]]
            d = int(random() * (p1 + p2) >= p1)
            ncurr.append(curr[j + d])
            res[curr[j + 1 - d]] = i
        curr = ncurr
    res[curr[0]] = 7
    return res


def main():
    """Run the Monte Carlo simulation and print the results."""
    # create a frequency map of the (team, round) wins that contribute to winning (i.e. nonlosing) brackets
    cuttoff = int(N_PLAYERS * 0.2)
    totals = defaultdict(int)
    for _ in tqdm(range(N_SIMS)):
        rands = [get_random_bracket() for __ in range(N_PLAYERS)]
        golden = get_golden_bracket()
        winners = sorted(rands, key=lambda x: score(x, golden))[cuttoff:]
        for winner in winners:
            for k, v in winner.items():
                for i in range(1, v + 1):
                    totals[(k, i)] += 1

    # run through the tournament and pick the winners based on the frequency map
    curr = TOURNAMENT
    for rnd in range(1, 7):
        print(f"Round {rnd}")
        ncurr = []
        for j in range(0, len(curr), 2):
            t1 = totals[(curr[j], rnd)]
            t2 = totals[(curr[j + 1], rnd)]
            d = 0 if t1 > t2 else (1 if t2 > t1 else randint(0, 1))
            w = curr[j + d]
            ncurr.append(w)
            print(w)
        curr = ncurr
        print()


if __name__ == "__main__":
    main()
