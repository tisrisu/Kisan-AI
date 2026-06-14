"""
KisanAI — Celery Task for Background Fine-Tuning
"""

import logging
from celery import Celery
from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "kisanai",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=7200,  # 2 hours max for fine-tuning
    worker_prefetch_multiplier=1,
)


@celery_app.task(bind=True, name="finetune_district_model")
def finetune_district_model(self, district_id: int):
    """
    Background task: Fine-tune model for a specific district.
    Triggered when district reaches 50+ verified submissions.
    """
    import sys
    from pathlib import Path

    project_root = str(Path(__file__).parent.parent.parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from ml.finetune import DistrictFineTuner

        self.update_state(state="PROGRESS", meta={"status": "Starting fine-tuning", "district_id": district_id})

        finetuner = DistrictFineTuner(
            base_model_path=str(Path(settings.MODEL_DIR) / "base" / "best_model.pth"),
            output_dir=settings.MODEL_DIR,
            data_dir=str(Path(settings.MODEL_DIR).parent / "data"),
        )

        if not finetuner.check_ready(district_id):
            return {"status": "skipped", "reason": "Not enough submissions", "district_id": district_id}

        self.update_state(state="PROGRESS", meta={"status": "Training in progress", "district_id": district_id})

        metadata = finetuner.fine_tune(
            district_id=district_id,
            num_epochs=20,
            learning_rate=1e-5,
            batch_size=8,
        )

        return {"status": "completed", "district_id": district_id, "metadata": metadata}

    except Exception as e:
        logger.error(f"Fine-tuning failed for district {district_id}: {e}")
        return {"status": "failed", "error": str(e), "district_id": district_id}
