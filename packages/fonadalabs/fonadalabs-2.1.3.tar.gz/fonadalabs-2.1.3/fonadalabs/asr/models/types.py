# fonada_asr/models/types.py
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class TranscribeResult:
    text: str
    engine: Optional[str] = None
    language_id: Optional[str] = None
    latency_ms: Optional[float] = None
    request_id: Optional[str] = None
    raw: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None

@dataclass
class BatchResult:
    results: List[TranscribeResult] = field(default_factory=list)
    failed: List["FailedTranscription"] = field(default_factory=list)  # file paths that failed


@dataclass
class FailedTranscription:
    file_path: str
    error: str
