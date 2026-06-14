"""
KisanAI — Per-District Fine-Tuning Pipeline

Auto fine-tunes the base model when a district collects 50+ verified submissions.
Freezes early CNN layers, fine-tunes later layers + classifier with lower LR.
"""

import json
import logging
from pathlib import Path
from typing import Optional

import torch
import torch.optim as optim
from torch.utils.data import DataLoader
from transformers import BertTokenizer

from ml.models.fusion_model import CropDiseaseFusionModel
from ml.train import (
    CropDiseaseDataset,
    FocalLoss,
    Trainer,
    get_train_transforms,
    get_val_transforms,
)

logger = logging.getLogger(__name__)


class DistrictFineTuner:
    """
    Per-district fine-tuning pipeline.

    When a district collects 50+ verified farmer submissions,
    the base model is automatically fine-tuned on local data.
    Even 50-200 local images dramatically improve accuracy because
    the base model already understands leaf disease features — it
    just needs to learn local variations in crop varieties, lighting,
    and disease strains.
    """

    MIN_SUBMISSIONS = 50  # Minimum verified submissions to trigger fine-tuning

    def __init__(self, base_model_path: str = "models/base/best_model.pth",
                 output_dir: str = "models",
                 data_dir: str = "data"):
        self.base_model_path = Path(base_model_path)
        self.output_dir = Path(output_dir)
        self.data_dir = Path(data_dir)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")

    def check_ready(self, district_id: int) -> bool:
        """Check if a district has enough verified submissions for fine-tuning."""
        data_file = self.data_dir / f"district_{district_id}" / "verified_submissions.json"
        if not data_file.exists():
            return False

        with open(data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return len(data) >= self.MIN_SUBMISSIONS

    def fine_tune(self, district_id: int, num_epochs: int = 20,
                  learning_rate: float = 1e-5, batch_size: int = 8) -> dict:
        """
        Fine-tune the base model for a specific district.

        Strategy:
        1. Load base model checkpoint
        2. Freeze early EfficientNet layers (blocks 0-5)
        3. Unfreeze last 2 BERT encoder layers
        4. Use lower learning rate (1e-5 vs 1e-4)
        5. Train for fewer epochs (20 vs 50)
        6. Save as district-specific model
        """
        logger.info(f"Starting fine-tuning for district {district_id}")

        # Load base model
        if not self.base_model_path.exists():
            raise FileNotFoundError(f"Base model not found: {self.base_model_path}")

        checkpoint = torch.load(self.base_model_path, map_location=self.device,
                                weights_only=False)
        base_config = checkpoint.get("config", {})

        model = CropDiseaseFusionModel(
            num_diseases=base_config.get("num_diseases", 38),
            num_districts=base_config.get("num_districts", 100),
            num_seasons=base_config.get("num_seasons", 3),
            num_crops=base_config.get("num_crops", 50),
        )
        model.load_state_dict(checkpoint["model_state_dict"])

        # Fine-tuning strategy: unfreeze specific layers
        # Image branch: unfreeze last 3 EfficientNet blocks
        model.image_branch.unfreeze_last_n_blocks(3)
        # Text branch: unfreeze last 2 BERT layers
        model.text_branch.unfreeze_last_n_layers(2)
        # Context branch: always trainable (small)
        # Fusion layers: always trainable

        model.to(self.device)

        # Dataset
        data_file = self.data_dir / f"district_{district_id}" / "verified_submissions.json"
        image_root = self.data_dir / f"district_{district_id}" / "images"

        dataset = CropDiseaseDataset(
            str(data_file), str(image_root), self.tokenizer,
            transform=get_train_transforms(),
        )

        # Split into train/val (80/20 for small datasets)
        train_size = int(0.8 * len(dataset))
        val_size = len(dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            dataset, [train_size, val_size]
        )

        train_loader = DataLoader(
            train_dataset, batch_size=batch_size, shuffle=True,
            num_workers=2, pin_memory=True,
        )
        val_loader = DataLoader(
            val_dataset, batch_size=batch_size, shuffle=False,
            num_workers=2, pin_memory=True,
        )

        # Training config
        config = {
            **base_config,
            "learning_rate": learning_rate,
            "weight_decay": 1e-5,
            "patience": 5,
            "checkpoint_dir": str(self.output_dir / f"district_{district_id}"),
            "district_id": district_id,
            "fine_tuned_from": str(self.base_model_path),
            "num_training_samples": len(train_dataset),
        }

        # Train
        trainer = Trainer(model, config)
        history = trainer.train(train_loader, val_loader, num_epochs=num_epochs)

        # Save metadata
        metadata = {
            "district_id": district_id,
            "base_model": str(self.base_model_path),
            "num_samples": len(dataset),
            "num_epochs_trained": len(history["train"]),
            "final_val_metrics": history["val"][-1] if history["val"] else {},
            "config": config,
        }

        metadata_path = self.output_dir / f"district_{district_id}" / "metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)

        logger.info(f"Fine-tuning complete for district {district_id}. "
                     f"Model saved to {config['checkpoint_dir']}")

        return metadata
