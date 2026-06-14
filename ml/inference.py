"""
KisanAI — Inference Engine (LoRA ResNet50 Integration)

Handles model loading, preprocessing, and prediction using the
trained ResNet50 + LoRA adapters.
"""

import os
# Fix for OpenMP on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import json
import logging
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import numpy as np
from PIL import Image
from torchvision import transforms, models
from torchvision.models import ResNet50_Weights
from peft import PeftModel

logger = logging.getLogger(__name__)

class InferenceEngine:
    """
    Inference engine using our locally trained ResNet50 + LoRA adapters.
    """

    SEVERITY_LABELS = ["Mild", "Moderate", "Severe"]
    CLASSES = ["Tomato_early_blight", "Tomato_healthy", "Tomato_late_blight"]

    def __init__(self, model_dir: str = "models", disease_names_file: str = "data/knowledge_base/diseases.json",
                 device: Optional[str] = None):
        self.model_dir = Path(model_dir)
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

        # Try loading disease mapping, though we'll primarily use our CLASSES
        self.disease_names = self._load_disease_names(disease_names_file)

        # Image transforms (matching the training script)
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        self._base_model = None
        logger.info(f"InferenceEngine initialized on {self.device}")

    def _load_disease_names(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                diseases = json.load(f)
            return {d["id"]: d for d in diseases}
        except Exception:
            return {}

    def load_model(self, district_id: Optional[int] = None):
        """
        Loads the ResNet50 base model and injects the LoRA adapters from lora_adapters directory.
        """
        if self._base_model is None:
            logger.info("Loading base ResNet50 model...")
            model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
            
            # Replace classifier to match our 3 classes
            model.fc = nn.Linear(model.fc.in_features, len(self.CLASSES))
            
            lora_path = self.model_dir / "lora_adapters"
            if lora_path.exists():
                logger.info(f"Injecting LoRA adapters from {lora_path}")
                model = PeftModel.from_pretrained(model, str(lora_path))
            else:
                logger.warning(f"LoRA adapters not found at {lora_path}! Running untrained head.")
            
            model.to(self.device)
            model.eval()
            self._base_model = model

        return self._base_model

    def preprocess_image(self, image_path: str) -> torch.Tensor:
        image = Image.open(image_path).convert("RGB")
        tensor = self.transform(image)
        return tensor.unsqueeze(0)

    def preprocess_image_from_bytes(self, image_bytes: bytes) -> torch.Tensor:
        import io
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        tensor = self.transform(image)
        return tensor.unsqueeze(0)

    def predict(self, image_path: str, symptom_text: str,
                district_id: int = 0, season_id: int = 0,
                crop_id: int = 0, top_k: int = 3) -> dict:
        
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        return self.predict_from_bytes(image_bytes, symptom_text, district_id, season_id, crop_id, top_k)

    def predict_from_bytes(self, image_bytes: bytes, symptom_text: str,
                           district_id: int = 0, season_id: int = 0,
                           crop_id: int = 0, top_k: int = 3) -> dict:
        
        model = self.load_model(district_id)
        image_tensor = self.preprocess_image_from_bytes(image_bytes).to(self.device)

        with torch.no_grad():
            outputs = model(image_tensor)
            # PEFT models sometimes return a tuple, we just want logits
            if isinstance(outputs, tuple):
                logits = outputs[0]
            elif hasattr(outputs, 'logits'):
                logits = outputs.logits
            else:
                logits = outputs
                
            probs = torch.softmax(logits, dim=1)
            
            # Get top k (limited by our 3 classes)
            k = min(top_k, len(self.CLASSES))
            topk_probs, topk_indices = torch.topk(probs, k, dim=1)

        predictions = []
        for i in range(k):
            idx = topk_indices[0][i].item()
            class_name = self.CLASSES[idx]
            
            predictions.append({
                "rank": i + 1,
                "disease_id": idx, # use our internal ID
                "disease_name": class_name.replace("_", " "),
                "scientific_name": class_name,
                "confidence": round(topk_probs[0][i].item() * 100, 2),
            })

        # Mock severity since our model doesn't predict it
        severity_idx = 1 # Moderate
        severity_probs = [10.0, 80.0, 10.0]

        return {
            "predictions": predictions,
            "primary_diagnosis": predictions[0],
            "severity": {
                "level": self.SEVERITY_LABELS[severity_idx],
                "level_id": severity_idx,
                "confidence": 80.0,
                "distribution": {
                    "Mild": severity_probs[0],
                    "Moderate": severity_probs[1],
                    "Severe": severity_probs[2]
                },
            },
            "model_info": {
                "type": "lora_resnet50",
                "device": str(self.device),
            },
        }
