"""
KisanAI — Training Pipeline

Handles:
- Data loading with augmentation
- Multi-modal dataset (image + text + context)
- Focal loss for class imbalance
- Mixed precision training
- Model checkpointing + early stopping
- Metrics tracking (accuracy, F1, confusion matrix)
"""

import os
import json
import logging
from pathlib import Path
from typing import Optional

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms
from transformers import BertTokenizer
from PIL import Image
import numpy as np
from sklearn.metrics import f1_score, classification_report, confusion_matrix

from ml.models.fusion_model import CropDiseaseFusionModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ────────────────────────────────────────────────────────────────
# Focal Loss — handles class imbalance for rare diseases
# ────────────────────────────────────────────────────────────────

class FocalLoss(nn.Module):
    """
    Focal Loss for addressing class imbalance.
    FL(p_t) = -alpha_t * (1 - p_t)^gamma * log(p_t)
    """

    def __init__(self, alpha: Optional[torch.Tensor] = None, gamma: float = 2.0,
                 reduction: str = "mean"):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, inputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        ce_loss = nn.functional.cross_entropy(inputs, targets, reduction="none",
                                               weight=self.alpha)
        p_t = torch.exp(-nn.functional.cross_entropy(inputs, targets, reduction="none"))
        focal_loss = ((1 - p_t) ** self.gamma) * ce_loss

        if self.reduction == "mean":
            return focal_loss.mean()
        elif self.reduction == "sum":
            return focal_loss.sum()
        return focal_loss


# ────────────────────────────────────────────────────────────────
# Dataset
# ────────────────────────────────────────────────────────────────

class CropDiseaseDataset(Dataset):
    """
    Multi-modal dataset for crop disease diagnosis.

    Expected data format (JSON):
    {
        "image_path": "path/to/leaf.jpg",
        "disease_label": 0,
        "severity_label": 1,  # 0=mild, 1=moderate, 2=severe
        "symptom_text": "Patti pe bhure daag dikh rahe",
        "district_id": 5,
        "season_id": 0,  # 0=kharif, 1=rabi, 2=zaid
        "crop_id": 3
    }
    """

    def __init__(self, data_file: str, image_root: str, tokenizer: BertTokenizer,
                 transform=None, max_text_len: int = 128):
        with open(data_file, "r", encoding="utf-8") as f:
            self.data = json.load(f)

        self.image_root = Path(image_root)
        self.tokenizer = tokenizer
        self.transform = transform
        self.max_text_len = max_text_len

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Image
        img_path = self.image_root / item["image_path"]
        image = Image.open(img_path).convert("RGB")
        if self.transform:
            image = self.transform(image)

        # Text
        symptom_text = item.get("symptom_text", "")
        if not symptom_text:
            symptom_text = "no symptoms described"
        encoding = self.tokenizer(
            symptom_text,
            max_length=self.max_text_len,
            padding="max_length",
            truncation=True,
            return_tensors="pt",
        )

        # Context
        district_id = torch.tensor(item.get("district_id", 0), dtype=torch.long)
        season_id = torch.tensor(item.get("season_id", 0), dtype=torch.long)
        crop_id = torch.tensor(item.get("crop_id", 0), dtype=torch.long)

        # Labels
        disease_label = torch.tensor(item["disease_label"], dtype=torch.long)
        severity_label = torch.tensor(item.get("severity_label", 1), dtype=torch.long)

        return {
            "image": image,
            "input_ids": encoding["input_ids"].squeeze(0),
            "attention_mask": encoding["attention_mask"].squeeze(0),
            "district_id": district_id,
            "season_id": season_id,
            "crop_id": crop_id,
            "disease_label": disease_label,
            "severity_label": severity_label,
        }

    def get_class_weights(self):
        """Compute class weights for oversampling rare diseases."""
        labels = [item["disease_label"] for item in self.data]
        class_counts = np.bincount(labels)
        weights = 1.0 / class_counts
        sample_weights = [weights[label] for label in labels]
        return sample_weights


# ────────────────────────────────────────────────────────────────
# Data Augmentation
# ────────────────────────────────────────────────────────────────

def get_train_transforms():
    """Training augmentation: rotation, flip, brightness jitter, noise."""
    return transforms.Compose([
        transforms.Resize((380, 380)),
        transforms.RandomRotation(30),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.2, hue=0.1),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


def get_val_transforms():
    """Validation/test transforms: only resize + normalize."""
    return transforms.Compose([
        transforms.Resize((380, 380)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])


# ────────────────────────────────────────────────────────────────
# Trainer
# ────────────────────────────────────────────────────────────────

class Trainer:
    """
    Multi-modal training pipeline with:
    - Focal loss for class imbalance
    - Mixed precision training (AMP)
    - Early stopping
    - Model checkpointing
    - Comprehensive metrics
    """

    def __init__(self, model: CropDiseaseFusionModel, config: dict):
        self.model = model
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

        # Loss functions
        self.disease_criterion = FocalLoss(gamma=2.0)
        self.severity_criterion = nn.CrossEntropyLoss()

        # Optimizer
        self.optimizer = optim.AdamW(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=config.get("learning_rate", 1e-4),
            weight_decay=config.get("weight_decay", 1e-5),
        )

        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
            self.optimizer,
            T_0=config.get("scheduler_T0", 10),
            T_mult=2,
        )

        # Mixed precision
        self.scaler = torch.amp.GradScaler("cuda") if self.device.type == "cuda" else None
        self.use_amp = self.device.type == "cuda"

        # Early stopping
        self.best_val_loss = float("inf")
        self.patience_counter = 0
        self.patience = config.get("patience", 10)

        # Checkpointing
        self.checkpoint_dir = Path(config.get("checkpoint_dir", "models/base"))
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Loss weighting
        self.disease_weight = config.get("disease_loss_weight", 0.7)
        self.severity_weight = config.get("severity_loss_weight", 0.3)

    def train_epoch(self, dataloader: DataLoader) -> dict:
        """Train for one epoch."""
        self.model.train()
        total_loss = 0
        disease_correct = 0
        severity_correct = 0
        total_samples = 0

        for batch in dataloader:
            # Move to device
            image = batch["image"].to(self.device)
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            district_id = batch["district_id"].to(self.device)
            season_id = batch["season_id"].to(self.device)
            crop_id = batch["crop_id"].to(self.device)
            disease_label = batch["disease_label"].to(self.device)
            severity_label = batch["severity_label"].to(self.device)

            self.optimizer.zero_grad()

            if self.use_amp:
                with torch.amp.autocast("cuda"):
                    disease_logits, severity_logits = self.model(
                        image, input_ids, attention_mask, district_id, season_id, crop_id
                    )
                    disease_loss = self.disease_criterion(disease_logits, disease_label)
                    severity_loss = self.severity_criterion(severity_logits, severity_label)
                    loss = (self.disease_weight * disease_loss +
                            self.severity_weight * severity_loss)

                self.scaler.scale(loss).backward()
                self.scaler.unscale_(self.optimizer)
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.scaler.step(self.optimizer)
                self.scaler.update()
            else:
                disease_logits, severity_logits = self.model(
                    image, input_ids, attention_mask, district_id, season_id, crop_id
                )
                disease_loss = self.disease_criterion(disease_logits, disease_label)
                severity_loss = self.severity_criterion(severity_logits, severity_label)
                loss = (self.disease_weight * disease_loss +
                        self.severity_weight * severity_loss)

                loss.backward()
                torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                self.optimizer.step()

            total_loss += loss.item() * image.size(0)
            disease_correct += (disease_logits.argmax(1) == disease_label).sum().item()
            severity_correct += (severity_logits.argmax(1) == severity_label).sum().item()
            total_samples += image.size(0)

        self.scheduler.step()

        return {
            "loss": total_loss / total_samples,
            "disease_acc": disease_correct / total_samples,
            "severity_acc": severity_correct / total_samples,
        }

    @torch.no_grad()
    def validate(self, dataloader: DataLoader) -> dict:
        """Validate the model."""
        self.model.eval()
        total_loss = 0
        all_disease_preds = []
        all_disease_labels = []
        all_severity_preds = []
        all_severity_labels = []
        total_samples = 0

        for batch in dataloader:
            image = batch["image"].to(self.device)
            input_ids = batch["input_ids"].to(self.device)
            attention_mask = batch["attention_mask"].to(self.device)
            district_id = batch["district_id"].to(self.device)
            season_id = batch["season_id"].to(self.device)
            crop_id = batch["crop_id"].to(self.device)
            disease_label = batch["disease_label"].to(self.device)
            severity_label = batch["severity_label"].to(self.device)

            disease_logits, severity_logits = self.model(
                image, input_ids, attention_mask, district_id, season_id, crop_id
            )
            disease_loss = self.disease_criterion(disease_logits, disease_label)
            severity_loss = self.severity_criterion(severity_logits, severity_label)
            loss = (self.disease_weight * disease_loss +
                    self.severity_weight * severity_loss)

            total_loss += loss.item() * image.size(0)
            total_samples += image.size(0)

            all_disease_preds.extend(disease_logits.argmax(1).cpu().numpy())
            all_disease_labels.extend(disease_label.cpu().numpy())
            all_severity_preds.extend(severity_logits.argmax(1).cpu().numpy())
            all_severity_labels.extend(severity_label.cpu().numpy())

        disease_f1 = f1_score(all_disease_labels, all_disease_preds, average="macro",
                              zero_division=0)
        severity_f1 = f1_score(all_severity_labels, all_severity_preds, average="macro",
                               zero_division=0)

        return {
            "loss": total_loss / total_samples,
            "disease_acc": np.mean(np.array(all_disease_preds) == np.array(all_disease_labels)),
            "severity_acc": np.mean(np.array(all_severity_preds) == np.array(all_severity_labels)),
            "disease_f1": disease_f1,
            "severity_f1": severity_f1,
        }

    def train(self, train_loader: DataLoader, val_loader: DataLoader,
              num_epochs: int = 50) -> dict:
        """Full training loop with early stopping and checkpointing."""
        history = {"train": [], "val": []}

        logger.info(f"Training on {self.device} for {num_epochs} epochs")
        logger.info(f"Model parameters: {sum(p.numel() for p in self.model.parameters()):,}")
        logger.info(f"Trainable parameters: {sum(p.numel() for p in self.model.parameters() if p.requires_grad):,}")

        for epoch in range(num_epochs):
            train_metrics = self.train_epoch(train_loader)
            val_metrics = self.validate(val_loader)

            history["train"].append(train_metrics)
            history["val"].append(val_metrics)

            logger.info(
                f"Epoch {epoch + 1}/{num_epochs} | "
                f"Train Loss: {train_metrics['loss']:.4f} | "
                f"Val Loss: {val_metrics['loss']:.4f} | "
                f"Val Disease Acc: {val_metrics['disease_acc']:.4f} | "
                f"Val Disease F1: {val_metrics['disease_f1']:.4f}"
            )

            # Checkpointing
            if val_metrics["loss"] < self.best_val_loss:
                self.best_val_loss = val_metrics["loss"]
                self.patience_counter = 0
                self.save_checkpoint(epoch, val_metrics, is_best=True)
                logger.info(f"  ✓ New best model saved (val_loss: {val_metrics['loss']:.4f})")
            else:
                self.patience_counter += 1

            # Early stopping
            if self.patience_counter >= self.patience:
                logger.info(f"Early stopping at epoch {epoch + 1}")
                break

        return history

    def save_checkpoint(self, epoch: int, metrics: dict, is_best: bool = False):
        """Save model checkpoint."""
        checkpoint = {
            "epoch": epoch,
            "model_state_dict": self.model.state_dict(),
            "optimizer_state_dict": self.optimizer.state_dict(),
            "scheduler_state_dict": self.scheduler.state_dict(),
            "metrics": metrics,
            "config": self.config,
        }

        filename = "best_model.pth" if is_best else f"checkpoint_epoch_{epoch}.pth"
        path = self.checkpoint_dir / filename
        torch.save(checkpoint, path)

    def load_checkpoint(self, path: str):
        """Load model from checkpoint."""
        checkpoint = torch.load(path, map_location=self.device, weights_only=False)
        self.model.load_state_dict(checkpoint["model_state_dict"])
        self.optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        if "scheduler_state_dict" in checkpoint:
            self.scheduler.load_state_dict(checkpoint["scheduler_state_dict"])
        logger.info(f"Loaded checkpoint from {path} (epoch {checkpoint['epoch']})")
        return checkpoint


# ────────────────────────────────────────────────────────────────
# Entry Point
# ────────────────────────────────────────────────────────────────

def main():
    """Main training entry point."""
    config = {
        "data_dir": "data",
        "train_file": "data/train.json",
        "val_file": "data/val.json",
        "image_root": "data/images",
        "num_diseases": 38,
        "num_districts": 100,
        "num_seasons": 3,
        "num_crops": 50,
        "batch_size": 16,
        "num_epochs": 50,
        "learning_rate": 1e-4,
        "weight_decay": 1e-5,
        "patience": 10,
        "checkpoint_dir": "models/base",
        "disease_loss_weight": 0.7,
        "severity_loss_weight": 0.3,
    }

    # Tokenizer
    tokenizer = BertTokenizer.from_pretrained("bert-base-multilingual-cased")

    # Datasets
    train_dataset = CropDiseaseDataset(
        config["train_file"], config["image_root"], tokenizer,
        transform=get_train_transforms(),
    )
    val_dataset = CropDiseaseDataset(
        config["val_file"], config["image_root"], tokenizer,
        transform=get_val_transforms(),
    )

    # Weighted sampler for class imbalance
    sample_weights = train_dataset.get_class_weights()
    sampler = WeightedRandomSampler(sample_weights, len(sample_weights))

    train_loader = DataLoader(
        train_dataset, batch_size=config["batch_size"],
        sampler=sampler, num_workers=4, pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset, batch_size=config["batch_size"],
        shuffle=False, num_workers=4, pin_memory=True,
    )

    # Model
    model = CropDiseaseFusionModel(
        num_diseases=config["num_diseases"],
        num_districts=config["num_districts"],
        num_seasons=config["num_seasons"],
        num_crops=config["num_crops"],
    )

    # Train
    trainer = Trainer(model, config)
    history = trainer.train(train_loader, val_loader, config["num_epochs"])

    # Save training history
    with open(Path(config["checkpoint_dir"]) / "training_history.json", "w") as f:
        json.dump({k: [{kk: float(vv) for kk, vv in d.items()} for d in v]
                   for k, v in history.items()}, f, indent=2)

    logger.info("Training complete!")


if __name__ == "__main__":
    main()
