import pytesseract


def extract_text(image) -> str:
    if image is None:
        return ""

    try:
        return pytesseract.image_to_string(image)
    except Exception:
        return ""


def text_confidence(haystack: str, needle: str) -> float:
    """
    Heuristic confidence metric optimized for screen automation (not NLP).

    Rules:
    - If the target text is present → confidence = 1.0
    - Otherwise → 0.0

    This avoids false negatives when OCR returns large amounts of text.
    """
    if not haystack or not needle:
        return 0.0

    haystack_l = haystack.lower()
    needle_l = needle.lower()

    if needle_l in haystack_l:
        return 1.0

    return 0.0
