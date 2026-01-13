# TimePix

A lightweight Python utility for measuring execution time between named checkpoints.

## Installation

```bash
$ pip install timepix
```
## Quick start
```python
from timepix import timepix as tp
import time

tp.set_point("start")
time.sleep(0.5)

tp.set_point("middle")
time.sleep(0.3)

tp.from_point("start") # stdout >> Time from point "start": 0.7988662s.
tp.from_last_point() # stdout >> Time from point "middle": 0.3008336s.
tp.between_points("start", "middle") # stdout >> Time between "start" and "middle" is 0.4981095s.
```