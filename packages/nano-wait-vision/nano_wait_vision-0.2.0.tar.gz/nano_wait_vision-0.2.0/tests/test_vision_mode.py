from nano_wait_vision.vision import VisionMode
from nano_wait_vision.vision_state import VisionState


def test_vision_mode_init():
    vision = VisionMode()
    assert vision.mode == "observe"


def test_observe_returns_vision_state():
    vision = VisionMode()
    state = vision.observe()
    assert isinstance(state, VisionState)


def test_wait_text_timeout():
    vision = VisionMode()
    state = vision.wait_text("TEXT_THAT_WILL_NOT_EXIST", timeout=1)
    assert state.detected is False
