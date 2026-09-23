from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.core.logger import logger
from app.models.location import Location

NER_SEED_LOCATIONS: List[Dict[str, Any]] = [
    # Arunachal Pradesh
    {"name": "Itanagar Capital Complex", "state": "Arunachal Pradesh", "district": "Papum Pare", "latitude": 27.0844, "longitude": 93.6053, "elevation_m": 440.0, "slope_deg": 18.5},
    {"name": "Tawang Hill Pass", "state": "Arunachal Pradesh", "district": "Tawang", "latitude": 27.5861, "longitude": 91.8594, "elevation_m": 3048.0, "slope_deg": 32.0},
    {"name": "Pasighat Foothills", "state": "Arunachal Pradesh", "district": "East Siang", "latitude": 28.0667, "longitude": 95.3333, "elevation_m": 155.0, "slope_deg": 12.0},
    {"name": "Changlang Valley Slope", "state": "Arunachal Pradesh", "district": "Changlang", "latitude": 27.1264, "longitude": 95.7337, "elevation_m": 580.0, "slope_deg": 22.4},

    # Assam
    {"name": "Haflong Hill Station", "state": "Assam", "district": "Dima Hasao", "latitude": 25.1764, "longitude": 93.0189, "elevation_m": 680.0, "slope_deg": 28.6},
    {"name": "Guwahati Kamakhya Ridge", "state": "Assam", "district": "Kamrup Metropolitan", "latitude": 26.1664, "longitude": 91.7058, "elevation_m": 160.0, "slope_deg": 15.0},
    {"name": "Diphu High Range", "state": "Assam", "district": "Karbi Anglong", "latitude": 25.8433, "longitude": 93.4312, "elevation_m": 290.0, "slope_deg": 19.8},
    {"name": "Silchar Cachar Edge", "state": "Assam", "district": "Cachar", "latitude": 24.8333, "longitude": 92.7789, "elevation_m": 35.0, "slope_deg": 8.5},

    # Manipur
    {"name": "Noney Railway Corridor", "state": "Manipur", "district": "Noney", "latitude": 24.7892, "longitude": 93.5975, "elevation_m": 550.0, "slope_deg": 34.2},
    {"name": "Imphal Valley Basin", "state": "Manipur", "district": "Imphal West", "latitude": 24.8170, "longitude": 93.9368, "elevation_m": 786.0, "slope_deg": 9.2},
    {"name": "Ukhrul Hill Ridge", "state": "Manipur", "district": "Ukhrul", "latitude": 25.1167, "longitude": 94.3667, "elevation_m": 1662.0, "slope_deg": 26.4},
    {"name": "Tamenglong Forest Slope", "state": "Manipur", "district": "Tamenglong", "latitude": 24.9833, "longitude": 93.4833, "elevation_m": 1260.0, "slope_deg": 30.1},

    # Meghalaya
    {"name": "Sohra (Cherrapunji) Cliff", "state": "Meghalaya", "district": "East Khasi Hills", "latitude": 25.2744, "longitude": 91.7323, "elevation_m": 1430.0, "slope_deg": 31.5},
    {"name": "Shillong Peak Slopes", "state": "Meghalaya", "district": "East Khasi Hills", "latitude": 25.5788, "longitude": 91.8933, "elevation_m": 1525.0, "slope_deg": 22.0},
    {"name": "Mawsynram Plateau Edge", "state": "Meghalaya", "district": "South West Khasi Hills", "latitude": 25.2975, "longitude": 91.5828, "elevation_m": 1400.0, "slope_deg": 29.8},
    {"name": "Tura Peak Range", "state": "Meghalaya", "district": "West Garo Hills", "latitude": 25.5138, "longitude": 90.2201, "elevation_m": 872.0, "slope_deg": 24.0},

    # Mizoram
    {"name": "Aizawl Ridge Sector", "state": "Mizoram", "district": "Aizawl", "latitude": 23.7271, "longitude": 92.7176, "elevation_m": 1132.0, "slope_deg": 27.5},
    {"name": "Champhai Border Slope", "state": "Mizoram", "district": "Champhai", "latitude": 23.4738, "longitude": 93.3278, "elevation_m": 1356.0, "slope_deg": 23.8},
    {"name": "Lunglei South Highway", "state": "Mizoram", "district": "Lunglei", "latitude": 22.8833, "longitude": 92.7333, "elevation_m": 722.0, "slope_deg": 25.2},
    {"name": "Kolasib River Bluff", "state": "Mizoram", "district": "Kolasib", "latitude": 24.2247, "longitude": 92.6789, "elevation_m": 610.0, "slope_deg": 21.0},

    # Nagaland
    {"name": "Kohima By-pass Corridor", "state": "Nagaland", "district": "Kohima", "latitude": 25.6751, "longitude": 94.1086, "elevation_m": 1444.0, "slope_deg": 29.0},
    {"name": "Mokokchung Ridge", "state": "Nagaland", "district": "Mokokchung", "latitude": 26.3247, "longitude": 94.5208, "elevation_m": 1325.0, "slope_deg": 24.5},
    {"name": "Phek Highland Slope", "state": "Nagaland", "district": "Phek", "latitude": 25.6833, "longitude": 94.5000, "elevation_m": 1500.0, "slope_deg": 31.0},
    {"name": "Dimapur Foothill Transition", "state": "Nagaland", "district": "Dimapur", "latitude": 25.9068, "longitude": 93.7272, "elevation_m": 195.0, "slope_deg": 9.0},

    # Sikkim
    {"name": "Gangtok Ridge Corridor", "state": "Sikkim", "district": "East Sikkim", "latitude": 27.3389, "longitude": 88.6065, "elevation_m": 1650.0, "slope_deg": 33.0},
    {"name": "Mangan North Highway", "state": "Sikkim", "district": "North Sikkim", "latitude": 27.5097, "longitude": 88.5283, "elevation_m": 1310.0, "slope_deg": 36.5},
    {"name": "Namchi Hill Slopes", "state": "Sikkim", "district": "South Sikkim", "latitude": 27.1667, "longitude": 88.3500, "elevation_m": 1315.0, "slope_deg": 28.0},
    {"name": "Gyalshing Valley Edge", "state": "Sikkim", "district": "West Sikkim", "latitude": 27.2833, "longitude": 88.2500, "elevation_m": 1700.0, "slope_deg": 30.5},

    # Tripura
    {"name": "Jampui Hills Ridge", "state": "Tripura", "district": "North Tripura", "latitude": 23.9789, "longitude": 92.2742, "elevation_m": 930.0, "slope_deg": 20.5},
    {"name": "Agartala City Basin", "state": "Tripura", "district": "West Tripura", "latitude": 23.8315, "longitude": 91.2868, "elevation_m": 16.0, "slope_deg": 5.0},
    {"name": "Dharmanagar River Edge", "state": "Tripura", "district": "North Tripura", "latitude": 24.3833, "longitude": 92.1667, "elevation_m": 29.0, "slope_deg": 7.5},
    {"name": "Udaipur Terrace Slope", "state": "Tripura", "district": "Gomati", "latitude": 23.5333, "longitude": 91.4833, "elevation_m": 32.0, "slope_deg": 8.0},
]


def seed_database(db: Session):
    """Seed base NER monitoring locations if database is empty."""
    existing_count = db.query(Location).count()
    if existing_count > 0:
        logger.info(f"Database already contains {existing_count} locations. Skipping seed.")
        return

    logger.info(f"Seeding {len(NER_SEED_LOCATIONS)} initial monitoring stations across 8 NER states...")
    for loc_data in NER_SEED_LOCATIONS:
        loc = Location(**loc_data)
        db.add(loc)
    db.commit()
    logger.info("NER seed stations created successfully.")
