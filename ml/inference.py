"""
KisanAI — Inference Engine (Multi-Modal Fusion)

Loads the trained CropDiseaseFusionModel
  Image branch  : EfficientNet-B4  → 1792-dim
  Text branch   : mBERT            →  256-dim
  Context branch: District/Season/Crop embeddings → 64-dim
  Fusion        : 2112 → 512 → 256 → Disease + Severity heads

Per-district LoRA adapters are injected from models/lora_adapters/<district_id>/
when available, falling back to the base model otherwise.
"""

import io
import os
import json
import logging
from pathlib import Path
from typing import Optional

# Fix for OpenMP on Windows
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn
from PIL import Image
from torchvision import transforms
from transformers import BertTokenizer

logger = logging.getLogger(__name__)

SEVERITY_LABELS = ["Mild", "Moderate", "Severe"]


class InferenceEngine:
    """
    Multi-modal inference engine for KisanAI.

    Supports:
      • Base model inference (no LoRA)
      • Per-district LoRA adapter injection (models/lora_adapters/<district_id>/)
    """

    def __init__(
        self,
        model_dir: str = "models",
        disease_names_file: str = "data/knowledge_base/diseases.json",
        device: Optional[str] = None,
        num_diseases: int = 38,
        num_districts: int = 100,
        num_seasons: int = 3,
        num_crops: int = 50,
    ):
        self.model_dir = Path(model_dir)
        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))
        self.num_diseases = num_diseases
        self.num_districts = num_districts
        self.num_seasons = num_seasons
        self.num_crops = num_crops

        # Disease name/info lookup
        self.disease_names = self._load_disease_names(disease_names_file)

        # Image transforms — match training val transforms (380×380, no augmentation)
        self.image_transform = transforms.Compose([
            transforms.Resize((380, 380)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        # Multilingual BERT tokenizer (supports EN/HI/TA/TE)
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")
        self.max_text_len = 128

        # Base model — lazy-loaded on first predict call
        self._base_model: Optional[nn.Module] = None

        logger.info(f"InferenceEngine initialised on {self.device}")

    # ──────────────────────────────────────────────────────────────
    # Internal helpers
    # ──────────────────────────────────────────────────────────────

    def _load_disease_names(self, path: str) -> dict:
        try:
            with open(path, "r", encoding="utf-8") as f:
                diseases = json.load(f)
            return {d["id"]: d for d in diseases}
        except Exception:
            return {}

    def _load_base_model(self) -> nn.Module:
        """Load CropDiseaseFusionModel from checkpoint (or random weights in demo mode)."""
        from ml.models.fusion_model import CropDiseaseFusionModel

        model = CropDiseaseFusionModel(
            num_diseases=self.num_diseases,
            num_districts=self.num_districts,
            num_seasons=self.num_seasons,
            num_crops=self.num_crops,
        )

        checkpoint_path = self.model_dir / "base" / "best_model.pth"
        if checkpoint_path.exists():
            logger.info(f"Loading checkpoint: {checkpoint_path}")
            checkpoint = torch.load(checkpoint_path, map_location=self.device, weights_only=False)
            state_dict = checkpoint.get("model_state_dict", checkpoint)
            model.load_state_dict(state_dict, strict=False)
            logger.info("Checkpoint loaded ✓")
        else:
            logger.warning(
                f"No checkpoint at {checkpoint_path}. "
                "Running in demo mode with random weights."
            )

        model.to(self.device).eval()
        return model

    def load_model(self, district_id: Optional[int] = None) -> nn.Module:
        """
        Return the model for inference.

        If a per-district LoRA adapter exists at
        models/lora_adapters/<district_id>/ it is injected on top of the
        base model; otherwise the base model is returned as-is.
        """
        # Lazy-load base model
        if self._base_model is None:
            self._base_model = self._load_base_model()

        # Inject per-district LoRA adapter if available
        if district_id is not None:
            adapter_dir = self.model_dir / "lora_adapters" / str(district_id)
            if adapter_dir.exists():
                try:
                    from peft import PeftModel
                    logger.info(f"Injecting LoRA adapter for district {district_id}")
                    return PeftModel.from_pretrained(self._base_model, str(adapter_dir))
                except Exception as e:
                    logger.warning(f"LoRA adapter load failed ({e}), using base model")

        return self._base_model

    def _preprocess_image(self, image_bytes: bytes) -> torch.Tensor:
        """Decode image bytes → normalised (1, 3, 380, 380) tensor."""
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        return self.image_transform(image).unsqueeze(0)

    def _tokenize_text(self, symptom_text: str) -> tuple[torch.Tensor, torch.Tensor]:
        """Tokenise symptom text with mBERT tokeniser."""
        text = symptom_text.strip() or "no symptoms described"
        enc = self.tokenizer(
            text,
            max_length=self.max_text_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )
        return enc["input_ids"], enc["attention_mask"]

    # ──────────────────────────────────────────────────────────────
    # Public prediction API
    # ──────────────────────────────────────────────────────────────

    def predict_from_bytes(
        self,
        image_bytes: bytes,
        symptom_text: str = "",
        district_id: int = 0,
        season_id: int = 0,
        crop_id: int = 0,
        top_k: int = 3,
    ) -> dict:
        """
        Run full multi-modal inference.

        Args:
            image_bytes:  Raw bytes of the leaf photo (JPG/PNG).
            symptom_text: Symptom description — any supported language
                          (English, Hindi, Tamil, Telugu).
            district_id:  District index (0 – num_districts-1).
            season_id:    0 = kharif, 1 = rabi, 2 = zaid.
            crop_id:      Crop variety index (0 – num_crops-1).
            top_k:        Number of ranked predictions to return.

        Returns:
            dict with: predictions, primary_diagnosis, severity, model_info
        """
        model = self.load_model(district_id)

        image_t = self._preprocess_image(image_bytes).to(self.device)
        input_ids, attn_mask = self._tokenize_text(symptom_text)
        input_ids = input_ids.to(self.device)
        attn_mask = attn_mask.to(self.device)

        district_t = torch.tensor([district_id], dtype=torch.long, device=self.device)
        season_t   = torch.tensor([season_id],   dtype=torch.long, device=self.device)
        crop_t     = torch.tensor([crop_id],     dtype=torch.long, device=self.device)

        with torch.no_grad():
            disease_logits, severity_logits = model(
                image_t, input_ids, attn_mask, district_t, season_t, crop_t
            )
            disease_probs  = torch.softmax(disease_logits,  dim=1)
            severity_probs = torch.softmax(severity_logits, dim=1)

        # Top-k disease predictions
        k = min(top_k, self.num_diseases)
        topk_probs, topk_idx = torch.topk(disease_probs, k, dim=1)

        predictions = []
        for i in range(k):
            idx = topk_idx[0][i].item()
            info = self.disease_names.get(idx, {})
            predictions.append({
                "rank": i + 1,
                "disease_id": idx,
                "disease_name": info.get("name", f"Disease_{idx}"),
                "scientific_name": info.get("scientific_name", ""),
                "confidence": round(topk_probs[0][i].item() * 100, 2),
            })

        # Severity
        sev_idx = severity_probs.argmax(dim=1).item()
        sev_dist = {
            SEVERITY_LABELS[i]: round(severity_probs[0][i].item() * 100, 2)
            for i in range(3)
        }

        # Detect whether a per-district adapter was used
        adapter_path = self.model_dir / "lora_adapters" / str(district_id)
        model_type = "fusion_district_lora" if adapter_path.exists() else "fusion_base"

        return {
            "predictions": predictions,
            "primary_diagnosis": predictions[0],
            "severity": {
                "level": SEVERITY_LABELS[sev_idx],
                "level_id": sev_idx,
                "confidence": round(severity_probs[0][sev_idx].item() * 100, 2),
                "distribution": sev_dist,
            },
            "model_info": {
                "type": model_type,
                "device": str(self.device),
                "district_id": district_id,
            },
        }

    def predict(
        self,
        image_path: str,
        symptom_text: str = "",
        district_id: int = 0,
        season_id: int = 0,
        crop_id: int = 0,
        top_k: int = 3,
    ) -> dict:
        """Convenience wrapper that reads image from a file path."""
        with open(image_path, "rb") as f:
            image_bytes = f.read()
        return self.predict_from_bytes(
            image_bytes, symptom_text, district_id, season_id, crop_id, top_k
        )
