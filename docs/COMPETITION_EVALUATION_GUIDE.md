# NER-LANDSLIDE WATCH | SIH 2026 COMPETITION EVALUATION & JUDGE'S MANUAL
**Smart India Hackathon 2026 — Problem Statement ID: 26001**  
**Title:** AI-Based Early Warning and Landslide Risk Monitoring System for the North Eastern Region of India  
**Target Region:** All 8 States of North Eastern India (*Arunachal Pradesh, Assam, Manipur, Meghalaya, Mizoram, Nagaland, Sikkim, Tripura*)

---

## 1. Executive Summary & Problem Context

The North Eastern Region (NER) of India is among the most landslide-prone mountainous terrains in the world due to:
- Complex Himalayan & Indo-Burman tectonics with high seismic fragility
- Steep terrain slopes ($>25^\circ$) with highly weathered soils and weak sedimentary lithology
- Extreme monsoon precipitation (receiving $>2,000\text{ mm}$ annual rainfall, with cloudbursts $>100\text{ mm/24h}$)
- Strategic National Highway lifelines (NH-10, NH-29, NH-06, NH-102) whose blockages isolate entire state populations.

**NER-LANDSLIDE WATCH** is an evidence-driven, scientifically transparent, multi-modal disaster intelligence and early-warning platform designed specifically to address Problem Statement 26001.

---

## 2. Core Architectural Pillars

```
+----------------------------------------------------------------------------------------------------+
|                                      NER-LANDSLIDE WATCH PLATFORM                                  |
+----------------------------------------------------------------------------------------------------+
                                                  │
                 ┌────────────────────────────────┴────────────────────────────────┐
                 ▼                                                                 ▼
   ┌───────────────────────────┐                                     ┌───────────────────────────┐
   │    MACHINE LEARNING       │                                     │     SATELLITE EVIDENCE    │
   │        CORE               │                                     │     & GROUND TRUTH        │
   ├───────────────────────────┤                                     ├───────────────────────────┤
   │ Model 1: XGBoost Susc.    │                                     │ Sentinel-1 SAR GRD        │
   │ (13 static terrain vars)  │                                     │ (Multi-temporal ΔVV, ΔVH) │
   │ Threshold: 0.39           │                                     │                           │
   │                           │                                     │ Sentinel-2 Optical SR     │
   │ Model 2: XGBoost Dynamic  │                                     │ (Harmonized Surface ΔNDVI)│
   │ (10 dynamic rain/soil)    │                                     │                           │
   │ Threshold: 0.10           │                                     │ Copernicus DEM GLO-30     │
   │                           │                                     │ (30m high-res grid)       │
   │ Risk Engine 2.0:          │                                     │                           │
   │ 0.45*M1 + 0.55*M2 + ΔRain │                                     │ Field Ground Truth Triage │
   └───────────────────────────┘                                     └───────────────────────────┘
                 │                                                                 │
                 └────────────────────────────────┬────────────────────────────────┘
                                                  ▼
                         ┌─────────────────────────────────────────────────┐
                         │       MULTI-SOURCE EVIDENCE FUSION LAYER        │
                         ├─────────────────────────────────────────────────┤
                         │ - 6 Independent Multi-Modal Signals             │
                         │ - Supporting vs Conflicting Anomaly Signals     │
                         │ - Provenance & Data Freshness Quality Flags     │
                         │ - Mandatory Field Verification SOP Requirements │
                         └─────────────────────────────────────────────────┘
                                                  │
                 ┌────────────────────────────────┼────────────────────────────────┐
                 ▼                                ▼                                ▼
   ┌───────────────────────────┐    ┌───────────────────────────┐    ┌───────────────────────────┐
   │    REGIONAL GRID &        │    │    INFRASTRUCTURE &       │    │    EXPLAINABLE AI &       │
   │    HOTSPOT SURVEILLANCE   │    │    LIFELINE CORRIDORS     │    │    DISASTER REPLAY        │
   ├───────────────────────────┤    ├───────────────────────────┤    ├───────────────────────────┤
   │ - 8 NER States Coverage   │    │ - National Highway Routes │    │ - Local tree attribution  │
   │ - Dynamic Grid Sampling   │    │ - Road Proximity Buffers  │    │ - DDMA SOP Action Steps   │
   │ - District Rankings       │    │ - Bridges, Schools, Towns │    │ - 7-Day Catastrophe Replay│
   │ - Asynchronous Batching   │    │ - GIS Completeness Notice │    │   (Remal, Tupul, Haflong) │
   └───────────────────────────┘    └───────────────────────────┘    └───────────────────────────┘
```

---

## 3. Scientific Integrity & The "Zero-Touch" Models

### Model 1: Static Landslide Susceptibility
- **Artifact:** `model1_landslide_susceptibility.joblib` (`model1_v1.0`)
- **Algorithm:** XGBoost Classification
- **Decision Threshold:** `0.39`
- **13 Exact Features:**
  `[elevation, slope, curvature, tpi, tri, aspect_sin, aspect_cos, ndvi_p90, ndvi_p50, ndvi_p10, distance_to_road_m, distance_to_drainage_m, lulc_type]`

### Model 2: Dynamic Landslide Early-Warning Candidate
- **Artifact:** `model2_landslide_early_warning.joblib` (`model2_v1.0_temporal_candidate`)
- **Algorithm:** XGBoost Classification
- **Decision Threshold:** `0.10`
- **10 Exact Features:**
  `[Rainfall_1h, Rainfall_3h, Rainfall_6h, Rainfall_12h, Rainfall_24h, Rainfall_3day, Rainfall_7day, susceptibility_probability, soil_moisture_layer_1, soil_moisture_layer_2]`

### Baseline Risk Engine 2.0
$$\text{Combined Score} = \text{clip}\left(0.45 \times P_{\text{susc}} + 0.55 \times P_{\text{dyn}} + \Delta_{\text{rainfall}}, 0.0, 1.0\right)$$
- **Rainfall Adjustments ($\Delta_{\text{rainfall}}$):**
  - $< 15\text{ mm}$: $+0.00$
  - $15 - 35\text{ mm}$: $+0.05$
  - $35 - 65\text{ mm}$: $+0.10$
  - $\ge 65\text{ mm}$: $+0.15$
- **Risk Classification Bands:**
  - **Normal:** $< 0.25$
  - **Watch:** $0.25 - 0.50$
  - **Alert:** $0.50 - 0.75$
  - **Critical:** $\ge 0.75$

---

## 4. Multi-Source Evidence Fusion vs Raw Prediction

A major failure mode of naive AI systems is asserting that an ML prediction is an absolute truth. **NER-LANDSLIDE WATCH** explicitly decouples:
1. **Model Prediction:** What the statistical tree model estimates from training correlations.
2. **Physical Environmental Trigger:** What real-time precipitation gages & antecedent rainfall totals measure.
3. **Satellite Evidence:** What Sentinel-1 SAR backscatter changes ($\Delta\text{VV}, \Delta\text{VH}$) and Sentinel-2 vegetation optical changes ($\Delta\text{NDVI}$) observe through cloud-filtered imagery.
4. **Data Quality & Freshness:** Whether sensor streams are live ($<6\text{h}$), stale, or missing.
5. **Human Field Verification:** What ground-truth field inspectors report via verified tension crack audits.

---

## 5. Judge Demonstration Script (Step-by-Step)

Follow this 5-minute live demonstration script to showcase all 15 system phases to competition evaluators:

### Step 1: Open Live Monitoring Station
- Navigate to the **Monitoring** tab.
- Select a high-threat station (e.g. **Sonapur / Dima Hasao, Assam** or **Lunglei, Mizoram**).
- **Observe:**
  - Fused Risk Score ($>70\%$ during heavy rainfall triggers).
  - Dual XGBoost Model breakdown (Model 1 susceptibility vs Model 2 candidate).
  - 7 Rainfall Accumulation Windows ($1\text{h}$ to $7\text{d}$) plotted on interactive bar chart.
  - Live GEE Satellite Telemetry (Copernicus DEM 30m, Sentinel-2 Optical NDVI, Sentinel-1 SAR Backscatter dB).

### Step 2: Inspect Multi-Source Evidence & Exposure
- Scroll to the **Multi-Source Evidence Fusion Layer**.
- **Observe:** The 6 independent factor breakdown, data quality rating, supporting factors, and conflicting signals.
- Scroll to **Infrastructure & Population Exposure**.
- **Observe:** Exposed National Highway lifelines, distance to nearest road (e.g. $120\text{ m}$), settlement population estimates, and OpenStreetMap data completeness notices.

### Step 3: Trigger Explainable AI & DDMA Audit Brief
- Click the **"Explainable AI"** button in the top toolbar.
- **Observe:**
  - Executive Risk Interpretation in plain English.
  - Top driving factor attributions (Slope angle impact, 24h Rain impact, 3-day antecedent impact, soil saturation impact).
  - District Disaster Management Authority (DDMA) Actionable Standard Operating Procedure (SOP) checklist.

### Step 4: Run Historical Disaster Replay Benchmark
- Click the **"Disaster Replay"** button.
- Select **"Cyclone Remal Landslides (Mizoram 2024)"** or **"Tupul Railway Debris Flow (Manipur 2022)"**.
- Click **"Re-Run Replay"**.
- **Observe:** The 7-day retrospective disaster progression curve, showing how antecedent rainfall coupled with steep terrain forced the Risk Engine into Critical threat status on the documented event day.

### Step 5: Explore Regional Hotspots & Highway Lifeline Corridors
- Navigate to the **Risk Map** tab.
- Toggle **View: [Hotspot Grid]** to view regional grid cells across all 8 NER states.
- Toggle **View: [NH Corridors]** to inspect key transport arteries (NH-10 Sikkim, NH-29 Nagaland, NH-06 Meghalaya-Assam, NH-102 Manipur) with segment-level risk highlighting.

### Step 6: Verify System Telemetry & Remote Sensing Health
- Navigate to the **Data Sources & Health** tab.
- **Observe:**
  - FastAPI server uptime, SQLAlchemy database connection, and dual model SHA-256 verification.
  - Google Earth Engine (GEE) Remote Sensing SLA and API latency.
  - Live external weather provider connection test tools.

---

## 6. Testing & Quality Assurance Summary

The platform is backed by comprehensive automated regression and unit test suites:
- **Backend Test Suite:** `48/48 passed` (`python -m pytest tests/`)
  - `test_api_endpoints.py` (5 tests)
  - `test_data_collectors.py` (8 tests)
  - `test_gee_service.py` (4 tests)
  - `test_model1_inference.py` (2 tests)
  - `test_model2_inference.py` (2 tests)
  - `test_model_loader.py` (1 test)
  - `test_platform_features.py` (10 tests)
  - `test_risk_engine.py` (3 tests)
  - `test_satellite_evidence.py` (13 tests)
- **Frontend Build & Type Check:** `0 errors` (`tsc && vite build`)

---

## 7. Limitations & Operational Ethics Notice

1. **Research Candidate Models:** Model 1 and Model 2 are trained on available historical catalogs and have not undergone multi-year operational field deployment certification.
2. **Satellite Latency:** Sentinel-1 (6-12 day revisit) and Sentinel-2 (5-day revisit) are non-realtime orbital assets. Optical imagery is cloud-limited during monsoon peaks.
3. **No Automated Evacuation:** The system is an operational decision-support tool for disaster management authorities; it is not a direct substitute for official alerts issued by the Geological Survey of India (GSI) or India Meteorological Department (IMD).
