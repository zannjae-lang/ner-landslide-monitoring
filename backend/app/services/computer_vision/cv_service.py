from typing import Any, Dict, Optional
from app.schemas.predictions import ComputerVisionOutput


class ComputerVisionService:
    """Interface for future drone/satellite computer vision landslide detection."""

    def __init__(self):
        self.is_active = False

    def process_image(self, image_bytes: Optional[bytes] = None, metadata: Optional[Dict[str, Any]] = None) -> ComputerVisionOutput:
        """Processes optical/SAR image payload for landslide visual scars.

        Currently unvalidated and marked as inactive/unavailable.
        """
        return ComputerVisionOutput(
            module_name="Computer Vision Landslide Detector",
            status="Unavailable",
            evidence_probability=None,
            is_operational=False,
            message="CV module is currently inactive. No visual evidence fused into score.",
        )


cv_service = ComputerVisionService()
