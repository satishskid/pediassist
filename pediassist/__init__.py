"""
PediAssist - AI-Powered Pediatric Subspecialty Treatment Assistant

An intelligent system providing evidence-based treatment guidance 
for general pediatricians across all pediatric subspecialties.
"""

__version__ = "0.1.0"
__author__ = "PediAssist Team"
__email__ = "team@pediassist.com"

from .core.diagnosis_parser import DiagnosisParser
from .core.treatment_generator import TreatmentGenerator
from .core.communication_engine import CommunicationEngine
from .core.delegation_manager import DelegationManager

__all__ = [
    "DiagnosisParser",
    "TreatmentGenerator", 
    "CommunicationEngine",
    "DelegationManager",
]