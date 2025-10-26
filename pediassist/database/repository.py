"""
Database repository layer for PediAssist
"""

from typing import Optional, List, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .models import (
    Diagnosis, TreatmentProtocol, Medication, DosingGuideline, 
    ClinicalGuideline, CommunicationTemplate, QueryLog, License
)

class DiagnosisRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_name(self, name: str) -> Optional[Diagnosis]:
        """Get diagnosis by exact name match"""
        result = await self.session.execute(
            select(Diagnosis).where(func.lower(Diagnosis.name) == func.lower(name))
        )
        return result.scalar_one_or_none()
    
    async def get_by_icd10(self, icd10_code: str) -> Optional[Diagnosis]:
        """Get diagnosis by ICD-10 code"""
        result = await self.session.execute(
            select(Diagnosis).where(Diagnosis.icd10_code == icd10_code)
        )
        return result.scalar_one_or_none()
    
    async def search_by_name(self, query: str, limit: int = 10) -> List[Diagnosis]:
        """Search diagnoses by name (fuzzy match)"""
        result = await self.session.execute(
            select(Diagnosis)
            .where(Diagnosis.name.ilike(f"%{query}%"))
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_category(self, category: str) -> List[Diagnosis]:
        """Get all diagnoses in a category"""
        result = await self.session.execute(
            select(Diagnosis).where(func.lower(Diagnosis.category) == func.lower(category))
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> Diagnosis:
        """Create a new diagnosis"""
        diagnosis = Diagnosis(**kwargs)
        self.session.add(diagnosis)
        await self.session.commit()
        await self.session.refresh(diagnosis)
        return diagnosis

class TreatmentProtocolRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_protocol(
        self, 
        diagnosis_id: int, 
        severity_level: str, 
        version: Optional[int] = None
    ) -> Optional[TreatmentProtocol]:
        """Get treatment protocol for diagnosis and severity"""
        query = select(TreatmentProtocol).where(
            and_(
                TreatmentProtocol.diagnosis_id == diagnosis_id,
                func.lower(TreatmentProtocol.severity_level) == func.lower(severity_level)
            )
        )
        
        if version:
            query = query.where(TreatmentProtocol.version == version)
        else:
            # Get latest version
            query = query.order_by(TreatmentProtocol.version.desc()).limit(1)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_for_diagnosis(self, diagnosis_id: int) -> List[TreatmentProtocol]:
        """Get all treatment protocols for a diagnosis"""
        result = await self.session.execute(
            select(TreatmentProtocol)
            .where(TreatmentProtocol.diagnosis_id == diagnosis_id)
            .order_by(TreatmentProtocol.severity_level, TreatmentProtocol.version.desc())
        )
        return result.scalars().all()
    
    async def create(self, **kwargs) -> TreatmentProtocol:
        """Create a new treatment protocol"""
        protocol = TreatmentProtocol(**kwargs)
        self.session.add(protocol)
        await self.session.commit()
        await self.session.refresh(protocol)
        return protocol

class MedicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_generic_name(self, generic_name: str) -> Optional[Medication]:
        """Get medication by generic name"""
        result = await self.session.execute(
            select(Medication).where(func.lower(Medication.generic_name) == func.lower(generic_name))
        )
        return result.scalar_one_or_none()
    
    async def search_by_name(self, query: str, limit: int = 10) -> List[Medication]:
        """Search medications by generic or brand name"""
        result = await self.session.execute(
            select(Medication)
            .where(
                or_(
                    Medication.generic_name.ilike(f"%{query}%"),
                    func.array_to_string(Medication.brand_names, ' ').ilike(f"%{query}%")
                )
            )
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_category(self, category: str) -> List[Medication]:
        """Get medications by category"""
        result = await self.session.execute(
            select(Medication).where(func.lower(Medication.category) == func.lower(category))
        )
        return result.scalars().all()
    
    async def get_pediatric_approved(self) -> List[Medication]:
        """Get all pediatric-approved medications"""
        result = await self.session.execute(
            select(Medication).where(Medication.pediatric_approved == True)
        )
        return result.scalars().all()

class DosingGuidelineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_guidelines_for_medication_and_diagnosis(
        self, medication_id: int, diagnosis_id: Optional[int] = None
    ) -> List[DosingGuideline]:
        """Get dosing guidelines for medication and optionally diagnosis"""
        query = select(DosingGuideline).where(DosingGuideline.medication_id == medication_id)
        
        if diagnosis_id:
            query = query.where(DosingGuideline.diagnosis_id == diagnosis_id)
        
        result = await self.session.execute(query)
        return result.scalars().all()

class ClinicalGuidelineRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_source(self, source: str) -> List[ClinicalGuideline]:
        """Get guidelines by source organization"""
        result = await self.session.execute(
            select(ClinicalGuideline).where(func.lower(ClinicalGuideline.source) == func.lower(source))
        )
        return result.scalars().all()
    
    async def search_by_title(self, query: str, limit: int = 10) -> List[ClinicalGuideline]:
        """Search guidelines by title"""
        result = await self.session.execute(
            select(ClinicalGuideline)
            .where(ClinicalGuideline.title.ilike(f"%{query}%"))
            .limit(limit)
        )
        return result.scalars().all()

class CommunicationTemplateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_template(
        self, 
        diagnosis_id: int, 
        template_type: str, 
        age_range: Optional[str] = None,
        language: str = "en"
    ) -> Optional[CommunicationTemplate]:
        """Get communication template for diagnosis and type"""
        query = select(CommunicationTemplate).where(
            and_(
                CommunicationTemplate.diagnosis_id == diagnosis_id,
                func.lower(CommunicationTemplate.template_type) == func.lower(template_type),
                CommunicationTemplate.language == language
            )
        )
        
        if age_range:
            query = query.where(
                or_(
                    CommunicationTemplate.age_range == age_range,
                    CommunicationTemplate.age_range.is_(None)
                )
            )
        
        result = await self.session.execute(query.limit(1))
        return result.scalar_one_or_none()

class QueryLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_query(
        self, 
        user_id: str, 
        diagnosis_input: str, 
        patient_age: Optional[int] = None,
        treatment_plan_generated: bool = False,
        tokens_used: Optional[int] = None,
        response_time_ms: Optional[int] = None
    ) -> QueryLog:
        """Log a user query"""
        log_entry = QueryLog(
            user_id=user_id,
            diagnosis_input=diagnosis_input,
            patient_age=patient_age,
            treatment_plan_generated=treatment_plan_generated,
            tokens_used=tokens_used,
            response_time_ms=response_time_ms
        )
        self.session.add(log_entry)
        await self.session.commit()
        await self.session.refresh(log_entry)
        return log_entry
    
    async def get_usage_stats(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get usage statistics for a user"""
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        result = await self.session.execute(
            select(
                func.count(QueryLog.id).label("total_queries"),
                func.sum(QueryLog.tokens_used).label("total_tokens"),
                func.avg(QueryLog.response_time_ms).label("avg_response_time")
            )
            .where(
                and_(
                    QueryLog.user_id == user_id,
                    QueryLog.timestamp >= cutoff_date
                )
            )
        )
        
        stats = result.one()
        return {
            "total_queries": stats.total_queries or 0,
            "total_tokens": stats.total_tokens or 0,
            "avg_response_time_ms": float(stats.avg_response_time or 0),
            "period_days": days
        }

class LicenseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_key(self, license_key: str) -> Optional[License]:
        """Get license by key"""
        result = await self.session.execute(
            select(License).where(License.license_key == license_key)
        )
        return result.scalar_one_or_none()
    
    async def get_active_licenses(self) -> List[License]:
        """Get all active licenses"""
        result = await self.session.execute(
            select(License).where(License.is_active == True)
        )
        return result.scalars().all()

# Repository factory
class RepositoryFactory:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    @property
    def diagnoses(self) -> DiagnosisRepository:
        return DiagnosisRepository(self.session)
    
    @property
    def treatment_protocols(self) -> TreatmentProtocolRepository:
        return TreatmentProtocolRepository(self.session)
    
    @property
    def medications(self) -> MedicationRepository:
        return MedicationRepository(self.session)
    
    @property
    def dosing_guidelines(self) -> DosingGuidelineRepository:
        return DosingGuidelineRepository(self.session)
    
    @property
    def clinical_guidelines(self) -> ClinicalGuidelineRepository:
        return ClinicalGuidelineRepository(self.session)
    
    @property
    def communication_templates(self) -> CommunicationTemplateRepository:
        return CommunicationTemplateRepository(self.session)
    
    @property
    def query_logs(self) -> QueryLogRepository:
        return QueryLogRepository(self.session)
    
    @property
    def licenses(self) -> LicenseRepository:
        return LicenseRepository(self.session)