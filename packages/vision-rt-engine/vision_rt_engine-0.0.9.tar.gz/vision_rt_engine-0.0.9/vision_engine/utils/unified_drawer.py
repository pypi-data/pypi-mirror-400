#!/usr/bin/env python

import cv2 as cv
import numpy as np
from typing import Tuple, List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class UnifiedDrawer:
    radius: int = 4
    rect_start: Optional[Tuple[int, int]] = None
    rect_end: Optional[Tuple[int, int]] = None
    rect_drawing: bool = False
    rect_finalized: bool = False
    rect_mode: bool = False
    
    points: List[Tuple[int, int]] = field(default_factory=lambda: [])
    labels: List[int] = field(default_factory=lambda: [])
    
    image: Optional[np.ndarray] = None
    cursor: Optional[Tuple[int, int]] = None
    window_name: str = ("Drawer | r:rect  i:+1  d:+0  z:undo  q/ESC:quit")
    
    colors: Optional[Dict[int, Tuple[int]]] = field(default_factory=lambda: {1: (0, 255, 0), 0: (0, 0, 255)})
    cursor_color: Optional[Tuple[int]] = field(default_factory=lambda: (255, 255, 255))

    def _clamp(self, x: int, y: int) -> Tuple[int, int]:
        h, w = self.image.shape[:2]
        return max(0, min(x, w - 1)), max(0, min(y, h - 1))

    def _reset_rect(self) -> None:
        self.rect_start = None
        self.rect_end = None
        self.rect_drawing = False
        self.rect_finalized = False

    def _current_rect(self) -> Optional[Tuple[int, int, int, int]]:
        if not (self.rect_start and self.rect_end):
            return None
        x1, y1 = self.rect_start
        x2, y2 = self.rect_end
        return min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)

    def _add_point(self, label: int) -> None:
        if self.cursor is None:
            return
        self.points.append(self.cursor)
        self.labels.append(int(label))

    def _mouse_event(self, event, x, y, *_):
        x, y = self._clamp(x, y)
        self.cursor = (x, y)

        if event == cv.EVENT_LBUTTONDOWN and self.rect_mode:
            self.rect_start = (x, y)
            self.rect_end = (x, y)
            self.rect_drawing = True
            self.rect_finalized = False

        elif event == cv.EVENT_MOUSEMOVE and self.rect_mode and self.rect_drawing:
            self.rect_end = (x, y)

        elif event == cv.EVENT_LBUTTONUP and self.rect_mode and self.rect_drawing:
            self.rect_end = (x, y)
            self.rect_drawing = False
            self.rect_finalized = True

    def _render(self) -> np.ndarray:
        canvas = self.image.copy()

        rect = self._current_rect()
        if rect:
            x1, y1, x2, y2 = rect
            thickness = 2 if self.rect_finalized else 1
            cv.rectangle(canvas, (x1, y1), (x2, y2), (0, 255, 0), thickness)

        for (x, y), label in zip(self.points, self.labels):
            cv.circle(canvas, (x, y), self.radius, self.colors[label], -1)

        if self.cursor is not None:
            cv.circle(canvas, self.cursor, self.radius, self.cursor_color, 1)

        mode = "RECT MODE" if self.rect_mode else "POINT MODE"
        status = (
            f"{mode} | Points: {len(self.points)} | "
            f"Rect: {'yes' if self.rect_finalized else 'no'}"
        )
        cv.putText(
            canvas, status, (10, 20),
            cv.FONT_HERSHEY_SIMPLEX, 0.5,
            (200, 200, 200), 1, cv.LINE_AA
        )

        return canvas

    def reset_all(self):
        self.cursor = None
        self._reset_rect()
        self.points.clear()
        self.labels.clear()
    
    def run(self, image: np.ndarray) -> Dict[str, Tuple[np.ndarray, ...]]:
        self.image = image.copy()
        self.reset_all()

        cv.namedWindow(self.window_name)
        cv.setMouseCallback(self.window_name, self._mouse_event)

        while True:
            cv.imshow(self.window_name, self._render())
            key = cv.waitKey(20) & 0xFF

            if key in (ord('q'), 27):
                break

            elif key == ord('r'):
                self.rect_mode = not self.rect_mode
                if not self.rect_mode:
                    self.rect_drawing = False

            elif key == ord('i'):
                self._add_point(1)

            elif key == ord('d'):
                self._add_point(0)

            elif key == ord('z') and self.points:
                self.points.pop()
                self.labels.pop()

            elif key == ord('c'):
                self.reset_all()

        cv.destroyAllWindows()

        rect = np.array(self._current_rect(), dtype=np.float32) if self.rect_finalized else None
        return {
            'bbox': rect,
            'points': np.asarray(self.points, dtype=np.float32),
            'labels': np.asarray(self.labels, dtype=np.int64),
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        img = cv.imread(sys.argv[1])
        if img is None:
            raise RuntimeError(f"Failed to read image: {sys.argv[1]}")
    else:
        img = np.full((480, 640, 3), 50, dtype=np.uint8)

    rect, pts, labels = UnifiedDrawer().run(img)
    print("Rect:", rect)
    print("Points:", pts)
    print("Labels:", labels)

