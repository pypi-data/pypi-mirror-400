"""Vision processing for LLM capability."""

import base64
from io import BytesIO
from typing import List, Tuple

import numpy as np
from PIL import Image as PILImage

from highlighter.core.data_models.data_sample import DataSample

from .config import VisionConfig

__all__ = ["VisionProcessor"]


class VisionProcessor:
    """Handles image encoding, resizing, format detection

    Extracts images from DataSamples, resizes if needed, and
    encodes as base64 for LLM API transmission.
    """

    def __init__(self, config: VisionConfig):
        self.config = config

    def prepare_visual_content(self, data_samples: List[DataSample]) -> List[dict]:
        """Extract and prepare images from DataSamples

        Returns list of image content blocks ready for LLM API.

        Args:
            data_samples: List of DataSample objects

        Returns:
            List of dicts with 'type', 'source' keys for LLM API
        """
        if not self.config.enabled:
            return []

        visual_samples = [ds for ds in data_samples if ds.content_type.startswith(("image", "video"))]

        content_blocks = []
        for ds in visual_samples[: self.config.max_images_per_request]:
            image = self._extract_image(ds)

            if self.config.resize_images:
                image = self._resize_if_needed(image, ds.wh)

            image_data, media_type = self._encode_image(image)

            content_blocks.append(
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": image_data},
                }
            )

        return content_blocks

    def _extract_image(self, data_sample: DataSample):
        """Extract image from DataSample

        Args:
            data_sample: DataSample with image/video content

        Returns:
            PIL Image or numpy array

        Raises:
            NotImplementedError: If video frame extraction not supported
        """
        if data_sample.content_type.startswith("video"):
            if isinstance(data_sample.content, (np.ndarray, PILImage.Image)):
                return data_sample.content
            raise NotImplementedError(
                "Video frame extraction not implemented. " "Ensure video sources emit frames as DataSamples."
            )
        return data_sample.content

    def _resize_if_needed(self, image, original_size: Tuple[int, int]):
        """Resize if exceeds max dimension

        Args:
            image: PIL Image or numpy array
            original_size: (width, height) tuple

        Returns:
            Resized image (PIL Image)
        """
        w, h = original_size
        max_dim = self.config.max_image_dimension

        if max(w, h) > max_dim:
            if w > h:
                new_w, new_h = max_dim, int(h * max_dim / w)
            else:
                new_w, new_h = int(w * max_dim / h), max_dim

            if isinstance(image, np.ndarray):
                image = PILImage.fromarray(image)
            return image.resize((new_w, new_h), PILImage.Resampling.LANCZOS)

        return image

    def _encode_image(self, image) -> Tuple[str, str]:
        """Encode image to base64 with format detection

        Detects best format (PNG for transparency, JPEG otherwise)
        and encodes image as base64 string.

        Args:
            image: PIL Image or numpy array

        Returns:
            Tuple of (base64_data, media_type)
        """
        if isinstance(image, np.ndarray):
            image = PILImage.fromarray(image)

        # Detect format based on image mode
        if self.config.preserve_format and image.mode in ("RGBA", "LA", "P"):
            format_type = "PNG"
            media_type = "image/png"
            save_kwargs = {"format": format_type}
        else:
            # Convert to RGB if needed
            if image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            format_type = "JPEG"
            media_type = "image/jpeg"
            save_kwargs = {"format": format_type, "quality": self.config.image_quality}

        buffer = BytesIO()
        image.save(buffer, **save_kwargs)
        image_bytes = buffer.getvalue()

        return base64.b64encode(image_bytes).decode("utf-8"), media_type
