import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone

from .schemas import (
    CognitionEvent, InputPayload, KnowledgePayload, PlanPayload, 
    ToolPayload, ValidationPayload, OutputPayload, IncidentFlags
)
from .buffer import EventBuffer

class Lightcurve:
    def __init__(self, api_key: Optional[str] = None, base_url: str = "http://localhost:8000"):
        self.api_key = api_key
        self.base_url = base_url
        self.buffer = EventBuffer(api_url=base_url, api_key=api_key)

    def start_run(self, agent_id: str, run_id: Optional[str] = None, org_id: Optional[str] = None) -> 'Run':
        if not run_id:
            run_id = str(uuid.uuid4())
        return Run(client=self, run_id=run_id, agent_id=agent_id, org_id=org_id)

    def close(self):
        self.buffer.close()

class Run:
    def __init__(self, client: Lightcurve, run_id: str, agent_id: str, org_id: Optional[str] = None):
        self.client = client
        self.run_id = run_id
        self.agent_id = agent_id
        self.org_id = org_id

    def _log(self, type: str, data: Any, incident_flags: Optional[IncidentFlags] = None):
        event = CognitionEvent(
            run_id=self.run_id,
            agent_id=self.agent_id,
            org_id=self.org_id,
            timestamp=datetime.now(timezone.utc),
            type=type,
            data=data,
            incident_flags=incident_flags
        )
        self.client.buffer.add_event(event)

    def log_input(self, user_input: str, interpreted_goal: Optional[str] = None, constraints: List[str] = []):
        data = InputPayload(user_input=user_input, interpreted_goal=interpreted_goal, constraints=constraints)
        self._log("input", data)

    def log_knowledge(self, summary: str, evidence_present: bool = False, sources: List[str] = []):
        data = KnowledgePayload(summary=summary, evidence_present=evidence_present, sources=sources)
        self._log("knowledge", data)

    def log_plan(self, steps: List[str], rationale: Optional[str] = None, alternatives: List[str] = []):
        data = PlanPayload(steps=steps, rationale=rationale, alternatives=alternatives)
        self._log("plan", data)

    def log_tool(self, tool_name: str, input: Dict[str, Any], output: Optional[Dict[str, Any]] = None, 
                 success: bool = True, retries: int = 0, latency_ms: Optional[float] = None):
        data = ToolPayload(
            tool_name=tool_name, input=input, output=output, 
            success=success, retries=retries, latency_ms=latency_ms
        )
        self._log("tool", data)

    def log_validation(self, result: bool, method: str = "auto", confidence_score: Optional[float] = None):
        data = ValidationPayload(result=result, method=method, confidence_score=confidence_score)
        self._log("validation", data)

    def log_output(self, content: str, structured_data: Optional[Dict[str, Any]] = None, 
                   confidence: Optional[float] = None):
        data = OutputPayload(content=content, structured_data=structured_data, confidence=confidence)
        self._log("output", data)

    def end(self):
        # Flush the buffer to ensure all events are sent
        self.client.buffer.flush()
