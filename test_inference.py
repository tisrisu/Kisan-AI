"""
KisanAI — Quick inference smoke-test.

Run from the project root:
    python test_inference.py

Expects:
    models/base/best_model.pth   (or runs in demo / random-weight mode)
    data/knowledge_base/diseases.json

The engine uses all three modalities:
  • image_bytes   — leaf photo (green dummy image here)
  • symptom_text  — vernacular description (Hindi example)
  • district_id, season_id, crop_id — contextual metadata
"""

import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from PIL import Image
import io

from ml.inference import InferenceEngine

# ── Initialise engine ──────────────────────────────────────────
engine = InferenceEngine(
    model_dir="models",
    disease_names_file="data/knowledge_base/diseases.json",
)

# ── Create a dummy 380×380 green leaf image ────────────────────
buf = io.BytesIO()
Image.new("RGB", (380, 380), color=(34, 139, 34)).save(buf, format="JPEG")
img_bytes = buf.getvalue()

# Also save to disk for visual inspection
with open("test_leaf.jpg", "wb") as f:
    f.write(img_bytes)

# ── Run full multi-modal prediction ───────────────────────────
result = engine.predict_from_bytes(
    image_bytes=img_bytes,
    symptom_text="Patti pe bhure aur peele daag dikh rahe hain",  # Hindi: "Brown and yellow spots visible on leaves"
    district_id=5,    # e.g. Vaishali, Bihar
    season_id=0,      # 0 = kharif
    crop_id=3,        # e.g. Rice
    top_k=3,
)

print("\n=== KisanAI Prediction Result ===")
print(json.dumps(result, indent=2))
print("\nModel type :", result["model_info"]["type"])
print("Device     :", result["model_info"]["device"])
print("Top disease:", result["primary_diagnosis"]["disease_name"],
      f"({result['primary_diagnosis']['confidence']}%)")
print("Severity   :", result["severity"]["level"],
      f"({result['severity']['confidence']}%)")
