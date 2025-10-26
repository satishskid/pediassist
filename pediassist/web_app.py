"""
Web interface for PediAssist using FastAPI
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional, Dict, Any
import json
import os
from pathlib import Path

from .config import settings
from .core.diagnosis_parser import DiagnosisParser
from .core.treatment_generator import TreatmentGenerator
from .core.communication_engine import CommunicationEngine
from .database import DatabaseManager
from .llm.provider import LLMManager
from .security import license_manager

# Initialize FastAPI app
app = FastAPI(
    title="PediAssist",
    description="Pediatric Clinical Decision Support System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Create templates and static directories
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"
templates_dir.mkdir(exist_ok=True)
static_dir.mkdir(exist_ok=True)

# Initialize templates and static files
templates = Jinja2Templates(directory=str(templates_dir))
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Pydantic models for API requests
class DiagnosisRequest(BaseModel):
    age: int
    sex: str = "unknown"
    weight: Optional[float] = None
    chief_complaint: str
    history: Optional[str] = None
    complexity: str = "standard"
    output_format: str = "detailed"

class TreatmentRequest(BaseModel):
    diagnosis: str
    age: int
    weight: Optional[float] = None
    complexity: str = "standard"
    output_format: str = "detailed"

class CommunicationRequest(BaseModel):
    content: str
    audience: str = "patient"
    age_group: str = "child"
    language: str = "english"

# Initialize core components
db_manager = DatabaseManager(settings.database_url)

# Create LLM config dictionary
llm_config = {
    "provider": settings.llm_provider,
    "model": settings.model if settings.llm_provider != "ollama" else settings.local_model,
    "api_key": getattr(settings, f"{settings.llm_provider.upper()}_API_KEY", None),
    "base_url": getattr(settings, f"{settings.llm_provider.upper()}_BASE_URL", None),
    "temperature": 0.1,
    "max_tokens": 4000,
    "debug": settings.debug
}

llm_manager = LLMManager(llm_config)
diagnosis_parser = DiagnosisParser()
treatment_generator = TreatmentGenerator()
communication_engine = CommunicationEngine()

# Dependency to check license
def verify_license():
    """Verify that a valid license is configured"""
    if not settings.license_key:
        raise HTTPException(status_code=403, detail="No license key configured")
    
    validation = license_manager.verify_license(settings.license_key)
    if not validation["valid"]:
        raise HTTPException(status_code=403, detail=f"Invalid license: {validation.get('error', 'Unknown error')}")
    
    return validation

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with main interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/status")
async def get_status():
    """Get system status"""
    try:
        # Check database
        db_status = "Connected" if await db_manager.check_connection() else "Disconnected"
        
        # Check LLM
        llm_health = await llm_manager.health_check()
        llm_status = "Ready" if llm_health["status"] == "healthy" else "Not Ready"
        
        # Check license
        license_info = None
        if settings.license_key:
            license_validation = license_manager.verify_license(settings.license_key)
            license_status = "Valid" if license_validation["valid"] else "Invalid"
            license_info = {
                "status": license_status,
                "type": license_validation.get("license_info", {}).get("license_type", "Unknown"),
                "features": license_validation.get("features", [])
            }
        else:
            license_info = {"status": "Not configured", "type": "None", "features": []}
        
        return {
            "system": {
                "name": settings.app_name,
                "version": settings.app_version,
                "database": db_status,
                "llm_provider": settings.llm_provider,
                "model": settings.local_model if settings.llm_provider == "ollama" else settings.model
            },
            "license": license_info
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

@app.post("/api/diagnose")
async def diagnose(request: DiagnosisRequest, license_info: Dict = Depends(verify_license)):
    """Generate diagnosis based on patient information"""
    try:
        # Create patient data dictionary
        patient_data = {
            "age": request.age,
            "sex": request.sex,
            "weight": request.weight,
            "chief_complaint": request.chief_complaint,
            "history": request.history or ""
        }
        
        # Generate diagnosis
        diagnosis_result = diagnosis_parser.parse(
            query=request.chief_complaint,
            diagnosis_text=request.chief_complaint
        )
        
        # Track usage
        await db_manager.track_usage(
            operation="diagnosis",
            input_data=patient_data,
            output_data=diagnosis_result
        )
        
        return {
            "success": True,
            "diagnosis": diagnosis_result,
            "safety_validation": {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diagnosis generation failed: {str(e)}")

@app.post("/api/treatment")
async def generate_treatment(request: TreatmentRequest, license_info: Dict = Depends(verify_license)):
    """Generate treatment plan based on diagnosis"""
    try:
        # Create patient data
        patient_data = {
            "age": request.age,
            "weight": request.weight
        }
        
        # Generate treatment plan
        treatment_result = treatment_generator.generate_protocol(
            diagnosis=request.diagnosis,
            age_group=f"age_{request.age}",
            urgency_level=request.complexity
        )
        
        # Track usage
        await db_manager.track_usage(
            operation="treatment",
            input_data={"diagnosis": request.diagnosis, "patient_data": patient_data},
            output_data=treatment_result
        )
        
        return {
            "success": True,
            "treatment": treatment_result,
            "safety_validation": {}
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Treatment generation failed: {str(e)}")

@app.post("/api/communicate")
async def communicate(request: CommunicationRequest, license_info: Dict = Depends(verify_license)):
    """Generate patient-friendly communication"""
    try:
        # Generate communication
        communication_result = communication_engine.generate_communication(
            condition=request.content,
            age_group=request.age_group,
            communication_style=request.audience
        )
        
        # Track usage
        await db_manager.track_usage(
            operation="communication",
            input_data={
                "content": request.content,
                "audience": request.audience,
                "age_group": request.age_group,
                "language": request.language
            },
            output_data=communication_result
        )
        
        return {
            "success": True,
            "communication": communication_result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Communication generation failed: {str(e)}")

@app.get("/api/usage")
async def get_usage_stats(license_info: Dict = Depends(verify_license)):
    """Get usage statistics"""
    try:
        stats = await db_manager.get_usage_stats()
        return {
            "success": True,
            "usage_stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Usage stats retrieval failed: {str(e)}")

# Simple form-based interface
@app.get("/simple", response_class=HTMLResponse)
async def simple_interface(request: Request):
    """Simple web form interface"""
    return templates.TemplateResponse("simple.html", {"request": request})

@app.post("/simple/diagnose", response_class=HTMLResponse)
async def simple_diagnose(
    request: Request,
    age: int = Form(...),
    sex: str = Form("unknown"),
    weight: Optional[float] = Form(None),
    chief_complaint: str = Form(...),
    history: Optional[str] = Form(None),
    complexity: str = Form("standard")
):
    """Simple diagnosis form handler"""
    try:
        # Verify license - this will raise HTTPException if invalid
        license_validation = verify_license()
        
        # Create patient data
        patient_data = {
            "age": age,
            "sex": sex,
            "weight": weight,
            "chief_complaint": chief_complaint,
            "history": history or "",
            "complexity": complexity
        }
        
        # Generate diagnosis
        diagnosis_result = diagnosis_parser.parse(
            query=chief_complaint,
            diagnosis_text=chief_complaint
        )
        
        # Track usage
        await db_manager.track_usage(
            operation="diagnosis",
            input_data=patient_data,
            output_data=diagnosis_result
        )
        
        return templates.TemplateResponse("simple.html", {
            "request": request,
            "result": diagnosis_result,
            "patient_data": patient_data
        })
        
    except HTTPException as e:
        return templates.TemplateResponse("simple.html", {
            "request": request,
            "error": str(e.detail)
        })
    except Exception as e:
        return templates.TemplateResponse("simple.html", {
            "request": request,
            "error": f"Diagnosis failed: {str(e)}"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)