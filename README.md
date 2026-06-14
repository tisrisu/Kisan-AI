# 🌿 KisanAI — Hyper-Local Crop Disease Diagnosis

> AI-powered crop disease detection for Indian farmers.  
> Multi-modal fusion (leaf photo + symptom text + district context) with per-district LoRA fine-tuning.

---

## Architecture

```
Leaf Photo (380×380)   ──► EfficientNet-B4  → 1792-dim embedding ─┐
Symptom Text (HI/TA/TE/EN) ──► mBERT        →  256-dim embedding ─┤─► Fusion → Disease + Severity
District / Season / Crop ──► Embeddings     →   64-dim embedding ─┘
```

**Two output heads:**
- Disease classification (38 classes)
- Severity grading (Mild / Moderate / Severe)

**Per-district adaptation:**  
When a district collects 50+ verified submissions, LoRA adapters are auto-trained on local data and injected at inference time — without retraining the full model.

---

## Repo Structure

```
Kisan-AI/
├── backend/          FastAPI app (API + DB + services)
│   ├── app/
│   │   ├── api/routes/   diagnosis.py, feedback.py, history.py
│   │   ├── db/           SQLAlchemy models + seed
│   │   ├── services/     ml_service.py (orchestrates inference)
│   │   └── main.py
│   └── requirements.txt
├── frontend/         Next.js 15 app (App Router, Tailwind v4)
│   └── src/app/      page.js, diagnose/, results/, dashboard/
├── ml/               Model definitions, training, inference
│   ├── models/       fusion_model.py (EfficientNet-B4 + mBERT)
│   ├── inference.py  InferenceEngine (loads base + LoRA adapters)
│   ├── train.py      Full training pipeline with Focal Loss + AMP
│   └── finetune.py   Per-district fine-tuning
├── models/
│   ├── base/         best_model.pth (trained checkpoint — git-ignored)
│   └── lora_adapters/  Per-district LoRA adapters
│       └── adapter_config.json
├── data/
│   ├── knowledge_base/  diseases.json, medications.json, districts.json
│   └── uploads/         Farmer-submitted images (git-ignored)
├── docker-compose.yml
├── .env.example
└── test_inference.py
```

---

## Quick Start

### Local development (no Docker)

```bash
# 1. Clone
git clone https://github.com/tisrisu/Kisan-AI.git
cd Kisan-AI

# 2. Backend
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt          # heavy — skip for demo mode
cd backend && uvicorn app.main:app --reload --port 8000

# 3. Frontend (new terminal)
cd frontend && npm install && npm run dev   # → http://localhost:3000

# 4. Smoke-test inference
python test_inference.py
```

### Docker (full stack)

```bash
cp .env.example .env          # fill in passwords
docker-compose up --build     # backend :8000, frontend :3000
```

---

## Training

```bash
# 1. Prepare dataset JSON (see ml/train.py for format)
# 2. Run training
python -m ml.train

# Output: models/base/best_model.pth
```

### Per-district fine-tuning

```bash
# Triggered automatically by the backend when a district
# reaches MIN_SUBMISSIONS_FOR_FINETUNE (default: 50).
# Manual trigger:
python -m ml.finetune --district_id 5
```

---

## API Reference

Interactive docs at **http://localhost:8000/docs**

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/diagnose` | Upload leaf photo → get diagnosis |
| `POST` | `/api/v1/feedback` | Submit farmer feedback on diagnosis |
| `GET`  | `/api/v1/history`  | Fetch past diagnoses |

**Diagnose request (multipart/form-data):**
```
image          : file     (JPG/PNG, max 10 MB)
symptom_text   : string   e.g. "Patti pe bhure daag" (any language)
district_id    : int      (0–99)
season         : string   kharif | rabi | zaid
crop_variety_id: int
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| ML    | PyTorch · EfficientNet-B4 · mBERT · PEFT/LoRA |
| API   | FastAPI · SQLAlchemy (async) · SQLite / PostgreSQL |
| UI    | Next.js 15 · React 19 · Tailwind CSS v4 |
| Infra | Docker Compose · PostgreSQL · Redis · MinIO |

---

## Contributing

1. Fork → feature branch → PR
2. `python test_inference.py` must pass before pushing
3. Run `cd frontend && npm run lint` for frontend changes

---

## License

MIT — see [LICENSE](LICENSE)
