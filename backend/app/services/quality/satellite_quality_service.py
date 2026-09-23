from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from app.schemas.satellite_evidence import EvidenceQualityStatus


class SatelliteQualityService:
    """Evaluates satellite telemetry completeness, sensor comparability, temporal freshness, and atmospheric quality."""

    def evaluate_sentinel1_comparability(
        self,
        baseline_obs: Optional[Dict[str, Any]],
        recent_obs: Optional[Dict[str, Any]],
        total_found: int,
    ) -> Tuple[EvidenceQualityStatus, bool, List[str]]:
        reasons: List[str] = []

        if total_found == 0 or not baseline_obs or not recent_obs:
            reasons.append("Insufficient SAR passes found in the requested time windows.")
            return EvidenceQualityStatus.INSUFFICIENT_DATA, False, reasons

        # Check orbit direction comparability
        base_orbit = baseline_obs.get("orbit_direction")
        rec_orbit = recent_obs.get("orbit_direction")
        if base_orbit and rec_orbit and base_orbit != rec_orbit:
            reasons.append(
                f"Incompatible orbit directions: baseline is {base_orbit}, recent is {rec_orbit}. Geometry mismatch impairs backscatter comparison."
            )
            return EvidenceQualityStatus.LOW_QUALITY, False, reasons

        # Check relative orbit number if available
        base_rel = baseline_obs.get("relative_orbit_number")
        rec_rel = recent_obs.get("relative_orbit_number")
        if base_rel is not None and rec_rel is not None and base_rel != rec_rel:
            reasons.append(
                f"Relative orbit tracks differ (Baseline track {base_rel} vs Recent track {rec_rel}). Incidence angle variation may bias delta."
            )
            # Not strictly invalid, but tagged as requires verification
            return EvidenceQualityStatus.REQUIRES_VERIFICATION, True, reasons

        # Check missing polarisations
        if baseline_obs.get("vv_backscatter_db") is None or recent_obs.get("vv_backscatter_db") is None:
            reasons.append("Missing VV backscatter values in one or both observation windows.")
            return EvidenceQualityStatus.INSUFFICIENT_DATA, False, reasons

        return EvidenceQualityStatus.VALID, True, reasons

    def evaluate_sentinel2_quality(
        self,
        baseline_count: int,
        recent_count: int,
        baseline_cloud: float,
        recent_cloud: float,
        cloud_threshold: float,
        baseline_ndvi: Optional[float],
        recent_ndvi: Optional[float],
    ) -> Tuple[EvidenceQualityStatus, bool, List[str]]:
        reasons: List[str] = []

        if baseline_count == 0:
            reasons.append(
                f"Zero cloud-free Sentinel-2 images available in baseline period (cloud filter <= {cloud_threshold}%)."
            )
        if recent_count == 0:
            reasons.append(
                f"Zero cloud-free Sentinel-2 images available in recent period (cloud filter <= {cloud_threshold}%)."
            )

        if baseline_count == 0 or recent_count == 0:
            return EvidenceQualityStatus.INSUFFICIENT_DATA, False, reasons

        if baseline_ndvi is None or recent_ndvi is None:
            reasons.append("NDVI calculation yielded null values over the target coordinates.")
            return EvidenceQualityStatus.INSUFFICIENT_DATA, False, reasons

        # Cloud contamination warning
        if recent_cloud > cloud_threshold * 0.8:
            reasons.append(
                f"Recent composite cloud cover ({recent_cloud:.1f}%) is close to the threshold limit ({cloud_threshold}%); residual haze/shadow possible."
            )
            return EvidenceQualityStatus.REQUIRES_VERIFICATION, True, reasons

        return EvidenceQualityStatus.VALID, True, reasons

    def evaluate_freshness_hours(
        self, acquisition_time: Optional[datetime], max_freshness_hours: float = 720.0
    ) -> Tuple[Optional[float], List[str]]:
        if not acquisition_time:
            return None, ["Acquisition timestamp unavailable."]

        if acquisition_time.tzinfo is None:
            acquisition_time = acquisition_time.replace(tzinfo=timezone.utc)

        now_utc = datetime.now(timezone.utc)
        age_hours = round((now_utc - acquisition_time).total_seconds() / 3600.0, 1)

        warnings = []
        if age_hours > max_freshness_hours:
            warnings.append(
                f"Observation is {age_hours:.1f} hours old ({age_hours / 24.0:.1f} days), which exceeds typical revisit window."
            )
        return age_hours, warnings


satellite_quality_service = SatelliteQualityService()
