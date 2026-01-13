# t4racker

[![PyPI](https://img.shields.io/pypi/v/t4racker)](https://pypi.org/project/t4racker/)
[![Tests](https://img.shields.io/github/actions/workflow/status/romazu/t4racker/tests.yml?branch=main)](https://github.com/romazu/t4racker/actions?query=branch%3Amain)

Transparent time-travel tracker for Python objects. Records mutations to dicts, sets, lists, and custom objects—then replay state at any step.

## Install

```bash
pip install t4racker
```

## Usage

```python
from t4racker import TTTTracker, TrackReplayer


class Algorithm:
    def __init__(self):
        self.visited = set()
        self.path = []


tracker = TTTTracker()
algo = Algorithm()
tracker.track(algo, tracked_fields=['visited', 'path'])
tracker.capture_snapshot('start')

algo.visited.add('A')
algo.path.append('A')
algo.visited.add('B')
algo.path.append('B')

# Export
data = tracker.to_dict()

# Replay
replayer = TrackReplayer(data)
state = replayer.state_at(2)  # State after step 2
print(state)  # {'visited': {'A', 'B'}, 'path': ['A']}
```

## What it tracks

- **dict**: `__setitem__`, `__delitem__`
- **set**: `add`, `remove`, `discard`
- **list**: `append`, `pop`, `__setitem__`, `clear`, `extend`
- **Custom objects**: attribute assignments

Nested containers are tracked recursively.

## Tests

```bash
pytest
```

## License

MIT
