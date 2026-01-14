import numpy as np
from nano_wait_vision.ocr import extract_text


def test_extract_text_none():
    assert extract_text(None) == ""


def test_extract_text_empty_image():
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    text = extract_text(img)
    assert isinstance(text, str)
