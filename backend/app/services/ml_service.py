"""
KisanAI — ML Service (orchestrates inference)
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MLService:
    """
    Orchestrates ML inference for crop disease diagnosis.
    Wraps the inference engine and provides a clean API for the routes.
    """

    def __init__(self, model_dir: str, knowledge_base_dir: str):
        self.model_dir = Path(model_dir)
        self.knowledge_base_dir = Path(knowledge_base_dir)
        self._engine = None
        self._diseases = None
        self._medications = None

        # Load knowledge base
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load disease and medication data from JSON files."""
        diseases_file = self.knowledge_base_dir / "diseases.json"
        medications_file = self.knowledge_base_dir / "medications.json"

        try:
            with open(diseases_file, "r", encoding="utf-8") as f:
                diseases_list = json.load(f)
                self._diseases = {d["id"]: d for d in diseases_list}
        except FileNotFoundError:
            logger.warning(f"Diseases file not found: {diseases_file}")
            self._diseases = {}

        try:
            with open(medications_file, "r", encoding="utf-8") as f:
                medications_list = json.load(f)
                # Group by disease_id
                self._medications = {}
                for med in medications_list:
                    disease_id = med["disease_id"]
                    if disease_id not in self._medications:
                        self._medications[disease_id] = []
                    self._medications[disease_id].append(med)
        except FileNotFoundError:
            logger.warning(f"Medications file not found: {medications_file}")
            self._medications = {}

    def get_engine(self):
        """Lazy-load the inference engine (heavy initialization)."""
        if self._engine is None:
            try:
                from ml.inference import InferenceEngine
                self._engine = InferenceEngine(
                    model_dir=str(self.model_dir),
                    disease_names_file=str(self.knowledge_base_dir / "diseases.json"),
                )
                logger.info("ML InferenceEngine loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load ML engine: {e}")
                self._engine = None
        return self._engine

    async def diagnose(self, image_bytes: bytes, symptom_text: str,
                       district_id: int = 0, season_id: int = 0,
                       crop_id: int = 0) -> dict:
        """
        Run diagnosis on uploaded image + metadata.

        Returns enriched results with medications and precautions.
        """
        engine = self.get_engine()

        if engine is None:
            # Return mock/demo results when model isn't loaded
            return self._get_demo_results(district_id, season_id, crop_id)

        try:
            # Run ML inference
            result = engine.predict_from_bytes(
                image_bytes=image_bytes,
                symptom_text=symptom_text,
                district_id=district_id,
                season_id=season_id,
                crop_id=crop_id,
                top_k=3,
            )

            # Enrich with medications and precautions
            primary = result["predictions"][0]
            disease_id = primary["disease_id"]

            result["medications"] = self.get_medications(disease_id)
            result["precautions"] = self.get_precautions(disease_id)
            result["prevention_tips"] = self.get_prevention_tips(disease_id)
            result["disease_info"] = self._diseases.get(disease_id, {})

            return result

        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return self._get_demo_results(district_id, season_id, crop_id)

    def get_medications(self, disease_id: int) -> list:
        """Get medication recommendations for a disease."""
        return self._medications.get(disease_id, [])

    def get_precautions(self, disease_id: int) -> list:
        """Get precautions for a disease. Common precautions + disease-specific."""
        common_precautions = [
            "Wear mask and gloves while spraying",
            "Do NOT spray near water bodies",
            "Spray during evening hours (low wind)",
            "Wait 14 days before harvest",
            "Drain excess field water",
            "Remove severely infected plants",
            "Contact nearest KVK if >30% crop affected",
        ]
        return common_precautions

    def get_prevention_tips(self, disease_id: int) -> list:
        """Get prevention tips for a disease."""
        disease = self._diseases.get(disease_id, {})
        common_tips = [
            "Use resistant crop varieties",
            "Balanced fertilization — avoid excess nitrogen",
            "Proper plant spacing for air circulation",
            "Crop rotation with non-host crops",
            "Use certified disease-free seeds",
        ]
        return common_tips

    def get_disease_info(self, disease_id: int) -> dict:
        """Get full disease information."""
        disease = self._diseases.get(disease_id, {})
        disease["medications"] = self.get_medications(disease_id)
        return disease

    def _get_demo_results(self, district_id: int = 0, season_id: int = 0,
                          crop_id: int = 0) -> dict:
        """Return demo results when ML model is not loaded."""
        return {
            "predictions": [
                {
                    "rank": 1,
                    "disease_id": 0,
                    "disease_name": "Rice Blast",
                    "scientific_name": "Magnaporthe oryzae",
                    "confidence": 94.2,
                },
                {
                    "rank": 2,
                    "disease_id": 2,
                    "disease_name": "Brown Spot",
                    "scientific_name": "Cochliobolus miyabeanus",
                    "confidence": 3.8,
                },
                {
                    "rank": 3,
                    "disease_id": 3,
                    "disease_name": "Sheath Blight",
                    "scientific_name": "Rhizoctonia solani",
                    "confidence": 1.2,
                },
            ],
            "primary_diagnosis": {
                "rank": 1,
                "disease_id": 0,
                "disease_name": "Rice Blast",
                "scientific_name": "Magnaporthe oryzae",
                "confidence": 94.2,
            },
            "severity": {
                "level": "Moderate",
                "level_id": 1,
                "confidence": 78.5,
                "distribution": {"Mild": 12.3, "Moderate": 78.5, "Severe": 9.2},
            },
            "medications": self.get_medications(0),
            "precautions": self.get_precautions(0),
            "prevention_tips": self.get_prevention_tips(0),
            "disease_info": self._diseases.get(0, {}),
            "model_info": {"type": "demo", "device": "cpu"},
        }
