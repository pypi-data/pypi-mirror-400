#!/usr/bin/env python

import numpy as np
import cv2 as cv


class RectangleDrawer:
    def __init__(self):
        self.start_point = None
        self.end_point = None
        self.drawing = False
        self.image = None

    def draw_rectangle(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.start_point = (x, y)
            self.drawing = True
        elif event == cv.EVENT_MOUSEMOVE and self.drawing:
            self.end_point = (x, y)
        elif event == cv.EVENT_LBUTTONUP:
            self.end_point = (x, y)
            self.drawing = False
            cv.rectangle(self.image, self.start_point, self.end_point, (0, 255, 0), 2)

    def run(self, image: np.ndarray):
        wname = 'Mark Region'
        cv.namedWindow(wname)
        cv.setMouseCallback(wname, self.draw_rectangle)

        self.image = image
        while True:
            display_image = image.copy()
            if self.start_point and self.end_point and self.drawing:
                cv.rectangle(display_image, self.start_point, self.end_point, (0, 255, 0), 2)

            cv.imshow(wname, display_image)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()
        return np.array([*self.start_point, *self.end_point], dtype=np.float32)


class PointDrawer:
    def __init__(self, radius=4, color=(0, 0, 255)):
        self.points = []
        self.image = None
        self.radius = radius
        self.color = color

    def draw_point(self, event, x, y, flags, param):
        if event == cv.EVENT_LBUTTONDOWN:
            self.points.append((x, y))
            cv.circle(self.image, (x, y), self.radius, self.color, -1)

    def run(self, image: np.ndarray):
        wname = 'Mark Points'
        cv.namedWindow(wname)
        cv.setMouseCallback(wname, self.draw_point)

        self.image = image.copy()

        while True:
            display_image = self.image.copy()

            for p in self.points:
                cv.circle(display_image, p, self.radius, self.color, -1)

            cv.imshow(wname, display_image)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break

        cv.destroyAllWindows()
        return np.asarray(self.points, dtype=np.float32)


class LabeledPointDrawer:
    def __init__(self, radius=4):
        self.points = []
        self.labels = []
        self.radius = radius

        self.image = None
        self.cursor = None  # current mouse position

        self.colors = {
            1: (0, 255, 0),  # include -> green
            0: (0, 0, 255),  # discard -> red
        }

    def mouse_move(self, event, x, y, flags, param):
        if event == cv.EVENT_MOUSEMOVE:
            self.cursor = (x, y)

    def run(self, image: np.ndarray):
        wname = 'Mark Points (i=include, d=discard, z=undo, q=quit)'
        cv.namedWindow(wname)
        cv.setMouseCallback(wname, self.mouse_move)

        self.image = image.copy()

        while True:
            display_image = self.image.copy()

            # draw existing points
            for (x, y), label in zip(self.points, self.labels):
                cv.circle(
                    display_image,
                    (x, y),
                    self.radius,
                    self.colors[label],
                    -1
                )

            # draw cursor preview
            if self.cursor is not None:
                cv.circle(
                    display_image,
                    self.cursor,
                    self.radius,
                    (255, 255, 255),
                    1
                )

            cv.imshow(wname, display_image)
            key = cv.waitKey(1) & 0xFF

            if key == ord('i') and self.cursor is not None:
                self.points.append(self.cursor)
                self.labels.append(1)

            elif key == ord('d') and self.cursor is not None:
                self.points.append(self.cursor)
                self.labels.append(0)

            elif key == ord('z'):
                if self.points:
                    self.points.pop()
                    self.labels.pop()

            elif key == ord('q'):
                break

        cv.destroyAllWindows()
        return (
            np.asarray(self.points, dtype=np.float32),
            np.asarray(self.labels, dtype=np.int64),
        )
