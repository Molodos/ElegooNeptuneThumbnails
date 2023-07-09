# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import sys
from os import path

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QFont, QColor


class Test:
    colors: dict[str, QColor] = {
        "green": QColor(34, 236, 128),
        "red": QColor(209, 76, 81),
        "yellow": QColor(251, 226, 0),
        "white": QColor(255, 255, 255),
        "bg_dark": QColor(30, 36, 52),
        "bg_light": QColor(46, 54, 75),
        "bg_thumbnail": QColor(48, 57, 79),
        "own_gray": QColor(200, 200, 200)
    }
    thumbnail_bg_path: str = path.join(path.dirname(path.realpath(__file__)), "..", "bg_thumbnail.png")
    demo_in_path: str = path.join(path.dirname(path.realpath(__file__)), "cura_screen_example.png")
    demo_out_path: str = path.join(path.dirname(path.realpath(__file__)), "demo.png")

    @classmethod
    def test(cls) -> None:
        app = QtWidgets.QApplication(sys.argv)
        screen = QImage(cls.demo_in_path)
        screen = cls.add_background(screen)
        for i, line in enumerate(reversed(["⬌ 3.86m", "⭗ 12g", "⧗ 0.2mm", "⧖ 1:06h"])):
            if i < 4:
                screen = cls.add_text(screen, line, i > 1, i % 2 == 1)
        screen.save(cls.demo_out_path)

    @classmethod
    def add_background(cls, image: QImage) -> QImage:
        """
        Adds a background to replace the transparent one
        """
        background = QImage(cls.thumbnail_bg_path)
        painter = QPainter(background)
        painter.drawImage(150, 160, image)
        painter.end()
        return background

    @classmethod
    def add_text(cls, image: QImage, line: str, top: bool, left: bool) -> QImage:
        """
        Adds text line to the image
        """
        painter = QPainter(image)
        font = QFont("Arial", 30)
        painter.setFont(font)
        painter.setPen(cls.colors["own_gray"])
        painter.drawText(30 if left else 470, 20 if top else 790, 400, 100,
                         (Qt.AlignmentFlag.AlignLeft if left else Qt.AlignmentFlag.AlignRight) +
                         Qt.AlignmentFlag.AlignVCenter, line)
        painter.end()
        return image


if __name__ == "__main__":
    Test.test()
