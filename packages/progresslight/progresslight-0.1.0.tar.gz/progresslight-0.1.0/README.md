# ProgressLight

A lightweight, Rich-inspired CLI helper for progress bars and logs.

## Install (local)

```bash
pip install -e .
```

## Quick usage

```python
from progresslight import ProgressBar, Logger

logger = Logger()
logger.info("start")

bar = ProgressBar(description="Download", total_size=100, item="files")
for _ in range(100):
    bar.update(1)
bar.done()
```


