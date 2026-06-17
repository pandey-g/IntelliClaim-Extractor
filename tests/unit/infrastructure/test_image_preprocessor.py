"""Unit tests for OpenCV image preprocessor."""

import pytest

cv2 = pytest.importorskip("cv2")
import numpy as np

from intelliclaim.infrastructure.ocr.image_preprocessor import OpenCVImagePreprocessor


@pytest.mark.unit
class TestOpenCVImagePreprocessor:
    def test_preprocess_produces_output_file(self, tmp_path) -> None:
        input_path = tmp_path / "input.png"
        output_path = tmp_path / "output.png"

        image = np.full((100, 200, 3), 255, dtype=np.uint8)
        cv2.putText(
            image,
            "CLAIM",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 0),
            2,
        )
        cv2.imwrite(str(input_path), image)

        preprocessor = OpenCVImagePreprocessor()
        result = preprocessor.preprocess(input_path, output_path=output_path)

        assert result == output_path
        assert output_path.is_file()
        processed = cv2.imread(str(output_path), cv2.IMREAD_GRAYSCALE)
        assert processed is not None
        assert processed.shape == (100, 200)

    def test_preprocess_raises_for_missing_file(self, tmp_path) -> None:
        preprocessor = OpenCVImagePreprocessor()
        with pytest.raises(ValueError, match="Unable to read image"):
            preprocessor.preprocess(
                tmp_path / "missing.png",
                output_path=tmp_path / "out.png",
            )
