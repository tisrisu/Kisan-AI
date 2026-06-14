"""
KisanAI — Diagnosis API Route
POST /api/v1/diagnose — Upload image + metadata → Get diagnosis
"""

import uuid
import logging
from datetime import datetime

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.models.models import Submission, Diagnosis, Disease, Medication, District, CropVariety
from app.schemas.schemas import DiagnoseResponse, PredictionItem, SeverityInfo, MedicationItem
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Global ML service instance (initialized in main.py)
_ml_service = None


def get_ml_service():
    global _ml_service
    if _ml_service is None:
        from app.services.ml_service import MLService
        _ml_service = MLService(
            model_dir=settings.MODEL_DIR,
            knowledge_base_dir=settings.KNOWLEDGE_BASE_DIR,
        )
    return _ml_service


@router.post("/diagnose", response_model=DiagnoseResponse)
async def diagnose(
    image: UploadFile = File(..., description="Leaf photo (JPG/PNG, max 10MB)"),
    crop_variety_id: int = Form(default=0, description="Crop variety ID"),
    district_id: int = Form(default=0, description="District ID"),
    season: str = Form(default="kharif", description="Season: kharif/rabi/zaid"),
    symptom_text: str = Form(default="", description="Symptom description (any language)"),
    farmer_id: int = Form(default=None, description="Farmer ID (optional)"),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a leaf photo + metadata and receive AI diagnosis.

    Flow:
    1. Validate and save uploaded image
    2. Preprocess image (380×380, normalize)
    3. Run multi-modal classifier (image + text + context)
    4. Look up medications from knowledge base
    5. Return full diagnosis with treatment recommendations
    """
    # Validate image
    if image.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail=f"Invalid image type: {image.content_type}. Allowed: JPG, PNG")

    image_bytes = await image.read()
    if len(image_bytes) > settings.MAX_IMAGE_SIZE:
        raise HTTPException(status_code=400, detail="Image too large. Maximum size is 10MB.")

    # Map season string to ID
    season_map = {"kharif": 0, "rabi": 1, "zaid": 2}
    season_id = season_map.get(season.lower(), 0)

    # Generate image path
    image_filename = f"{uuid.uuid4().hex}_{image.filename}"
    image_path = f"uploads/{image_filename}"

    # Save image locally
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    with open(os.path.join(settings.UPLOAD_DIR, image_filename), "wb") as f:
        f.write(image_bytes)

    # Run ML inference
    ml_service = get_ml_service()
    result = await ml_service.diagnose(
        image_bytes=image_bytes,
        symptom_text=symptom_text or "",
        district_id=district_id,
        season_id=season_id,
        crop_id=crop_variety_id,
    )

    primary = result["primary_diagnosis"]
    severity = result["severity"]

    # Save submission to database
    try:
        submission = Submission(
            farmer_id=farmer_id,
            image_path=image_path,
            crop_variety_id=crop_variety_id if crop_variety_id > 0 else None,
            district_id=district_id if district_id > 0 else None,
            season=season.lower(),
            symptom_text=symptom_text,
        )
        db.add(submission)
        await db.flush()

        # Save diagnosis
        diagnosis = Diagnosis(
            submission_id=submission.id,
            disease_id=primary["disease_id"],
            disease_name=primary["disease_name"],
            scientific_name=primary.get("scientific_name", ""),
            confidence=primary["confidence"],
            severity=severity["level"].lower(),
            severity_confidence=severity["confidence"],
            top_predictions=result["predictions"],
            model_type=result.get("model_info", {}).get("type", "base"),
        )
        db.add(diagnosis)
        await db.commit()
        await db.refresh(submission)
        await db.refresh(diagnosis)

        submission_id = submission.id
        diagnosis_id = diagnosis.id
    except Exception as e:
        logger.error(f"Database error: {e}")
        await db.rollback()
        submission_id = 0
        diagnosis_id = 0

    # Build response
    predictions = [PredictionItem(**p) for p in result["predictions"]]
    severity_info = SeverityInfo(**severity)

    medications = []
    for med in result.get("medications", []):
        medications.append(MedicationItem(
            id=med.get("id", 0),
            name=med["name"],
            dosage=med["dosage"],
            application=med.get("application"),
            frequency=med.get("frequency"),
            translations=med.get("translations", {}),
        ))

    # Disease translations
    disease_info = result.get("disease_info", {})

    return DiagnoseResponse(
        submission_id=submission_id,
        diagnosis_id=diagnosis_id,
        disease_name=primary["disease_name"],
        scientific_name=primary.get("scientific_name", ""),
        confidence=primary["confidence"],
        severity=severity_info,
        predictions=predictions,
        medications=medications,
        precautions=result.get("precautions", []),
        prevention_tips=result.get("prevention_tips", []),
        model_type=result.get("model_info", {}).get("type", "base"),
        translations=disease_info.get("translations", {}),
        created_at=datetime.utcnow(),
    )
