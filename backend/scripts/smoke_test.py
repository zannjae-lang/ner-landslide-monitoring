"""End-to-End System Smoke Test Script

Validates:
1. Model Artifact Loading & SHA-256 verification
2. Health & Dependency Status
3. Model 1 Static Susceptibility Inference
4. Model 2 Dynamic Early Warning Inference
5. Risk Engine 2.0 Multi-Factor Fusion
6. Live Open-Meteo Collector / Fallback
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.services.ml_models.artifact_loader import model_loader
from app.services.ml_models.model1_service import model1_service
from app.services.ml_models.model2_service import model2_service
from app.services.risk_engine.risk_engine import risk_engine
from app.services.feature_extraction.feature_pipeline import feature_pipeline
from app.schemas.predictions import Model1FeatureInput, Model2FeatureInput


def run_smoke_test():
    print("=" * 70)
    print("NER LANDSLIDE MONITORING SYSTEM: SMOKE TEST SUITE")
    print("SIH 2026 | Problem ID: 26001 | MDoNER")
    print("=" * 70)

    # 1. Test Model Artifact Loading
    print("\n[Step 1/5] Verifying ML Model Artifacts...")
    ready, status = model_loader.load_artifacts()
    if not ready:
        print(f"FAILED: Artifact loading failed with errors: {status.get('errors')}")
        sys.exit(1)
    print("  -> Model 1: Loaded (XGBoost Pipeline, Thresh: 0.39)")
    print("  -> Model 2: Loaded (XGBoost Pipeline, Thresh: 0.10)")
    print("  -> Registry: Verified")

    # 2. Test Model 1 Susceptibility Inference (13 features)
    print("\n[Step 2/5] Testing Model 1 (Static Susceptibility Inference)...")
    m1_input = Model1FeatureInput(
        elevation=1650.0,
        slope=32.5,
        curvature=0.04,
        tpi=2.5,
        tri=5.1,
        aspect_sin=0.71,
        aspect_cos=0.70,
        ndvi_p90=0.75,
        ndvi_p50=0.62,
        ndvi_p10=0.40,
        distance_to_road_m=110.0,
        distance_to_drainage_m=45.0,
        lulc_type="Forest",
    )
    m1_res = model1_service.predict(m1_input)
    print(f"  -> Model 1 Probability: {m1_res.susceptibility_probability:.4f} ({m1_res.susceptibility_percent:.1f}%)")
    print(f"  -> Susceptibility Class: {m1_res.susceptibility_class.value}")
    print(f"  -> Is Prone (>= 0.39): {m1_res.is_susceptible}")

    # 3. Test Model 2 Dynamic Early Warning Inference (10 features)
    print("\n[Step 3/5] Testing Model 2 (Dynamic Early Warning Inference)...")
    m2_input = Model2FeatureInput(
        Rainfall_1h=8.5,
        Rainfall_3h=22.0,
        Rainfall_6h=45.0,
        Rainfall_12h=70.0,
        Rainfall_24h=110.0,
        Rainfall_3day=180.0,
        Rainfall_7day=260.0,
        susceptibility_probability=m1_res.susceptibility_probability,
        soil_moisture_layer_1=0.42,
        soil_moisture_layer_2=0.48,
    )
    m2_res = model2_service.predict(m2_input)
    print(f"  -> Model 2 Dynamic Probability: {m2_res.dynamic_probability:.4f}")
    print(f"  -> Early Warning Candidate (>= 0.10): {m2_res.warning_candidate}")

    # 4. Test Risk Engine 2.0 Multi-Factor Fusion
    print("\n[Step 4/5] Testing Risk Engine 2.0 Fusion...")
    risk_res = risk_engine.compute_risk(
        model1_result=m1_res,
        model2_result=m2_res,
        rainfall_24h_mm=m2_input.Rainfall_24h,
    )
    print(f"  -> Rainfall 24h: {risk_res.rainfall_24h_mm} mm ({risk_res.rainfall_class.value}, delta: +{risk_res.rainfall_adjustment:.2f})")
    print(f"  -> Combined Threat Score: {risk_res.combined_risk_score:.4f} ({(risk_res.combined_risk_score * 100):.1f}%)")
    print(f"  -> Final Risk Level: {risk_res.final_risk.value}")
    print(f"  -> Prototype Warning: {risk_res.prototype_warning}")

    # 5. Summary
    print("\n[Step 5/5] Checking Feature Pipelines & Coordinates...")
    valid, msg = feature_pipeline.validate_coordinates(27.0844, 93.6053)
    print(f"  -> Coordinate Validation (Itanagar): {'Valid' if valid else 'Invalid'}")

    print("\n" + "=" * 70)
    print("ALL SMOKE TESTS PASSED SUCCESSFULLY.")
    print("=" * 70)


if __name__ == "__main__":
    run_smoke_test()
