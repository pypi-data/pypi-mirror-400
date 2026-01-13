# Atari HNS (Human Normalized Score)

Lightweight helper for computing Atari human-normalized scores (HNS) using published human and random baselines.

## Installation

- From PyPI (once published): `pip install atarihns`
- From source: clone the repo and run `pip install .`

## Usage

```python
from atarihns import get_human_score, get_random_score
from atarihns import calculate_hns, get_hns # alias

environment = "Pong-v5"
agent_score = 15.0

human = get_human_score(environment)
random = get_random_score(environment)
hns = calculate_hns(environment, agent_score)

print(f"{environment} human: {human}, random: {random}, hns: {hns:.3f}")
```

## Notes

- Baseline scores for ALE environments are defined in `atarihns.constants.ATARI_SCORES` as `(random, human)`.
- Helper functions raise `KeyError` if an environment name is missing from the table.
