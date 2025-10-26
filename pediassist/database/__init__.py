"""
Database initialization and migration utilities
"""

import asyncio
import os
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text
import structlog

from .models import Base
from .repository import RepositoryFactory

logger = structlog.get_logger(__name__)

class DatabaseManager:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
        )
        self.async_session = async_sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Create all database tables"""
        logger.info("Creating database tables")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    
    async def drop_tables(self):
        """Drop all database tables (use with caution)"""
        logger.warning("Dropping all database tables")
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("Database tables dropped")
    
    async def check_connection(self) -> bool:
        """Test database connection"""
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
                logger.info("Database connection successful")
                return True
        except Exception as e:
            logger.error("Database connection failed", error=str(e))
            return False
    
    async def get_session(self) -> AsyncSession:
        """Get a new database session"""
        return self.async_session()
    
    def get_repository_factory(self, session: AsyncSession) -> RepositoryFactory:
        """Get repository factory for the given session"""
        return RepositoryFactory(session)
    
    async def track_usage(self, operation: str, input_data: dict, output_data: dict):
        """Track API usage for analytics and monitoring"""
        try:
            async with self.async_session() as session:
                # For now, just log the usage
                logger.info("API usage tracked", 
                           operation=operation, 
                           input_data=input_data, 
                           output_data=output_data)
                # TODO: Implement actual usage tracking to database when models are ready
                await session.commit()
        except Exception as e:
            logger.error("Failed to track usage", error=str(e))
    
    async def get_usage_stats(self) -> dict:
        """Get usage statistics"""
        # For now, return basic stats
        return {
            "total_requests": 0,
            "diagnosis_requests": 0,
            "treatment_requests": 0,
            "communication_requests": 0,
            "last_updated": "2024-01-01T00:00:00Z"
        }

# Sample data for initial database population
SAMPLE_DIAGNOSES = [
    {
        "name": "Asthma",
        "icd10_code": "J45.909",
        "category": "Pulmonology",
        "subspecialty": "Pulmonology",
        "description": "Chronic inflammatory disease of the airways characterized by variable and recurring symptoms, reversible airflow obstruction, and bronchial hyperresponsiveness.",
        "age_group": "all_ages",
        "severity_levels": ["mild", "moderate", "severe"],
        "keywords": ["wheezing", "cough", "dyspnea", "chest tightness"]
    },
    {
        "name": "Type 1 Diabetes",
        "icd10_code": "E10.9",
        "category": "Endocrinology",
        "subspecialty": "Endocrinology",
        "description": "Autoimmune destruction of pancreatic beta cells leading to absolute insulin deficiency.",
        "age_group": "all_ages",
        "severity_levels": ["new_onset", "stable", "complicated"],
        "keywords": ["polyuria", "polydipsia", "weight loss", "ketosis"]
    },
    {
        "name": "Attention Deficit Hyperactivity Disorder",
        "icd10_code": "F90.9",
        "category": "Psychiatry",
        "subspecialty": "Child Psychiatry",
        "description": "Neurodevelopmental disorder characterized by inattention, hyperactivity, and impulsivity.",
        "age_group": "pediatric",
        "severity_levels": ["mild", "moderate", "severe"],
        "keywords": ["inattention", "hyperactivity", "impulsivity", "executive dysfunction"]
    },
    {
        "name": "Pneumonia",
        "icd10_code": "J18.9",
        "category": "Infectious Disease",
        "subspecialty": "General Pediatrics",
        "description": "Infection of the lung parenchyma, most commonly bacterial or viral in origin.",
        "age_group": "all_ages",
        "severity_levels": ["mild", "moderate", "severe", "critical"],
        "keywords": ["fever", "cough", "tachypnea", "crackles"]
    },
    {
        "name": "Epilepsy",
        "icd10_code": "G40.909",
        "category": "Neurology",
        "subspecialty": "Neurology",
        "description": "Chronic disorder characterized by recurrent, unprovoked seizures.",
        "age_group": "all_ages",
        "severity_levels": ["controlled", "refractory", "intractable"],
        "keywords": ["seizure", "convulsion", "epileptiform", "ictal"]
    }
]

SAMPLE_MEDICATIONS = [
    {
        "generic_name": "Albuterol",
        "brand_names": ["ProAir", "Ventolin", "Proventil"],
        "category": "Bronchodilator",
        "drug_class": "Beta-2 Adrenergic Agonist",
        "pediatric_approved": True,
        "adult_approved": True,
        "controlled_substance": False,
        "controlled_substance_schedule": None,
        "dosage_forms": ["inhaler", "nebulizer solution", "tablet", "syrup"],
        "strengths": ["90mcg/inhalation", "0.083%", "2mg", "4mg"],
        "mechanism_of_action": "Selective beta-2 adrenergic receptor agonist causing bronchial smooth muscle relaxation"
    },
    {
        "generic_name": "Insulin Glargine",
        "brand_names": ["Lantus", "Basaglar", "Toujeo"],
        "category": "Insulin",
        "drug_class": "Long-acting Insulin",
        "pediatric_approved": True,
        "adult_approved": True,
        "controlled_substance": False,
        "controlled_substance_schedule": None,
        "dosage_forms": ["injection"],
        "strengths": ["100 units/mL", "300 units/mL"],
        "mechanism_of_action": "Long-acting insulin analog with 24-hour duration of action"
    },
    {
        "generic_name": "Methylphenidate",
        "brand_names": ["Ritalin", "Concerta", "Focalin"],
        "category": "Stimulant",
        "drug_class": "Central Nervous System Stimulant",
        "pediatric_approved": True,
        "adult_approved": True,
        "controlled_substance": True,
        "controlled_substance_schedule": "Schedule II",
        "dosage_forms": ["tablet", "extended-release tablet", "capsule"],
        "strengths": ["5mg", "10mg", "18mg", "27mg", "36mg", "54mg"],
        "mechanism_of_action": "Blocks reuptake of norepinephrine and dopamine in the prefrontal cortex"
    },
    {
        "generic_name": "Amoxicillin",
        "brand_names": ["Amoxil", "Moxatag"],
        "category": "Antibiotic",
        "drug_class": "Penicillin",
        "pediatric_approved": True,
        "adult_approved": True,
        "controlled_substance": False,
        "controlled_substance_schedule": None,
        "dosage_forms": ["tablet", "capsule", "suspension", "chewable tablet"],
        "strengths": ["125mg/5mL", "250mg/5mL", "500mg", "875mg"],
        "mechanism_of_action": "Inhibits bacterial cell wall synthesis"
    },
    {
        "generic_name": "Levetiracetam",
        "brand_names": ["Keppra", "Keppra XR"],
        "category": "Anticonvulsant",
        "drug_class": "Pyrrolidine Anticonvulsant",
        "pediatric_approved": True,
        "adult_approved": True,
        "controlled_substance": False,
        "controlled_substance_schedule": None,
        "dosage_forms": ["tablet", "extended-release tablet", "solution", "injection"],
        "strengths": ["100mg/mL", "250mg", "500mg", "750mg", "1000mg"],
        "mechanism_of_action": "Binds to synaptic vesicle protein 2A (SV2A)"
    }
]

SAMPLE_TREATMENT_PROTOCOLS = [
    {
        "diagnosis_name": "Asthma",
        "severity_level": "mild",
        "age_group": "pediatric",
        "protocol": """
## Mild Asthma Exacerbation - Pediatric

### Assessment
- Peak flow >80% predicted
- Mild symptoms: occasional wheeze, cough
- No significant distress

### Treatment Plan
1. **Albuterol 2.5mg nebulizer** or **4-8 puffs MDI with spacer**
   - Frequency: Every 4-6 hours PRN
   - Monitor for improvement

2. **Continue controller therapy**
   - If on inhaled corticosteroids, continue
   - Consider increasing dose if frequent symptoms

3. **Patient Education**
   - Proper inhaler technique
   - Trigger identification and avoidance
   - When to seek medical attention

### Follow-up
- Return if symptoms worsen or don't improve in 24-48 hours
- Regular follow-up in 1-2 weeks
""",
        "medications": ["Albuterol"],
        "duration": "24-48 hours",
        "follow_up_required": True,
        "emergency_indicators": ["respiratory distress", "peak flow <50%", "cyanosis", "altered mental status"]
    },
    {
        "diagnosis_name": "Type 1 Diabetes",
        "severity_level": "new_onset",
        "age_group": "pediatric",
        "protocol": """
## New Onset Type 1 Diabetes - Pediatric

### Initial Assessment
- Confirm diagnosis: glucose >200mg/dL, HbA1c, C-peptide
- Rule out diabetic ketoacidosis (DKA)
- Assess for precipitating illness

### Treatment Initiation
1. **Insulin Therapy**
   - Start with basal-bolus regimen
   - Insulin glargine 0.2-0.3 units/kg/day
   - Rapid-acting insulin with meals

2. **Blood Glucose Monitoring**
   - Check 4 times daily minimum
   - Target range: 70-180 mg/dL
   - Record readings for pattern analysis

3. **Nutrition Education**
   - Carbohydrate counting principles
   - Meal timing and consistency
   - Hypoglycemia management

4. **Family Education**
   - Insulin administration technique
   - Glucagon emergency use
   - When to contact provider

### Monitoring
- Daily phone contact first week
- Weekly visits first month
- HbA1c recheck in 3 months
""",
        "medications": ["Insulin Glargine"],
        "duration": "ongoing",
        "follow_up_required": True,
        "emergency_indicators": ["persistent vomiting", "ketones >0.6", "altered mental status", "severe hypoglycemia"]
    }
]

async def populate_sample_data(session: AsyncSession):
    """Populate database with sample data"""
    logger.info("Populating database with sample data")
    
    from .repository import RepositoryFactory
    repo_factory = RepositoryFactory(session)
    
    # Create diagnoses
    diagnosis_map = {}
    for diagnosis_data in SAMPLE_DIAGNOSES:
        diagnosis = await repo_factory.diagnoses.create(**diagnosis_data)
        diagnosis_map[diagnosis_data["name"]] = diagnosis
        logger.info(f"Created diagnosis: {diagnosis.name}")
    
    # Create medications
    medication_map = {}
    for medication_data in SAMPLE_MEDICATIONS:
        medication = await repo_factory.medications.create(**medication_data)
        medication_map[medication_data["generic_name"]] = medication
        logger.info(f"Created medication: {medication.generic_name}")
    
    # Create treatment protocols
    for protocol_data in SAMPLE_TREATMENT_PROTOCOLS:
        diagnosis_name = protocol_data.pop("diagnosis_name")
        if diagnosis_name in diagnosis_map:
            protocol_data["diagnosis_id"] = diagnosis_map[diagnosis_name].id
            protocol = await repo_factory.treatment_protocols.create(**protocol_data)
            logger.info(f"Created treatment protocol: {protocol.severity_level} {diagnosis_name}")
    
    logger.info("Sample data population completed")

async def init_database(database_url: str, populate_sample: bool = True):
    """Initialize the database with tables and optional sample data"""
    logger.info("Initializing database")
    
    db_manager = DatabaseManager(database_url)
    
    # Test connection
    if not await db_manager.check_connection():
        raise ConnectionError("Failed to connect to database")
    
    # Create tables
    await db_manager.create_tables()
    
    # Populate sample data if requested
    if populate_sample:
        async with db_manager.get_session() as session:
            await populate_sample_data(session)
    
    logger.info("Database initialization completed")
    return db_manager