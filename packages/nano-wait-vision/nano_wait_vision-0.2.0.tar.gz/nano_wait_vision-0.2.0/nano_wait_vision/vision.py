import time
import json
from pathlib import Path
from typing import Dict, Any

import cv2

from nano_wait import wait
from .vision_state import VisionState
from .ocr import extract_text, text_confidence
from .screen import capture_screen


VISION_DIR = Path.home() / ".nano-wait"
PATTERNS_FILE = VISION_DIR / "vision_patterns.json"

# Progressive timing phases: fast → normal → slow
PHASES = [
    ("fast", 0.2, 2.0),
    ("normal", 0.5, 5.0),
    ("slow", 1.0, None),
]


class VisionMode:
    def __init__(
        self,
        mode: str = "observe",
        verbose: bool = False,
        diagnostic: bool = False,
    ):
        self.mode = mode
        self.verbose = verbose
        self.diagnostic = diagnostic
        self.patterns = self._load_patterns()

    # ==========================
    # Public API
    # ==========================

    def observe(self) -> VisionState:
        frame = capture_screen()
        text = extract_text(frame).strip()

        return VisionState(
            name="observe",
            detected=bool(text),
            confidence=1.0 if text else 0.0,
            text=text,
            attempts=1,
            elapsed=0.0,
            diagnostics={"mode": "observe"},
        )

    def wait_text(self, text: str, timeout: float = 10.0) -> VisionState:
        """
        Wait until a given text appears on screen (OCR-based).

        Deterministic rule:
        - If the text appears anywhere in OCR output → detected = True
        """
        start = time.time()
        attempts = 0

        diagnostics: Dict[str, Any] = {
            "type": "text",
            "target": text,
            "phases": [],
        }

        for phase_name, interval, phase_limit in PHASES:
            phase_start = time.time()
            phase_attempts = 0

            while time.time() - start < timeout:
                if phase_limit and time.time() - phase_start > phase_limit:
                    break

                frame = capture_screen()
                detected_text = extract_text(frame)

                attempts += 1
                phase_attempts += 1

                conf = text_confidence(detected_text, text)

                # For UI automation, presence == success
                if conf >= 0.6:
                    diagnostics["phases"].append(
                        {
                            "phase": phase_name,
                            "attempts": phase_attempts,
                            "result": "success",
                        }
                    )

                    return VisionState(
                        name=text,
                        detected=True,
                        confidence=conf,
                        text=detected_text,
                        attempts=attempts,
                        elapsed=time.time() - start,
                        diagnostics=diagnostics,
                    )

                wait(interval, smart=True)

            diagnostics["phases"].append(
                {
                    "phase": phase_name,
                    "attempts": phase_attempts,
                    "result": "timeout",
                }
            )

        state = VisionState(
            name=text,
            detected=False,
            confidence=0.0,
            attempts=attempts,
            elapsed=time.time() - start,
            reason="timeout",
            diagnostics=diagnostics,
        )

        self._maybe_print_diagnostics(state)
        return state

    def wait_icon(
        self,
        icon_path: str,
        timeout: float = 10.0,
        threshold: float = 0.8,
    ) -> VisionState:
        icon = cv2.imread(icon_path, cv2.IMREAD_GRAYSCALE)
        if icon is None:
            raise FileNotFoundError(f"Icon not found: {icon_path}")

        start = time.time()
        attempts = 0
        best_confidence = 0.0

        diagnostics: Dict[str, Any] = {
            "type": "icon",
            "target": icon_path,
            "threshold": threshold,
            "phases": [],
        }

        for phase_name, interval, phase_limit in PHASES:
            phase_start = time.time()
            phase_attempts = 0

            while time.time() - start < timeout:
                if phase_limit and time.time() - phase_start > phase_limit:
                    break

                screen = capture_screen(gray=True)
                result = cv2.matchTemplate(screen, icon, cv2.TM_CCOEFF_NORMED)
                _, max_val, _, _ = cv2.minMaxLoc(result)

                attempts += 1
                phase_attempts += 1
                best_confidence = max(best_confidence, float(max_val))

                if max_val >= threshold:
                    diagnostics["phases"].append(
                        {
                            "phase": phase_name,
                            "attempts": phase_attempts,
                            "result": "success",
                            "confidence": float(max_val),
                        }
                    )

                    return VisionState(
                        name=icon_path,
                        detected=True,
                        confidence=float(max_val),
                        icon=icon_path,
                        attempts=attempts,
                        elapsed=time.time() - start,
                        diagnostics=diagnostics,
                    )

                wait(interval, smart=True)

            diagnostics["phases"].append(
                {
                    "phase": phase_name,
                    "attempts": phase_attempts,
                    "result": "timeout",
                }
            )

        state = VisionState(
            name=icon_path,
            detected=False,
            confidence=best_confidence,
            icon=icon_path,
            attempts=attempts,
            elapsed=time.time() - start,
            reason="timeout",
            diagnostics=diagnostics,
        )

        self._maybe_print_diagnostics(state)
        return state

    # ==========================
    # Diagnostics
    # ==========================

    def _maybe_print_diagnostics(self, state: VisionState):
        if not (self.verbose or self.diagnostic):
            return

        print("\n[Vision Diagnostic]")
        print(f"Target      : {state.name}")
        print(f"Detected    : {state.detected}")
        print(f"Confidence  : {state.confidence:.3f}")
        print(f"Attempts    : {state.attempts}")
        print(f"Elapsed     : {state.elapsed:.2f}s")
        print(f"Reason      : {state.reason}")

        for phase in state.diagnostics.get("phases", []):
            print(
                f"  - Phase {phase['phase']}: "
                f"{phase['attempts']} attempts → {phase['result']}"
            )

    # ==========================
    # Persistence
    # ==========================

    def _load_patterns(self):
        if not PATTERNS_FILE.exists():
            return {}

        with open(PATTERNS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_patterns(self):
        VISION_DIR.mkdir(parents=True, exist_ok=True)
        with open(PATTERNS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.patterns, f, indent=2)
