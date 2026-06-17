"""OpenCV image preprocessing for OCR."""

from pathlib import Path

import cv2
import numpy as np

from intelliclaim.application.interfaces.services import IImagePreprocessor


class OpenCVImagePreprocessor(IImagePreprocessor):
    """Applies deskew, denoise, contrast enhancement, and binarization."""

    def preprocess(self, image_path: Path, *, output_path: Path) -> Path:
        """Run the full preprocessing pipeline on an image file."""
        image = cv2.imread(str(image_path), cv2.IMREAD_COLOR)
        if image is None:
            msg = f"Unable to read image: {image_path}"
            raise ValueError(msg)

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        deskewed = self._deskew(gray)
        denoised = cv2.fastNlMeansDenoising(deskewed, h=10)
        enhanced = self._enhance_contrast(denoised)
        binary = self._binarize(enhanced)

        output_path.parent.mkdir(parents=True, exist_ok=True)
        cv2.imwrite(str(output_path), binary)
        return output_path

    def _deskew(self, gray: np.ndarray) -> np.ndarray:
        """Correct minor rotational skew using minimum area rectangle."""
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        coords = np.column_stack(np.where(binary > 0))
        if coords.size == 0:
            return gray

        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        elif angle > 45:
            angle = angle - 90

        if abs(angle) < 0.5:
            return gray

        height, width = gray.shape[:2]
        matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1.0)
        return cv2.warpAffine(
            gray,
            matrix,
            (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )

    def _enhance_contrast(self, gray: np.ndarray) -> np.ndarray:
        """Apply CLAHE contrast enhancement."""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        return clahe.apply(gray)

    def _binarize(self, gray: np.ndarray) -> np.ndarray:
        """Apply adaptive Gaussian thresholding."""
        return cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2,
        )
