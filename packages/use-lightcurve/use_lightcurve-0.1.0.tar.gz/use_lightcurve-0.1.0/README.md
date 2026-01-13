# use-lightcurve

The official Python SDK for Lightcurve, the observability and evaluation platform for LLM Agents.

## Installation

```bash
pip install use-lightcurve
```

## Quick Start

```python
from lightcurve import Lightcurve

lc = Lightcurve(api_key="your_api_key")

# Track a run
with lc.trace(agent_id="my-agent") as run:
    result = my_agent.run("input prompt")
    run.log_output(result)
```
