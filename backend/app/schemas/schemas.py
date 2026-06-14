"""
KisanAI — Pydantic Request/Response Schemas
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ────────────────────────────────────────────
# Diagnosis
# ────────────────────────────────────────────

class DiagnoseRequest(BaseModel):
    """Metadata sent alongside the image upload."""
    crop_variety_id: Optional[int] = None
    district_id: Optional[int] = None
    season: str = "kharif"  # kharif, rabi, zaid
    symptom_text: Optional[str] = ""
    farmer_id: Optional[int] = None


class PredictionItem(BaseModel):
    rank: int
    disease_id: int
    disease_name: str
    scientific_name: str
    confidence: float


class SeverityInfo(BaseModel):
    level: str  # Mild, Moderate, Severe
    level_id: int
    confidence: float
    distribution: dict


class MedicationItem(BaseModel):
    id: int
    name: str
    dosage: str
    application: Optional[str] = None
    frequency: Optional[str] = None
    translations: Optional[dict] = {}


class PrecautionItem(BaseModel):
    text: str
    translations: Optional[dict] = {}


class PreventionItem(BaseModel):
    text: str
    translations: Optional[dict] = {}


class DiagnoseResponse(BaseModel):
    """Full diagnosis response returned to the farmer."""
    submission_id: int
    diagnosis_id: int

    # Primary diagnosis
    disease_name: str
    scientific_name: str
    confidence: float
    severity: SeverityInfo

    # Top predictions
    predictions: List[PredictionItem]

    # Treatment
    medications: List[MedicationItem]
    precautions: List[str]
    prevention_tips: List[str]

    # Model info
    model_type: str  # base or district_specific
    translations: Optional[dict] = {}

    created_at: datetime


# ────────────────────────────────────────────
# Feedback
# ────────────────────────────────────────────

class FeedbackRequest(BaseModel):
    diagnosis_id: int
    is_correct: bool
    corrected_disease_id: Optional[int] = None
    corrected_severity: Optional[str] = None
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    diagnosis_id: int
    is_correct: bool
    message: str
    district_submission_count: Optional[int] = None
    fine_tune_eligible: bool = False


# ────────────────────────────────────────────
# History
# ────────────────────────────────────────────

class HistoryItem(BaseModel):
    submission_id: int
    diagnosis_id: Optional[int] = None
    image_url: Optional[str] = None
    disease_name: Optional[str] = None
    confidence: Optional[float] = None
    severity: Optional[str] = None
    crop_name: Optional[str] = None
    district_name: Optional[str] = None
    season: Optional[str] = None
    feedback_given: bool = False
    created_at: datetime


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int
    page: int
    per_page: int


# ────────────────────────────────────────────
# Districts, Crops
# ────────────────────────────────────────────

class DistrictItem(BaseModel):
    id: int
    name: str
    state: str
    code: str
    major_crops: List[str]
    climate: Optional[str] = None
    submission_count: int = 0
    has_custom_model: bool = False


class CropItem(BaseModel):
    id: int
    name: str
    category: str
    translations: Optional[dict] = {}


class DiseaseDetailResponse(BaseModel):
    id: int
    name: str
    scientific_name: Optional[str] = None
    description: Optional[str] = None
    affected_crops: List[str]
    common_in: List[str]
    medications: List[MedicationItem]
    translations: Optional[dict] = {}


# ────────────────────────────────────────────
# Health
# ────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    redis: str
    ml_model: str
    timestamp: datetime
