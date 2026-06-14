import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from ml.inference import InferenceEngine

engine = InferenceEngine(model_dir="models")

# Create a dummy image
from PIL import Image
img = Image.new('RGB', (224, 224), color=(0, 255, 0))
img.save("test_leaf.jpg")

with open("test_leaf.jpg", "rb") as f:
    img_bytes = f.read()

result = engine.predict_from_bytes(img_bytes, symptom_text="Yellow leaves")
print("Prediction Result:")
import json
print(json.dumps(result, indent=2))
