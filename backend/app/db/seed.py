"""
KisanAI — Database Seeder
Seeds diseases, medications, districts, and crop varieties from knowledge base JSON files.
"""

import json
import logging
from pathlib import Path

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.models.models import Disease, Medication, District, CropVariety
from app.config import settings

logger = logging.getLogger(__name__)


async def seed_knowledge_base():
    """Seed the database with knowledge base data if tables are empty."""
    async with AsyncSessionLocal() as session:
        # Check if already seeded
        result = await session.execute(select(Disease).limit(1))
        if result.scalar_one_or_none():
            logger.info("Knowledge base already seeded, skipping")
            return

        kb_dir = Path(settings.KNOWLEDGE_BASE_DIR)

        # Seed diseases
        diseases_file = kb_dir / "diseases.json"
        if diseases_file.exists():
            with open(diseases_file, "r", encoding="utf-8") as f:
                diseases = json.load(f)
            for d in diseases:
                disease = Disease(
                    id=d["id"],
                    name=d["name"],
                    scientific_name=d.get("scientific_name"),
                    description=d.get("description"),
                    affected_crops=d.get("affected_crops", []),
                    common_in=d.get("common_in", []),
                    translations=d.get("translations", {}),
                )
                session.add(disease)
            await session.flush()
            logger.info(f"Seeded {len(diseases)} diseases")

        # Seed medications
        medications_file = kb_dir / "medications.json"
        if medications_file.exists():
            with open(medications_file, "r", encoding="utf-8") as f:
                medications = json.load(f)
            for m in medications:
                medication = Medication(
                    id=m["id"],
                    disease_id=m["disease_id"],
                    name=m["name"],
                    dosage=m["dosage"],
                    application=m.get("application"),
                    frequency=m.get("frequency"),
                    translations=m.get("translations", {}),
                )
                session.add(medication)
            await session.flush()
            logger.info(f"Seeded {len(medications)} medications")

        # Seed districts
        districts_file = kb_dir / "districts.json"
        if districts_file.exists():
            with open(districts_file, "r", encoding="utf-8") as f:
                districts = json.load(f)
            for d in districts:
                district = District(
                    id=d["id"],
                    name=d["name"],
                    state=d["state"],
                    code=d["code"],
                    major_crops=d.get("major_crops", []),
                    climate=d.get("climate"),
                )
                session.add(district)
            await session.flush()
            logger.info(f"Seeded {len(districts)} districts")

        # Seed crop varieties
        crops_file = kb_dir / "crops.json"
        if crops_file.exists():
            with open(crops_file, "r", encoding="utf-8") as f:
                crops = json.load(f)
            for c in crops:
                crop = CropVariety(
                    id=c["id"],
                    name=c["name"],
                    category=c["category"],
                    translations=c.get("translations", {}),
                )
                session.add(crop)
            await session.flush()
            logger.info(f"Seeded {len(crops)} crop varieties")

        await session.commit()
        logger.info("✅ Knowledge base seeding complete!")
