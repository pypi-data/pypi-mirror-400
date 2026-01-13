from contextvars import ContextVar
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class active_run_context:
    steps: List[Dict[str, Any]] = field(default_factory=list)
    
run_ctx = ContextVar("lightcurve_run_ctx", default=None)
