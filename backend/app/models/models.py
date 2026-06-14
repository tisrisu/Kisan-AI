"""
KisanAI — SQLAlchemy ORM Models
"""

import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Text, Boolean, DateTime,
    ForeignKey, JSON
)
from sqlalchemy.orm import relationship
from app.db.database import Base
import enum


class SeasonEnum(str, enum.Enum):
    KHARIF = "kharif"
    RABI = "rabi"
    ZAID = "zaid"


class SeverityEnum(str, enum.Enum):
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class LanguageEnum(str, enum.Enum):
    EN = "en"
    HI = "hi"
    TE = "te"
    TA = "ta"


# ────────────────────────────────────────────
# Farmer
# ────────────────────────────────────────────

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(15), unique=True, nullable=True)
    name = Column(String(100), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    language_pref = Column(String(10), default="en")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    submissions = relationship("Submission", back_populates="farmer")
    district = relationship("District", back_populates="farmers")


# ────────────────────────────────────────────
# District
# ────────────────────────────────────────────

class District(Base):
    __tablename__ = "districts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, nullable=False)
    major_crops = Column(JSON, default=list)
    climate = Column(String(50), nullable=True)
    model_version = Column(String(50), nullable=True)
    submission_count = Column(Integer, default=0)

    farmers = relationship("Farmer", back_populates="district")
    submissions = relationship("Submission", back_populates="district")


# ────────────────────────────────────────────
# Crop Variety
# ────────────────────────────────────────────

class CropVariety(Base):
    __tablename__ = "crop_varieties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    category = Column(String(50), nullable=False)
    translations = Column(JSON, default=dict)

    submissions = relationship("Submission", back_populates="crop_variety")


# ────────────────────────────────────────────
# Submission (farmer upload)
# ────────────────────────────────────────────

class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    farmer_id = Column(Integer, ForeignKey("farmers.id"), nullable=True)
    image_path = Column(String(500), nullable=False)
    image_url = Column(String(500), nullable=True)
    crop_variety_id = Column(Integer, ForeignKey("crop_varieties.id"), nullable=True)
    district_id = Column(Integer, ForeignKey("districts.id"), nullable=True)
    season = Column(String(20), default="kharif")
    symptom_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    farmer = relationship("Farmer", back_populates="submissions")
    crop_variety = relationship("CropVariety", back_populates="submissions")
    district = relationship("District", back_populates="submissions")
    diagnosis = relationship("Diagnosis", back_populates="submission", uselist=False)


# ────────────────────────────────────────────
# Diagnosis (ML prediction)
# ────────────────────────────────────────────

class Diagnosis(Base):
    __tablename__ = "diagnoses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    submission_id = Column(Integer, ForeignKey("submissions.id"), nullable=False)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=False)
    disease_name = Column(String(200), nullable=False)
    scientific_name = Column(String(200), nullable=True)
    confidence = Column(Float, nullable=False)
    severity = Column(String(20), default="moderate")
    severity_confidence = Column(Float, nullable=True)
    top_predictions = Column(JSON, default=list)  # Top 3 predictions
    model_version = Column(String(50), nullable=True)
    model_type = Column(String(50), default="base")  # base or district_specific
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    submission = relationship("Submission", back_populates="diagnosis")
    disease = relationship("Disease")
    feedback = relationship("Feedback", back_populates="diagnosis", uselist=False)


# ────────────────────────────────────────────
# Disease
# ────────────────────────────────────────────

class Disease(Base):
    __tablename__ = "diseases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    scientific_name = Column(String(200), nullable=True)
    description = Column(Text, nullable=True)
    affected_crops = Column(JSON, default=list)
    common_in = Column(JSON, default=list)
    translations = Column(JSON, default=dict)

    medications = relationship("Medication", back_populates="disease")


# ────────────────────────────────────────────
# Medication
# ────────────────────────────────────────────

class Medication(Base):
    __tablename__ = "medications"

    id = Column(Integer, primary_key=True, autoincrement=True)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=False)
    name = Column(String(200), nullable=False)
    dosage = Column(String(200), nullable=False)
    application = Column(String(200), nullable=True)
    frequency = Column(String(200), nullable=True)
    precautions = Column(JSON, default=list)
    translations = Column(JSON, default=dict)

    disease = relationship("Disease", back_populates="medications")


# ────────────────────────────────────────────
# Feedback
# ────────────────────────────────────────────

class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    diagnosis_id = Column(Integer, ForeignKey("diagnoses.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    corrected_disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=True)
    corrected_severity = Column(String(20), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    diagnosis = relationship("Diagnosis", back_populates="feedback")
    corrected_disease = relationship("Disease")
