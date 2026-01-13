from __future__ import annotations
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

class StepPayload(BaseModel):
    name: str
    type: str # "tool", "llm", "planning", "custom"
    stage: Optional[str] = None # Mapped to backend stage
    cognitive_type: Optional[str] = None # Cognitive phase
    status: str # "success", "failure"
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    content: Optional[Dict[str, Any]] = None # Generic content container for persistence
    duration_ms: Optional[float] = None
    started_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

class RunPayload(BaseModel):
    run_id: str
    name: str
    org_id: str = "default-org" # Default for single-tenant / local
    agent_id: str # Mapped from name if not provided
    project: Optional[str] = None
    input: Optional[Dict[str, Any]] = None
    output: Optional[Dict[str, Any]] = None
    status: str # "success", "failure"
    duration_ms: Optional[float] = None
    started_at: datetime
    steps: List[StepPayload] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    exception: Optional[str] = None
