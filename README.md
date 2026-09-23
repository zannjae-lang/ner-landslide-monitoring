# AI-Based Early Warning & Landslide Risk Monitoring System in NER
**SIH 2026 | Problem Statement ID: 26001**  
**Ministry of Development of North Eastern Region (MDoNER)**

A full-stack, modular, evidence-driven disaster intelligence and risk monitoring platform for all eight North Eastern Region (NER) states of India:
1. Arunachal Pradesh
2. Assam
3. Manipur
4. Meghalaya
5. Mizoram
6. Nagaland
7. Sikkim
8. Tripura

---

## 📖 Comprehensive Judge & Evaluation Guide
For competition evaluators, technical judges, and disaster management officials, see the [Competition Evaluation Guide](file:///docs/COMPETITION_EVALUATION_GUIDE.md) for architecture breakdowns, live demo scripts, and remote sensing transparency details.

---

## 🏛️ System Architecture Overview

- **Model 1 (Static Susceptibility):** XGBoost pipeline evaluating 13 terrain, morphometric, and land-use features (`elevation`, `slope`, `curvature`, `tpi`, `tri`, `aspect_sin`, `aspect_cos`, `ndvi_p90`, `ndvi_p50`, `ndvi_p10`, `distance_to_road_m`, `distance_to_drainage_m`, `lulc_type`). Threshold: `0.39`.
- **Model 2 (Dynamic Early Warning):** XGBoost pipeline evaluating 10 dynamic environmental variables (7 rainfall windows: `1h`, `3h`, `6h`, `12h`, `24h`, `3d`, `7d`, `susceptibility_probability`, and 2 subsurface soil moisture layers). Threshold: `0.10`.
- **Risk Engine 2.0:** Multi-factor baseline fusion engine:
  $$\text{Score} = \text{clip}\left(0.45 \times P_{\text{susc}} + 0.55 \times P_{\text{dyn}} + \Delta_{\text{rainfall}}, 0.0, 1.0\right)$$
  Bands: Normal ($<0.25$), Watch ($\ge 0.25$), Alert ($\ge 0.50$), Critical ($\ge 0.75$). Max accepted data age: 6 hours.
- **Satellite Evidence & Verification Layer:**
  - **Sentinel-1 SAR Change Detection:** Multi-temporal C-band GRD backscatter difference ($\Delta\text{VV}, \Delta\text{VH}$) with orbit matching.
  - **Sentinel-2 Optical Disturbance:** Harmonized surface reflectance $\Delta\text{NDVI}$ with cloud-cover masking.
  - **Copernicus DEM (GLO-30):** High-resolution 30m topographic grid elevation and slope calculation.
- **Multi-Source Evidence Fusion Layer:** Transparent 6-factor matrix decoupling statistical model predictions from satellite evidence, physical triggers, and field verification.
- **Regional Surveillance & Hotspots:** Asynchronous grid sampling and state/district vulnerability rankings across all 8 NER states.
- **Infrastructure & Highway Lifeline Corridors:** Buffer proximity analysis on National Highways (NH-10, NH-29, NH-06, NH-102), bridges, settlements, and schools with GIS data completeness warnings.
- **Explainable AI & DDMA Protocols:** Local feature attribution decomposition and actionable Standard Operating Procedure (SOP) checklists.
- **Historical Disaster Event Replay:** 7-day retrospective timeline simulator against benchmark disasters (Cyclone Remal 2024, Tupul 2022, Haflong 2022, Teesta 2023).
- **Field Evidence & Citizen Ground-Truth:** Moderated triage portal for tension cracks and ground deformations.
- **System Observability:** Live telemetry tracking API latency, GEE SLA, model throughput, and error rates.

---

## ⚠️ Important Scientific & Ethics Disclaimer
> [!IMPORTANT]
> The machine learning models in this system are research prototype candidates. They are **not calibrated for operational warning** and do not represent government-certified landslide evacuation alerts. The user interface explicitly distinguishes model predictions, satellite observations, data freshness, and research prototype status.

---

## 🚀 Quick Start Instructions

### 1. Backend Setup & Run

```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Run Automated Test Suite (48 tests across 8 test suites)
python -m pytest tests/ -v

# Launch FastAPI Server (runs on http://localhost:8000)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI Documentation: `http://localhost:8000/api/v1/docs`

### 2. Frontend Setup & Run

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Build production bundle & type check
npm run build

# Launch Vite Development Server (runs on http://localhost:5173)
npm run dev
```

---

## 📡 Key REST API Endpoints

### Core Models & Telemetry
- `GET /api/v1/health` - System health, database connectivity, and ML model readiness.
- `GET /api/v1/models/status` - Model registry, algorithm versions, thresholds, and operational flags.
- `GET /api/v1/locations` - List monitored stations across 8 NER states with state/district/bbox filters.
- `POST /api/v1/predictions/run` - Execute end-to-end multi-factor prediction pipeline for any coordinate.
- `GET /api/v1/predictions/latest/{location_id}` - Latest fused prediction and feature breakdown.
- `GET /api/v1/weather/{location_id}` - 7-window rainfall telemetry and 2-layer soil moisture.

### Satellite & Evidence Analysis
- `GET /api/v1/satellite-analysis/metadata` - GEE orbit, pass count, and cloud metadata.
- `GET /api/v1/satellite-analysis/sentinel1/change` - Multi-temporal SAR backscatter change ($\Delta\text{VV}, \Delta\text{VH}$).
- `GET /api/v1/satellite-analysis/sentinel2/ndvi` - Optical surface disturbance & vegetation $\Delta\text{NDVI}$.
- `POST /api/v1/evidence/evaluate` - Multi-source evidence aggregation matrix across 6 factors.
- `GET /api/v1/evidence/location/{location_id}` - Location-specific evidence breakdown.

### Regional Spatial & Corridors
- `GET /api/v1/spatial/hotspots` - Regional bounding-box grid cells with risk rankings.
- `GET /api/v1/spatial/states/summary` - Aggregate risk metrics across all 8 NER states.
- `POST /api/v1/exposure/analyze` - Infrastructure and population exposure in buffer zone.
- `GET /api/v1/exposure/corridors` - National Highway lifelines (NH-10, NH-29, NH-06, NH-102).
- `POST /api/v1/exposure/corridor-risk` - Segment-level corridor risk assessment.

### Explainability, Replay & Field Evidence
- `POST /api/v1/reports/generate` - Explainable AI attribution report & DDMA SOP.
- `GET /api/v1/replay/events` - Historical benchmark disaster scenarios.
- `POST /api/v1/replay/simulate/{event_id}` - 7-day retrospective timeline simulation.
- `POST /api/v1/field-reports` - Submit field ground-truth observation.
- `GET /api/v1/monitoring/telemetry` - Live API latency, GEE SLA, and error rate telemetry.
