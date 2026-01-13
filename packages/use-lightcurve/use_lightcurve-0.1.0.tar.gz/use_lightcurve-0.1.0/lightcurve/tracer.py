import os
import uuid
import time
import functools
import datetime
from contextvars import ContextVar
from typing import Optional, Dict, Any, List, Union
from .transport import BackgroundTransport
from .schemas import RunPayload, StepPayload
from .context import run_ctx


COGNITIVE_PHASES = {
    "planning",
    "goal_decomposition",
    "reflection",
    "self_critique",
    "tool_selection",
    "validation",
    "synthesis"
}

class GlobalTracer:
    def __init__(self):
        self.transport: Optional[BackgroundTransport] = None
        self._api_key: Optional[str] = None
        self.project: Optional[str] = None

    def init(self, api_key: Optional[str] = None, base_url: str = "http://localhost:8000"):
        self._api_key = api_key or os.getenv("LIGHTCURVE_API_KEY")
        self.transport = BackgroundTransport(api_key=self._api_key, api_url=base_url)

    def trace(self, name: Optional[str] = None, project: Optional[str] = None, tags: Optional[Dict[str, Any]] = None):
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                if not self.transport:
                    # If not inited, just run the function
                    return func(*args, **kwargs)

                status = "success"
                error_msg = None
                output = None
                
                # Start Run
                start_time = time.time()
                run_id = str(uuid.uuid4())
                
                # Set Context
                token = run_ctx.set([]) # Initialize steps list
                
                try:
                    result = func(*args, **kwargs)
                    output = {"return_value": str(result)} # Simplistic stringification
                    return result
                except Exception as e:
                    status = "failure"
                    error_msg = str(e)
                    output = {"error": error_msg}
                    raise e
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    steps = run_ctx.get()
                    run_ctx.reset(token)

                    # Build Payload
                    payload = RunPayload(
                        run_id=run_id,
                        name=name or func.__name__,
                        agent_id=name or func.__name__, # Trace name = agent_id for now
                        org_id="default-org",
                        project=project or self.project,
                        started_at=datetime.datetime.now(datetime.timezone.utc),
                        duration_ms=duration_ms,
                        status=status,
                        input={"args": str(args), "kwargs": str(kwargs)}, # Redact in prod
                        output=output,
                        steps=steps, # now this is List[StepPayload]
                        metadata=tags,
                        exception=error_msg
                    )
                    
                    # Send
                    self.transport.send(payload)
            
            return wrapper
        return decorator

    def step(self, name: str, type: str = "custom", metadata: Optional[Dict[str, Any]] = None):
        return StepContext(name, type, metadata)

    def cognitive(self, phase: str, name: Optional[str] = None):
        if phase not in COGNITIVE_PHASES:
            # Soft warning
            print(f"Warning: Unknown cognitive phase '{phase}'. Expected one of {COGNITIVE_PHASES}")
        return StepContext(name or phase, "cognitive", {"cognitive_phase": phase})

class StepContext:
    def __init__(self, name: str, type: str, metadata: Optional[Dict[str, Any]]):
        self.name = name
        self.type = type
        self.metadata = metadata or {}
        self.start_time = None
        self.cognitive_type = None

        if type == "cognitive":
             self.cognitive_type = self.metadata.get("cognitive_phase")

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.time() - self.start_time) * 1000
        steps = run_ctx.get()
        
        # Map SDK type to Backend Stage
        stage_map = {
            "llm": "execution_strategy", 
            "planning": "task_specification",
            "custom": "execution_strategy",
            "cognitive": "execution_strategy" # Default mapping for cognitive steps if not overridden
        }
        
        # If it's a cognitive step, map based on phase if needed, or keep generic stage
        # For V1, let's map cognitive phases to stages roughly
        if self.cognitive_type:
            stage_map_cognitive = {
                "planning": "task_specification",
                "goal_decomposition": "task_specification",
                "reflection": "validation",
                "self_critique": "validation",
                "validation": "validation",
                "tool_selection": "tool_call",
                "synthesis": "output"
            }
            stage = stage_map_cognitive.get(self.cognitive_type, "execution_strategy")
        else:
            stage = stage_map.get(self.type, "execution_strategy")
        
        if steps is not None:
            steps.append(StepPayload(
                name=self.name,
                type=self.type,
                stage=stage,
                cognitive_type=self.cognitive_type,
                status="failure" if exc_type else "success",
                started_at=datetime.datetime.now(datetime.timezone.utc),
                duration_ms=duration,
                metadata=self.metadata,
                input={}, # Optionally capture
                output={"error": str(exc_val)} if exc_val else {},
                content={
                    "input": {},
                    "output": {"error": str(exc_val)} if exc_val else {}
                }
            ))

# Global Singleton
tracer = GlobalTracer()
