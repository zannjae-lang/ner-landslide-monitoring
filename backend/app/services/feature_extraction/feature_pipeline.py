import asyncio
import math
from typing import Any, Dict, Optional, Tuple


from app.core.logger import logger
from app.schemas.predictions import Model1FeatureInput, Model2FeatureInput
from app.services.data_collectors.base import NormalizedObservation
from app.services.data_collectors.google_earth_engine import gee_service


class FeaturePipeline:
    """Extracts, validates, and normalizes feature vectors for Model 1 and Model 2."""

    # NER Region Approximate Geographic Bounding Box
    NER_BOUNDS = {
        "min_lat": 21.5,
        "max_lat": 29.5,
        "min_lon": 89.5,
        "max_lon": 97.5,
    }

    def validate_coordinates(self, latitude: float, longitude: float) -> Tuple[bool, Optional[str]]:
        if not (-90.0 <= latitude <= 90.0 and -180.0 <= longitude <= 180.0):
            return False, f"Coordinates out of world bounds: ({latitude}, {longitude})"
        
        is_ner = (
            self.NER_BOUNDS["min_lat"] <= latitude <= self.NER_BOUNDS["max_lat"]
            and self.NER_BOUNDS["min_lon"] <= longitude <= self.NER_BOUNDS["max_lon"]
        )
        if not is_ner:
            return True, f"Coordinates ({latitude}, {longitude}) are outside typical NER regional bounds."
        return True, None

    async def derive_live_terrain_features(
        self,
        latitude: float,
        longitude: float,
        elevation_override: Optional[float] = None,
        slope_override: Optional[float] = None,
    ) -> Tuple[Model1FeatureInput, Dict[str, Any]]:
        """Derive Model 1 features using live Google Earth Engine DEM & Sentinel-2 with fast timeout fallback."""
        telemetry_meta: Dict[str, Any] = {"dem_source": "topographic_model", "ndvi_source": "vegetation_index_prior"}

        elev = elevation_override
        ndvi_p50 = None
        ndvi_p90 = None
        ndvi_p10 = None

        if gee_service.is_initialized:
            try:
                # Run GEE DEM & Sentinel-2 concurrently with a 4-second timeout limit
                tasks = []
                if elev is None:
                    tasks.append(gee_service.get_dem_elevation(latitude, longitude))
                else:
                    tasks.append(asyncio.sleep(0, result=None))
                
                tasks.append(gee_service.get_sentinel2_ndvi(latitude, longitude))

                gee_results = await asyncio.wait_for(
                    asyncio.gather(*tasks, return_exceptions=True),
                    timeout=4.0
                )

                # Process DEM result
                dem_res = gee_results[0]
                if isinstance(dem_res, dict) and dem_res.get("elevation_m") is not None:
                    elev = dem_res["elevation_m"]
                    telemetry_meta["dem_source"] = "gee_copernicus_dem_glo30"
                    telemetry_meta["dem_tiles"] = dem_res.get("tile_count")

                # Process Sentinel-2 result
                s2_res = gee_results[1]
                if isinstance(s2_res, dict) and s2_res.get("ndvi_p50") is not None:
                    ndvi_p50 = s2_res["ndvi_p50"]
                    ndvi_p90 = s2_res["ndvi_p90"]
                    ndvi_p10 = s2_res["ndvi_p10"]
                    telemetry_meta["ndvi_source"] = "gee_sentinel2_optical"
                    telemetry_meta["ndvi_images"] = s2_res.get("image_count")
                    telemetry_meta["cloud_cover"] = s2_res.get("cloudy_pixel_percentage")
            except Exception as e:
                logger.info(f"Using topological fallback for feature extraction ({latitude}, {longitude}): {e}")

        m1_features = self.derive_terrain_features(
            latitude=latitude,
            longitude=longitude,
            elevation_override=elev,
            slope_override=slope_override,
            ndvi_p50_override=ndvi_p50,
            ndvi_p90_override=ndvi_p90,
            ndvi_p10_override=ndvi_p10,
        )
        return m1_features, telemetry_meta

    def derive_terrain_features(
        self,
        latitude: float,
        longitude: float,
        elevation_override: Optional[float] = None,
        slope_override: Optional[float] = None,
        ndvi_p50_override: Optional[float] = None,
        ndvi_p90_override: Optional[float] = None,
        ndvi_p10_override: Optional[float] = None,
    ) -> Model1FeatureInput:
        """Derive static terrain and geo-environmental features for Model 1."""
        lat_factor = (latitude - 22.0) / 7.0
        elev = elevation_override if elevation_override is not None else round(max(50.0, 350.0 + lat_factor * 2200.0), 1)
        slope = slope_override if slope_override is not None else round(min(55.0, max(5.0, 12.0 + lat_factor * 25.0)), 1)
        
        # Consistent terrain morphometrics
        curvature = round(0.01 + (math.sin(latitude * 10) * 0.04), 3)
        tpi = round(1.2 + math.cos(longitude * 5) * 1.5, 2)
        tri = round(slope * 0.22, 2)
        aspect_angle = math.radians((abs(latitude * 50 + longitude * 30)) % 360)
        aspect_sin = round(math.sin(aspect_angle), 4)
        aspect_cos = round(math.cos(aspect_angle), 4)
        
        # Vegetation NDVI percentiles
        if ndvi_p50_override is not None:
            p50 = ndvi_p50_override
            p90 = ndvi_p90_override if ndvi_p90_override is not None else min(1.0, round(p50 + 0.10, 3))
            p10 = ndvi_p10_override if ndvi_p10_override is not None else max(-1.0, round(p50 - 0.12, 3))
        else:
            p90 = round(0.78 - (elev / 8000.0), 3)
            p50 = round(p90 - 0.12, 3)
            p10 = round(p50 - 0.18, 3)
        
        # Distance to infrastructure & streams
        dist_road = round(max(20.0, 300.0 - (lat_factor * 100.0)), 1)
        dist_drainage = round(max(15.0, 180.0 - (slope * 2.0)), 1)

        return Model1FeatureInput(
            elevation=elev,
            slope=slope,
            curvature=curvature,
            tpi=tpi,
            tri=tri,
            aspect_sin=aspect_sin,
            aspect_cos=aspect_cos,
            ndvi_p90=p90,
            ndvi_p50=p50,
            ndvi_p10=p10,
            distance_to_road_m=dist_road,
            distance_to_drainage_m=dist_drainage,
            lulc_type="Forest" if elev > 500 else "Vegetation",
        )

    def assemble_model2_features(
        self,
        observation: NormalizedObservation,
        susceptibility_probability: float,
    ) -> Model2FeatureInput:
        """Assemble dynamic environmental feature vector for Model 2."""
        return Model2FeatureInput(
            Rainfall_1h=observation.rainfall_1h_mm,
            Rainfall_3h=observation.rainfall_3h_mm,
            Rainfall_6h=observation.rainfall_6h_mm,
            Rainfall_12h=observation.rainfall_12h_mm,
            Rainfall_24h=observation.rainfall_24h_mm,
            Rainfall_3day=observation.rainfall_3day_mm,
            Rainfall_7day=observation.rainfall_7day_mm,
            susceptibility_probability=susceptibility_probability,
            soil_moisture_layer_1=observation.soil_moisture_layer_1,
            soil_moisture_layer_2=observation.soil_moisture_layer_2,
        )


feature_pipeline = FeaturePipeline()
