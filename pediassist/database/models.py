"""
Database models for PediAssist
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Date, 
    ForeignKey, JSON, ARRAY, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column

# Database compatibility layer
try:
    from sqlalchemy.dialects.postgresql import ARRAY as PGArray
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False
    PGArray = None

Base = declarative_base()

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    icd10_code: Mapped[Optional[str]] = mapped_column(String(10), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    age_range: Mapped[Optional[str]] = mapped_column(String(50))
    
    # Relationships
    treatment_protocols: Mapped[List["TreatmentProtocol"]] = relationship(
        "TreatmentProtocol", back_populates="diagnosis", cascade="all, delete-orphan"
    )
    communication_templates: Mapped[List["CommunicationTemplate"]] = relationship(
        "CommunicationTemplate", back_populates="diagnosis", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Diagnosis(id={self.id}, name='{self.name}', category='{self.category}')>"

class TreatmentProtocol(Base):
    __tablename__ = "treatment_protocols"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    diagnosis_id: Mapped[int] = mapped_column(Integer, ForeignKey("diagnoses.id"), nullable=False)
    severity_level: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    protocol_text: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_level: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    version: Mapped[int] = mapped_column(Integer, default=1)
    
    # Relationships
    diagnosis: Mapped["Diagnosis"] = relationship("Diagnosis", back_populates="treatment_protocols")
    dosing_guidelines: Mapped[List["DosingGuideline"]] = relationship("DosingGuideline", back_populates="protocol")
    
    __table_args__ = (
        UniqueConstraint('diagnosis_id', 'severity_level', 'version'),
        Index('idx_protocol_diagnosis_severity', 'diagnosis_id', 'severity_level'),
    )
    
    def __repr__(self) -> str:
        return f"<TreatmentProtocol(id={self.id}, diagnosis_id={self.diagnosis_id}, severity='{self.severity_level}')>"

class Medication(Base):
    __tablename__ = "medications"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    generic_name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    brand_names: Mapped[Optional[List[str]]] = mapped_column(JSON)
    category: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    pediatric_approved: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    age_restrictions: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    # Relationships
    dosing_guidelines: Mapped[List["DosingGuideline"]] = relationship(
        "DosingGuideline", back_populates="medication", cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Medication(id={self.id}, generic_name='{self.generic_name}', category='{self.category}')>"

class DosingGuideline(Base):
    __tablename__ = "dosing_guidelines"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    medication_id: Mapped[int] = mapped_column(Integer, ForeignKey("medications.id"), nullable=False)
    diagnosis_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("diagnoses.id"))
    weight_based_dosing: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    age_based_dosing: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    max_dose: Mapped[Optional[str]] = mapped_column(String(100))
    contraindications: Mapped[Optional[List[str]]] = mapped_column(JSON)
    
    # Relationships
    medication: Mapped["Medication"] = relationship("Medication", back_populates="dosing_guidelines")
    diagnosis: Mapped[Optional["Diagnosis"]] = relationship("Diagnosis", back_populates="dosing_guidelines")
    protocol: Mapped[Optional["TreatmentProtocol"]] = relationship("TreatmentProtocol", back_populates="dosing_guidelines")
    
    __table_args__ = (
        Index('idx_dosing_medication', 'medication_id'),
        Index('idx_dosing_diagnosis', 'diagnosis_id'),
    )
    
    def __repr__(self) -> str:
        return f"<DosingGuideline(id={self.id}, medication_id={self.medication_id})>"

class ClinicalGuideline(Base):
    __tablename__ = "clinical_guidelines"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # AAP, CDC, etc.
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embeddings: Mapped[Optional[Any]] = mapped_column(JSON)  # For vector search (simplified)
    publish_date: Mapped[Optional[date]] = mapped_column(Date)
    url: Mapped[Optional[str]] = mapped_column(String(500))
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<ClinicalGuideline(id={self.id}, source='{self.source}', title='{self.title[:50]}...')>"

class CommunicationTemplate(Base):
    __tablename__ = "communication_templates"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    diagnosis_id: Mapped[int] = mapped_column(Integer, ForeignKey("diagnoses.id"), nullable=False)
    template_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # handout, sms, email
    age_range: Mapped[Optional[str]] = mapped_column(String(50), index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", index=True)
    
    # Relationships
    diagnosis: Mapped["Diagnosis"] = relationship("Diagnosis", back_populates="communication_templates")
    
    __table_args__ = (
        Index('idx_comm_template_diagnosis_type', 'diagnosis_id', 'template_type'),
        Index('idx_comm_template_age_lang', 'age_range', 'language'),
    )
    
    def __repr__(self) -> str:
        return f"<CommunicationTemplate(id={self.id}, diagnosis_id={self.diagnosis_id}, type='{self.template_type}')>"

class QueryLog(Base):
    __tablename__ = "query_log"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # Hashed, not identifiable
    diagnosis_input: Mapped[str] = mapped_column(Text, nullable=False)
    patient_age: Mapped[Optional[int]] = mapped_column(Integer)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    treatment_plan_generated: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
    
    def __repr__(self) -> str:
        return f"<QueryLog(id={self.id}, user_id='{self.user_id[:8]}...', timestamp='{self.timestamp}')>"

class License(Base):
    __tablename__ = "licenses"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    license_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    organization: Mapped[Optional[str]] = mapped_column(String(255))
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, index=True)
    feature_flags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<License(id={self.id}, organization='{self.organization}', active={self.is_active})>"
    
    def is_valid(self) -> bool:
        """Check if license is currently valid"""
        if not self.is_active:
            return False
        if self.expiry_date and self.expiry_date < date.today():
            return False
        return True