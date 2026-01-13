"""
AJT Grounded Extract - Engine Module

STOP-first, evidence-grounded extraction engine.
"""

__version__ = "2.1.0"

from .ingest import DocumentIngestor
from .extract import RuleBasedExtractor
from .ground import EvidenceGrounder
from .judge import ExtractionJudge, Decision, StopReason
from .archive import EvidenceArchive
from .pipeline import ExtractionPipeline
from .audit import AuditLogger, DefenseBriefGenerator, RegulatoryReportGenerator

__all__ = [
    "DocumentIngestor",
    "RuleBasedExtractor",
    "EvidenceGrounder",
    "ExtractionJudge",
    "Decision",
    "StopReason",
    "EvidenceArchive",
    "ExtractionPipeline",
    "AuditLogger",
    "DefenseBriefGenerator",
    "RegulatoryReportGenerator",
]
