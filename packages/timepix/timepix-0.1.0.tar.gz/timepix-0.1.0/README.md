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

tp.from_point("start")
tp.from_last_point()
tp.between_points("start", "middle")
```