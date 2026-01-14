from enum import Enum
from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class Severity(str, Enum):
    info = "info"
    low = "low"
    medium = "medium"
    high = "high"


class Finding(BaseModel):
    name: str
    severity: Severity
    description: str
    evidence: Dict[str, Any] = {}


class PathResult(BaseModel):
    path: str
    status_code: Optional[int] = None
    findings: List[Finding] = []


class SeveritySummary(BaseModel):
    info: int = 0
    low: int = 0
    medium: int = 0
    high: int = 0
    risk_score: int = 0  # simple weighted score


class ScanResult(BaseModel):
    target: str
    paths_scanned: List[str]
    path_results: List[PathResult]
    global_findings: List[Finding] = []
    summary: SeveritySummary = SeveritySummary()
