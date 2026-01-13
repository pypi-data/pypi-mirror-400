"""
AJT Grounded Extract - Engine Module

STOP-first, evidence-grounded extraction engine.
"""

__version__ = "1.0.0"

from .ingest import DocumentIngestor
from .extract import CandidateExtractor
from .ground import EvidenceGrounder
from .judge import ExtractionJudge, Decision, StopReason
from .archive import EvidenceArchiver
from .pipeline import ExtractionPipeline
from .audit import AuditLogger, DefenseBriefGenerator, RegulatoryReportGenerator

__all__ = [
    "DocumentIngestor",
    "CandidateExtractor",
    "EvidenceGrounder",
    "ExtractionJudge",
    "Decision",
    "StopReason",
    "EvidenceArchiver",
    "ExtractionPipeline",
    "AuditLogger",
    "DefenseBriefGenerator",
    "RegulatoryReportGenerator",
]
