"""
KisanAI — Multi-Modal Fusion Architecture for Crop Disease Diagnosis

Image Branch: EfficientNet-B4 (ImageNet pretrained) → 1792-dim embedding
Text Branch: Multilingual BERT → 256-dim embedding  
Context Branch: Categorical embeddings → 64-dim embedding
Fusion: Concatenation → Dense layers → Disease + Severity heads
"""

import torch
import torch.nn as nn
from torchvision import models
from transformers import BertModel, BertTokenizer


class ImageBranch(nn.Module):
    """
    Image Branch using EfficientNet-B4 pretrained on ImageNet.
    Input: 380×380×3 normalized leaf photo
    Output: 1792-dim image embedding
    """

    def __init__(self, freeze_layers: bool = True):
        super().__init__()
        # Load EfficientNet-B4 pretrained
        self.efficientnet = models.efficientnet_b4(weights=models.EfficientNet_B4_Weights.IMAGENET1K_V1)

        # Remove the classifier head
        self.features = self.efficientnet.features
        self.avgpool = nn.AdaptiveAvgPool2d(1)

        # Freeze early layers for transfer learning
        if freeze_layers:
            for i, layer in enumerate(self.features):
                if i < 5:  # Freeze first 5 blocks
                    for param in layer.parameters():
                        param.requires_grad = False

        self.output_dim = 1792  # EfficientNet-B4 feature dimension

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Args:
            x: Tensor of shape (batch_size, 3, 380, 380)
        Returns:
            Tensor of shape (batch_size, 1792)
        """
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1)
        return x

    def unfreeze_all(self):
        """Unfreeze all layers for full fine-tuning."""
        for param in self.features.parameters():
            param.requires_grad = True

    def unfreeze_last_n_blocks(self, n: int = 3):
        """Unfreeze last n blocks for gradual fine-tuning."""
        total_blocks = len(self.features)
        for i, layer in enumerate(self.features):
            if i >= total_blocks - n:
                for param in layer.parameters():
                    param.requires_grad = True


class TextBranch(nn.Module):
    """
    Text Branch using Multilingual BERT for vernacular symptom descriptions.
    Supports: English, Hindi, Tamil, Telugu
    Input: Tokenized symptom text
    Output: 256-dim text embedding
    """

    def __init__(self, model_name: str = "bert-base-multilingual-cased", freeze_bert: bool = True):
        super().__init__()
        self.bert = BertModel.from_pretrained(model_name)
        self.projection = nn.Sequential(
            nn.Linear(768, 512),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(512, 256),
        )

        # Freeze BERT layers for transfer learning
        if freeze_bert:
            for param in self.bert.parameters():
                param.requires_grad = False

        self.output_dim = 256

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        """
        Args:
            input_ids: Tensor of shape (batch_size, max_seq_len)
            attention_mask: Tensor of shape (batch_size, max_seq_len)
        Returns:
            Tensor of shape (batch_size, 256)
        """
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        # Use [CLS] token embedding as sentence representation
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        text_embedding = self.projection(cls_embedding)
        return text_embedding

    def unfreeze_last_n_layers(self, n: int = 2):
        """Unfreeze last n BERT encoder layers for fine-tuning."""
        total_layers = len(self.bert.encoder.layer)
        for i, layer in enumerate(self.bert.encoder.layer):
            if i >= total_layers - n:
                for param in layer.parameters():
                    param.requires_grad = True


class ContextBranch(nn.Module):
    """
    Context Branch for categorical metadata.
    Input: District ID, Season ID, Crop ID
    Output: 64-dim context embedding
    """

    def __init__(self, num_districts: int = 100, num_seasons: int = 3, num_crops: int = 50):
        super().__init__()

        self.district_embedding = nn.Embedding(num_districts, 32)
        self.season_embedding = nn.Embedding(num_seasons, 16)
        self.crop_embedding = nn.Embedding(num_crops, 16)

        self.output_dim = 64  # 32 + 16 + 16

    def forward(self, district_id: torch.Tensor, season_id: torch.Tensor,
                crop_id: torch.Tensor) -> torch.Tensor:
        """
        Args:
            district_id: Tensor of shape (batch_size,)
            season_id: Tensor of shape (batch_size,)
            crop_id: Tensor of shape (batch_size,)
        Returns:
            Tensor of shape (batch_size, 64)
        """
        d_emb = self.district_embedding(district_id)
        s_emb = self.season_embedding(season_id)
        c_emb = self.crop_embedding(crop_id)
        return torch.cat([d_emb, s_emb, c_emb], dim=1)


class CropDiseaseFusionModel(nn.Module):
    """
    Multi-Modal Fusion Model for Crop Disease Diagnosis.

    Architecture:
        Image (1792) + Text (256) + Context (64) = 2112-dim
        → Dense(512, ReLU) + BatchNorm + Dropout(0.3)
        → Dense(256, ReLU) + BatchNorm + Dropout(0.2)
        → Disease Classification head (softmax)
        → Severity Grading head (3-class softmax)
    """

    def __init__(self, num_diseases: int = 38, num_districts: int = 100,
                 num_seasons: int = 3, num_crops: int = 50):
        super().__init__()

        # Three branches
        self.image_branch = ImageBranch(freeze_layers=True)
        self.text_branch = TextBranch(freeze_bert=True)
        self.context_branch = ContextBranch(num_districts, num_seasons, num_crops)

        # Combined dimension
        combined_dim = (
            self.image_branch.output_dim +
            self.text_branch.output_dim +
            self.context_branch.output_dim
        )  # 1792 + 256 + 64 = 2112

        # Fusion layers
        self.fusion = nn.Sequential(
            nn.Linear(combined_dim, 512),
            nn.ReLU(),
            nn.BatchNorm1d(512),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.BatchNorm1d(256),
            nn.Dropout(0.2),
        )

        # Output heads
        self.disease_head = nn.Linear(256, num_diseases)
        self.severity_head = nn.Linear(256, 3)  # Mild, Moderate, Severe

        self.num_diseases = num_diseases

    def forward(self, image: torch.Tensor, input_ids: torch.Tensor,
                attention_mask: torch.Tensor, district_id: torch.Tensor,
                season_id: torch.Tensor, crop_id: torch.Tensor):
        """
        Full forward pass through all branches + fusion.

        Returns:
            disease_logits: (batch_size, num_diseases)
            severity_logits: (batch_size, 3)
        """
        # Branch outputs
        img_emb = self.image_branch(image)
        txt_emb = self.text_branch(input_ids, attention_mask)
        ctx_emb = self.context_branch(district_id, season_id, crop_id)

        # Concatenate
        combined = torch.cat([img_emb, txt_emb, ctx_emb], dim=1)

        # Fusion
        fused = self.fusion(combined)

        # Output heads
        disease_logits = self.disease_head(fused)
        severity_logits = self.severity_head(fused)

        return disease_logits, severity_logits

    def predict(self, image, input_ids, attention_mask, district_id, season_id, crop_id):
        """Inference mode: returns probabilities and predicted classes."""
        self.eval()
        with torch.no_grad():
            disease_logits, severity_logits = self.forward(
                image, input_ids, attention_mask, district_id, season_id, crop_id
            )
            disease_probs = torch.softmax(disease_logits, dim=1)
            severity_probs = torch.softmax(severity_logits, dim=1)

            disease_pred = torch.argmax(disease_probs, dim=1)
            severity_pred = torch.argmax(severity_probs, dim=1)

            disease_confidence = disease_probs.max(dim=1).values

        return {
            "disease_pred": disease_pred,
            "disease_probs": disease_probs,
            "disease_confidence": disease_confidence,
            "severity_pred": severity_pred,
            "severity_probs": severity_probs,
        }

    def get_top_k_diseases(self, disease_probs: torch.Tensor, k: int = 3):
        """Get top-k disease predictions with probabilities."""
        topk_probs, topk_indices = torch.topk(disease_probs, k, dim=1)
        return topk_indices, topk_probs
