"""Spatial layout utilities for key-value pair detection."""

from __future__ import annotations

from intelliclaim.domain.entities.ocr_result import OCRWord
from intelliclaim.domain.value_objects.bounding_box import BoundingBox


def normalize_box(box: BoundingBox, page_width: int, page_height: int) -> list[int]:
    """Convert pixel bounding box to LayoutLM 0-1000 [x0, y0, x1, y1] format."""
    if page_width <= 0 or page_height <= 0:
        return [0, 0, 0, 0]

    x0 = int(1000 * box.x / page_width)
    y0 = int(1000 * box.y / page_height)
    x1 = int(1000 * (box.x + box.width) / page_width)
    y1 = int(1000 * (box.y + box.height) / page_height)
    return [
        max(0, min(1000, x0)),
        max(0, min(1000, y0)),
        max(0, min(1000, x1)),
        max(0, min(1000, y1)),
    ]


def words_to_tokens(
    words: list[OCRWord],
    *,
    page_number: int,
    page_width: int,
    page_height: int,
) -> list[dict[str, object]]:
    """Convert OCR words to layout token dictionaries."""
    tokens: list[dict[str, object]] = []
    for word in words:
        tokens.append(
            {
                "text": word.text,
                "label": "O",
                "confidence": word.confidence.value,
                "page_number": page_number,
                "bbox": word.bounding_box.to_dict(),
                "normalized_bbox": normalize_box(word.bounding_box, page_width, page_height),
            }
        )
    return tokens


def group_words_into_lines(words: list[OCRWord], *, y_tolerance: int = 15) -> list[list[OCRWord]]:
    """Group OCR words into horizontal lines by vertical proximity."""
    if not words:
        return []

    sorted_words = sorted(words, key=lambda word: (word.bounding_box.y, word.bounding_box.x))
    lines: list[list[OCRWord]] = [[sorted_words[0]]]

    for word in sorted_words[1:]:
        current_line = lines[-1]
        line_y = current_line[0].bounding_box.y
        if abs(word.bounding_box.y - line_y) <= y_tolerance:
            current_line.append(word)
        else:
            lines.append([word])

    for line in lines:
        line.sort(key=lambda word: word.bounding_box.x)
    return lines


def _line_text(line: list[OCRWord]) -> str:
    return " ".join(word.text for word in line)


def _merge_boxes(words: list[OCRWord]) -> BoundingBox:
    x_min = min(word.bounding_box.x for word in words)
    y_min = min(word.bounding_box.y for word in words)
    x_max = max(word.bounding_box.x + word.bounding_box.width for word in words)
    y_max = max(word.bounding_box.y + word.bounding_box.height for word in words)
    return BoundingBox(x=x_min, y=y_min, width=x_max - x_min, height=y_max - y_min)


def _split_line_at_colon(line: list[OCRWord]) -> tuple[list[OCRWord], list[OCRWord]] | None:
    for index, word in enumerate(line):
        if word.text.rstrip().endswith(":"):
            key_words = line[: index + 1]
            value_words = line[index + 1 :]
            if key_words and value_words:
                return key_words, value_words
    return None


def _split_line_by_columns(
    line: list[OCRWord],
    *,
    page_width: int,
) -> tuple[list[OCRWord], list[OCRWord]] | None:
    if page_width <= 0 or len(line) < 2:
        return None

    midpoint = page_width // 2
    left = [word for word in line if word.bounding_box.x + word.bounding_box.width <= midpoint]
    right = [word for word in line if word.bounding_box.x >= midpoint]
    if left and right:
        return left, right
    return None


def detect_key_value_pairs(
    words: list[OCRWord],
    *,
    page_number: int,
    page_width: int,
    page_height: int,
) -> list[dict[str, object]]:
    """Detect key-value pairs from OCR words using spatial layout heuristics."""
    pairs: list[dict[str, object]] = []
    lines = group_words_into_lines(words)

    for line in lines:
        split = _split_line_at_colon(line) or _split_line_by_columns(
            line,
            page_width=page_width,
        )
        if split is None:
            continue

        key_words, value_words = split
        key_text = _line_text(key_words).rstrip(":").strip()
        value_text = _line_text(value_words).strip()
        if not key_text or not value_text:
            continue

        confidences = [word.confidence.value for word in key_words + value_words]
        avg_confidence = sum(confidences) / len(confidences)

        pairs.append(
            {
                "key": key_text,
                "value": value_text,
                "page_number": page_number,
                "confidence": avg_confidence,
                "key_bbox": _merge_boxes(key_words).to_dict(),
                "value_bbox": _merge_boxes(value_words).to_dict(),
            }
        )

    return pairs
