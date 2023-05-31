# Copyright (c) 2023 Molodos
# The ElegooNeptune3Thumbnails plugin is released under the terms of the AGPLv3 or higher.

import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QFont


class Test:

    @classmethod
    def test(cls) -> None:
        app = QtWidgets.QApplication(sys.argv)
        image = QImage(900, 900, QImage.Format.Format_ARGB32)
        painter = QPainter(image)
        painter.fillRect(0, 0, 900, 900, Qt.GlobalColor.darkGray)
        painter.end()
        image = cls.add_text(image, ["0.15€", "11.4m", "1:03h"])
        image.save("test.png")

    @classmethod
    def add_text(cls, image: QImage, text: list[str]) -> QImage:
        painter = QPainter(image)
        font = QFont("Arial", 60)
        painter.setFont(font)
        painter.setPen(Qt.GlobalColor.darkGreen)
        for i, line in enumerate(reversed(text)):
            painter.drawText(0, 0, 880, 890 - (i * 110), Qt.AlignmentFlag.AlignRight + Qt.AlignmentFlag.AlignBottom,
                             line)
        painter.end()
        return image


if __name__ == "__main__":
    Test.test()
