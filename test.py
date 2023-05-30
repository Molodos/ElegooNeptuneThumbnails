# Copyright (c) 2023 Molodos
# The ElegooNeptune3Thumbnails plugin is released under the terms of the AGPLv3 or higher.

import sys

from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QFont

app = QtWidgets.QApplication(sys.argv)
image = QImage(900, 900, QImage.Format.Format_ARGB32)
painter = QPainter(image)
painter.fillRect(0, 0, 900, 900, Qt.GlobalColor.gray)
font = QFont("Arial", 60)
painter.setFont(font)
painter.setPen(Qt.GlobalColor.darkGreen)
painter.drawText(0, 0, 880, 890, Qt.AlignmentFlag.AlignRight + Qt.AlignmentFlag.AlignBottom, "12:07")
painter.drawText(0, 0, 880, 890, Qt.AlignmentFlag.AlignRight + Qt.AlignmentFlag.AlignBottom, "12:07")
painter.end()
image.save("test.png")
