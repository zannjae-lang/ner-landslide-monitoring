import json
from pathlib import Path

import ee


# ==========================================
# CONFIGURATION
# ==========================================

PROJECT_ID = "inlaid-reach-509012-c3"

KEY_PATH = Path(
    "credentials/inlaid-reach-509012-c3-4af425befbb4.json"
)

LATITUDE = 25.5
LONGITUDE = 93.0

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"


# ==========================================
# AUTHENTICATION
# ==========================================

def initialize_earth_engine():

    if not KEY_PATH.exists():
        raise FileNotFoundError(
            f"Service account key not found: {KEY_PATH}"
        )

    with KEY_PATH.open("r", encoding="utf-8") as file:
        credentials_info = json.load(file)

    credentials = ee.ServiceAccountCredentials(
        credentials_info["client_email"],
        key_file=str(KEY_PATH)
    )

    ee.Initialize(
        credentials=credentials,
        project=PROJECT_ID
    )

    print(
        "✅ Earth Engine authentication successful!",
        flush=True
    )


# ==========================================
# COLLECTION TEST FUNCTION
# ==========================================

def test_collection(name, collection, point):

    print(f"\n📡 Testing: {name}", flush=True)

    try:

        filtered_collection = (
            collection
            .filterBounds(point)
            .filterDate(START_DATE, END_DATE)
        )

        image_count = filtered_collection.size().getInfo()

        print(
            f"   Images found: {image_count}",
            flush=True
        )

        if image_count > 0:

            first_image = ee.Image(
                filtered_collection.first()
            )

            bands = first_image.bandNames().getInfo()

            print(
                f"   Available bands: {bands}",
                flush=True
            )

            print(
                "   Status: ✅ Accessible",
                flush=True
            )

        else:

            print(
                "   ⚠️ No images found",
                flush=True
            )

    except Exception as error:

        print(
            "   Status: ❌ Failed",
            flush=True
        )

        print(
            f"   Error: {error}",
            flush=True
        )


# ==========================================
# SENTINEL-1 SAR
# ==========================================

def test_sentinel1(point):

    collection = (
        ee.ImageCollection("COPERNICUS/S1_GRD")
        .filter(
            ee.Filter.eq(
                "instrumentMode",
                "IW"
            )
        )
        .filter(
            ee.Filter.listContains(
                "transmitterReceiverPolarisation",
                "VV"
            )
        )
    )

    test_collection(
        "Sentinel-1 SAR",
        collection,
        point
    )


# ==========================================
# SENTINEL-2 OPTICAL
# ==========================================

def test_sentinel2(point):

    collection = (
        ee.ImageCollection(
            "COPERNICUS/S2_SR_HARMONIZED"
        )
        .filter(
            ee.Filter.lte(
                "CLOUDY_PIXEL_PERCENTAGE",
                30
            )
        )
    )

    test_collection(
        "Sentinel-2 Optical / NDVI",
        collection,
        point
    )


# ==========================================
# COPERNICUS DEM GLO-30
# ==========================================

def test_dem(point):

    print(
        "\n📡 Testing: Copernicus DEM GLO-30",
        flush=True
    )

    try:

        # Updated Copernicus DEM dataset
        dem_collection = ee.ImageCollection(
            "COPERNICUS/DEM/GLO30_2024_1"
        )

        print(
            "   DEM collection loaded",
            flush=True
        )

        # DEM does not need date filtering
        dem_collection = (
            dem_collection
            .filterBounds(point)
        )

        image_count = (
            dem_collection
            .size()
            .getInfo()
        )

        print(
            f"   DEM tiles found: {image_count}",
            flush=True
        )

        if image_count == 0:

            print(
                "   ⚠️ No DEM tiles found",
                flush=True
            )

            return

        # Combine DEM tiles
        dem_image = dem_collection.mosaic()

        print(
            "   DEM tiles mosaiced",
            flush=True
        )

        # Extract elevation
        elevation = (
            dem_image
            .select("DEM")
            .reduceRegion(
                reducer=ee.Reducer.first(),
                geometry=point,
                scale=30,
                maxPixels=100000
            )
            .getInfo()
        )

        print(
            f"   Elevation data: {elevation}",
            flush=True
        )

        if (
            elevation
            and elevation.get("DEM") is not None
        ):

            elevation_value = elevation["DEM"]

            print(
                f"   Elevation: "
                f"{elevation_value} meters",
                flush=True
            )

            print(
                "   Status: ✅ DEM accessible",
                flush=True
            )

        else:

            print(
                "   ⚠️ Elevation value unavailable",
                flush=True
            )

    except Exception as error:

        print(
            "   Status: ❌ Failed",
            flush=True
        )

        print(
            f"   Error: {error}",
            flush=True
        )


# ==========================================
# MAIN FUNCTION
# ==========================================

def main():

    try:

        # Initialize Earth Engine first
        initialize_earth_engine()

        # Create point only after initialization
        point = ee.Geometry.Point(
            [
                LONGITUDE,
                LATITUDE
            ]
        )

        print(
            f"\n📍 Location: "
            f"{LATITUDE}, {LONGITUDE}",
            flush=True
        )

        print(
            f"📅 Date range: "
            f"{START_DATE} to {END_DATE}",
            flush=True
        )

        print(
            "\n" + "=" * 50,
            flush=True
        )

        print(
            "SATELLITE DATA ACCESS TEST",
            flush=True
        )

        print(
            "=" * 50,
            flush=True
        )

        # Test Sentinel-1
        test_sentinel1(point)

        # Test Sentinel-2
        test_sentinel2(point)

        # Test Copernicus DEM
        test_dem(point)

        print(
            "\n" + "=" * 50,
            flush=True
        )

        print(
            "✅ Satellite testing completed",
            flush=True
        )

        print(
            "=" * 50,
            flush=True
        )

    except Exception as error:

        print(
            "\n❌ INITIALIZATION FAILED",
            flush=True
        )

        print(
            f"Error: {error}",
            flush=True
        )


# ==========================================
# SCRIPT ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()