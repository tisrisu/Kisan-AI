"""
KisanAI — History & Reference Data API Routes
"""

import json
import logging
from pathlib import Path
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from app.db.database import get_db
from app.models.models import (
    Submission, Diagnosis, Disease, Medication, District,
    CropVariety, Feedback
)
from app.schemas.schemas import (
    HistoryItem, HistoryResponse, DistrictItem, CropItem,
    DiseaseDetailResponse, MedicationItem, HealthResponse
)
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# ────────────────────────────────────────────
# History
# ────────────────────────────────────────────

@router.get("/history/{farmer_id}", response_model=HistoryResponse)
async def get_history(
    farmer_id: int,
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """Get past diagnoses for a farmer."""
    offset = (page - 1) * per_page

    # Count total
    count_q = select(func.count()).select_from(Submission).where(
        Submission.farmer_id == farmer_id
    )
    total_result = await db.execute(count_q)
    total = total_result.scalar() or 0

    # Get submissions with joins
    query = (
        select(Submission)
        .where(Submission.farmer_id == farmer_id)
        .order_by(desc(Submission.created_at))
        .offset(offset)
        .limit(per_page)
    )
    result = await db.execute(query)
    submissions = result.scalars().all()

    items = []
    for sub in submissions:
        # Get diagnosis for this submission
        diag_q = select(Diagnosis).where(Diagnosis.submission_id == sub.id)
        diag_result = await db.execute(diag_q)
        diag = diag_result.scalar_one_or_none()

        # Check feedback
        feedback_given = False
        if diag:
            fb_q = select(Feedback).where(Feedback.diagnosis_id == diag.id)
            fb_result = await db.execute(fb_q)
            feedback_given = fb_result.scalar_one_or_none() is not None

        # Get crop name
        crop_name = None
        if sub.crop_variety_id:
            crop_q = select(CropVariety).where(CropVariety.id == sub.crop_variety_id)
            crop_result = await db.execute(crop_q)
            crop = crop_result.scalar_one_or_none()
            crop_name = crop.name if crop else None

        # Get district name
        district_name = None
        if sub.district_id:
            dist_q = select(District).where(District.id == sub.district_id)
            dist_result = await db.execute(dist_q)
            dist = dist_result.scalar_one_or_none()
            district_name = dist.name if dist else None

        items.append(HistoryItem(
            submission_id=sub.id,
            diagnosis_id=diag.id if diag else None,
            image_url=sub.image_url or sub.image_path,
            disease_name=diag.disease_name if diag else None,
            confidence=diag.confidence if diag else None,
            severity=diag.severity if diag and diag.severity else None,
            crop_name=crop_name,
            district_name=district_name,
            season=sub.season if sub.season else None,
            feedback_given=feedback_given,
            created_at=sub.created_at,
        ))

    return HistoryResponse(items=items, total=total, page=page, per_page=per_page)


# ────────────────────────────────────────────
# Districts
# ────────────────────────────────────────────

@router.get("/districts", response_model=list[DistrictItem])
async def get_districts(db: AsyncSession = Depends(get_db)):
    """List all available districts."""
    result = await db.execute(select(District).order_by(District.state, District.name))
    districts = result.scalars().all()

    return [
        DistrictItem(
            id=d.id,
            name=d.name,
            state=d.state,
            code=d.code,
            major_crops=d.major_crops or [],
            climate=d.climate,
            submission_count=d.submission_count or 0,
            has_custom_model=d.model_version is not None,
        )
        for d in districts
    ]


# ────────────────────────────────────────────
# Crops
# ────────────────────────────────────────────

@router.get("/crops", response_model=list[CropItem])
async def get_crops(
    category: str = Query(default=None, description="Filter by crop category"),
    db: AsyncSession = Depends(get_db),
):
    """List all crop varieties."""
    query = select(CropVariety).order_by(CropVariety.category, CropVariety.name)
    if category:
        query = query.where(CropVariety.category == category)

    result = await db.execute(query)
    crops = result.scalars().all()

    return [
        CropItem(
            id=c.id,
            name=c.name,
            category=c.category,
            translations=c.translations or {},
        )
        for c in crops
    ]


# ────────────────────────────────────────────
# Diseases
# ────────────────────────────────────────────

@router.get("/diseases/{disease_id}", response_model=DiseaseDetailResponse)
async def get_disease_detail(disease_id: int, db: AsyncSession = Depends(get_db)):
    """Get full disease details with medications."""
    result = await db.execute(select(Disease).where(Disease.id == disease_id))
    disease = result.scalar_one_or_none()

    if not disease:
        raise HTTPException(status_code=404, detail="Disease not found")

    # Get medications
    med_result = await db.execute(
        select(Medication).where(Medication.disease_id == disease_id)
    )
    meds = med_result.scalars().all()

    return DiseaseDetailResponse(
        id=disease.id,
        name=disease.name,
        scientific_name=disease.scientific_name,
        description=disease.description,
        affected_crops=disease.affected_crops or [],
        common_in=disease.common_in or [],
        medications=[
            MedicationItem(
                id=m.id,
                name=m.name,
                dosage=m.dosage,
                application=m.application,
                frequency=m.frequency,
                translations=m.translations or {},
            )
            for m in meds
        ],
        translations=disease.translations or {},
    )


# ────────────────────────────────────────────
# Health
# ────────────────────────────────────────────

@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    """System health check."""
    # Check database
    db_status = "healthy"
    try:
        await db.execute(select(func.count()).select_from(Disease))
    except Exception:
        db_status = "unhealthy"

    # Check Redis
    redis_status = "healthy"
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
    except Exception:
        redis_status = "unavailable"

    # Check ML model
    ml_status = "loaded"
    model_path = Path(settings.MODEL_DIR) / "base" / "best_model.pth"
    if not model_path.exists():
        ml_status = "no_model_loaded (demo mode)"

    return HealthResponse(
        status="healthy" if db_status == "healthy" else "degraded",
        version=settings.APP_VERSION,
        database=db_status,
        redis=redis_status,
        ml_model=ml_status,
        timestamp=datetime.utcnow(),
    )
