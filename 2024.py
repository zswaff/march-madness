from collections import defaultdict
from math import inf
from random import randint, random

from tqdm import tqdm


N_PLAYERS = 30
N_SIMS = 100000
ORDERED_TEAMS = [
    "Connecticut",
    "Houston",
    "Purdue",
    "North Carolina",
    "Tennessee",
    "Arizona",
    "Marquette",
    "Iowa State",
    "Baylor",
    "Creighton",
    "Kentucky",
    "Illinois",
    "Duke",
    "Kansas",
    "Auburn",
    "Alabama",
    "BYU",
    "San Diego State",
    "Wisconsin",
    "Saint Mary's",
    "Gonzaga",
    "Clemson",
    "Texas Tech",
    "South Carolina",
    "Florida",
    "Washington State",
    "Texas",
    "Dayton",
    "Nebraska",
    "Utah State",
    "Florida Atlantic",
    "Mississippi State",
    "Michigan State",
    "Texas A&M",
    "TCU",
    "Northwestern",
    "Nevada",
    "Colorado or Boise State",
    "Drake",
    "New Mexico",
    "Oregon",
    "Colorado State or Virginia",
    "N.C. State",
    "Duquesne",
    "Grand Canyon",
    "James Madison",
    "McNeese State",
    "UAB",
    "Vermont",
    "Yale",
    "Samford",
    "Charleston",
    "Oakland",
    "Akron",
    "Morehead State",
    "Colgate",
    "Long Beach State",
    "Western Kentucky",
    "South Dakota State",
    "Saint Peter's",
    "Longwood",
    "Stetson",
    "Grambling State or Montana State",
    "Wagner",
]
ODDS = {
    "Connecticut": 370,
    "Houston": 550,
    "Purdue": 700,
    "Arizona": 1200,
    "North Carolina": 1700,
    "Tennessee": 1700,
    "Iowa State": 2000,
    "Auburn": 2200,
    "Creighton": 2500,
    "Marquette": 2500,
    "Duke": 3000,
    "Kentucky": 3000,
    "Baylor": 3500,
    "Illinois": 3500,
    "Alabama": 4000,
    "Kansas": 4500,
    "Gonzaga": 5000,
    "BYU": 6000,
    "Wisconsin": 6000,
    "Florida": 6500,
    "Michigan State": 6500,
    "Saint Mary's": 6500,
    "San Diego State": 7500,
    "New Mexico": 7500,
    "Texas Tech": 8000,
    "Texas": 10000,
    "Clemson": 12000,
    "TCU": 12000,
    "Nebraska": 12000,
    "Colorado or Boise State": 15000,  # Boise State is 25000 though
    "Washington State": 15000,
    "Texas A&M": 15000,
    "Mississippi State": 15000,
    "Florida Atlantic": 15000,
    "Dayton": 15000,
    "Oregon": 20000,
    "South Carolina": 20000,
    "Nevada": 20000,
    "Utah State": 20000,
    "Drake": 20000,
    "N.C. State": 25000,
    "Northwestern": 25000,
    "Colorado State or Virginia": 25000,
    "James Madison": 25000,
    "Grand Canyon": 50000,
    "McNeese State": 50000,
    "Yale": 50000,
    "Samford": 50000,
    "Vermont": 50000,
    "UAB": 100000,
    "Charleston": 100000,
    "Morehead State": 100000,
    "Longwood": 100000,
    "Stetson": 100000,
    "Oakland": 100000,
    "South Dakota State": 100000,
    "Colgate": 100000,
    "Wagner": 100000,
    "Akron": 100000,
    "Saint Peter's": 100000,
    "Western Kentucky": 100000,
    "Long Beach State": 100000,
    "Grambling State or Montana State": 100000,
    "Duquesne": 100000,
}
PAIRINGS = [
    "Connecticut",
    "Stetson",
    "Florida Atlantic",
    "Northwestern",
    "San Diego State",
    "UAB",
    "Auburn",
    "Yale",
    "BYU",
    "Duquesne",
    "Illinois",
    "Morehead State",
    "Washington State",
    "Drake",
    "Iowa State",
    "South Dakota State",
    "North Carolina",
    "Wagner",
    "Mississippi State",
    "Michigan State",
    "Saint Mary's",
    "Grand Canyon",
    "Alabama",
    "Charleston",
    "Clemson",
    "New Mexico",
    "Baylor",
    "Colgate",
    "Dayton",
    "Nevada",
    "Arizona",
    "Long Beach State",
    "Houston",
    "Longwood",
    "Nebraska",
    "Texas A&M",
    "Wisconsin",
    "James Madison",
    "Duke",
    "Vermont",
    "Texas Tech",
    "N.C. State",
    "Kentucky",
    "Oakland",
    "Florida",
    "Colorado or Boise State",
    "Marquette",
    "Western Kentucky",
    "Purdue",
    "Grambling State or Montana State",
    "Utah State",
    "TCU",
    "Gonzaga",
    "McNeese State",
    "Kansas",
    "Samford",
    "South Carolina",
    "Oregon",
    "Creighton",
    "Akron",
    "Texas",
    "Colorado State or Virginia",
    "Tennessee",
    "Saint Peter's",
]

R2 = {1: 8, 2: 12, 3: 16, 4: 16, 5: 24, 6: 24}
R3 = {1: 16, 2: 24, 3: 32, 4: 32, 5: 48, 6: 48}
R4 = {1: 8, 2: 26, 3: 32, 4: 48, 5: 96}
R5 = {1: 16, 2: 32, 3: 64, 4: 96, 5: 196}
R6 = {1: 48, 2: 196, 3: 384}

SEEDS = {e: i // 4 for i, e in enumerate(ORDERED_TEAMS, 4)}
PMS = {k: (v / 100) + 1 for k, v in ODDS.items()}
PMRS = {k: 1 / v for k, v in PMS.items()}
PRM_SUM = sum(PMRS.values())
K1, K2 = list(PMRS.keys())[:2]
PM1 = PMS[K1]
P1 = PMS[K2] / (PM1 + (PM1 * PMS[K2] * (PRM_SUM - PMRS[K2])))
PROBS = {k: P1 if k == K1 else P1 * PM1 / v for k, v in PMS.items()}


def score(candidate, golden):
    if any(
        (SEEDS[e] == 16 and candidate[e] >= 2 and golden[e] >= 2)
        or (SEEDS[e] >= 14 and candidate[e] >= 3 and golden[e] >= 3)
        or (SEEDS[e] >= 12 and candidate[e] >= 4 and golden[e] >= 4)
        or (SEEDS[e] >= 9 and candidate[e] >= 5 and golden[e] >= 5)
        or (SEEDS[e] >= 6 and candidate[e] >= 6 and golden[e] >= 6)
        or (SEEDS[e] >= 4 and candidate[e] == 7 and golden[e] == 7)
        for e in ORDERED_TEAMS
    ):
        return inf

    res = 0
    for e in [k for k, v in candidate.items() if v > 1]:
        res += SEEDS[e]
    for e in [k for k, v in candidate.items() if v > 2]:
        res += R2.get(SEEDS[e], 48)
    for e in [k for k, v in candidate.items() if v > 3]:
        res += R3.get(SEEDS[e], 96)
    for e in [k for k, v in candidate.items() if v > 4]:
        res += R4.get(SEEDS[e], 192)
    for e in [k for k, v in candidate.items() if v > 5]:
        res += R5.get(SEEDS[e], 384)
    for e in [k for k, v in candidate.items() if v > 6]:
        res += R6.get(SEEDS[e], 768)

    return res


def get_random_bracket():
    res = {}
    curr = list(PAIRINGS)
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
    res = {}
    curr = list(PAIRINGS)
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
    curr = list(PAIRINGS)
    for round in range(1, 7):
        print(f"Round {round}")
        ncurr = []
        for j in range(0, len(curr), 2):
            t1 = totals[(curr[j], round)]
            t2 = totals[(curr[j + 1], round)]
            d = 0 if t1 > t2 else (1 if t2 > t1 else randint(0, 1))
            w = curr[j + d]
            ncurr.append(w)
            print(w)
        curr = ncurr
        print()


if __name__ == "__main__":
    main()
