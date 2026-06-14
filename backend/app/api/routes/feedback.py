"""
KisanAI — Feedback API Route
POST /api/v1/feedback — Submit diagnosis feedback
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.models.models import Feedback, Diagnosis, Submission, District
from app.schemas.schemas import FeedbackRequest, FeedbackResponse
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit feedback on a diagnosis.
    Farmer confirms or corrects the AI diagnosis.
    Verified data feeds back into the district's training set.
    """
    # Verify diagnosis exists
    result = await db.execute(select(Diagnosis).where(Diagnosis.id == request.diagnosis_id))
    diagnosis = result.scalar_one_or_none()

    if not diagnosis:
        raise HTTPException(status_code=404, detail="Diagnosis not found")

    # Check if feedback already exists
    existing = await db.execute(
        select(Feedback).where(Feedback.diagnosis_id == request.diagnosis_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Feedback already submitted for this diagnosis")

    # Create feedback
    feedback = Feedback(
        diagnosis_id=request.diagnosis_id,
        is_correct=request.is_correct,
        corrected_disease_id=request.corrected_disease_id,
        corrected_severity=request.corrected_severity,
        notes=request.notes,
    )
    db.add(feedback)

    # Update district submission count
    submission = await db.execute(
        select(Submission).where(Submission.id == diagnosis.submission_id)
    )
    sub = submission.scalar_one_or_none()
    district_count = 0
    fine_tune_eligible = False

    if sub and sub.district_id:
        district = await db.execute(select(District).where(District.id == sub.district_id))
        dist = district.scalar_one_or_none()
        if dist:
            dist.submission_count = (dist.submission_count or 0) + 1
            district_count = dist.submission_count
            fine_tune_eligible = district_count >= settings.MIN_SUBMISSIONS_FOR_FINETUNE

    await db.commit()
    await db.refresh(feedback)

    message = "Thank you for your feedback!"
    if fine_tune_eligible:
        message += f" District has {district_count} verified submissions — eligible for model fine-tuning!"

    return FeedbackResponse(
        id=feedback.id,
        diagnosis_id=request.diagnosis_id,
        is_correct=request.is_correct,
        message=message,
        district_submission_count=district_count,
        fine_tune_eligible=fine_tune_eligible,
    )
