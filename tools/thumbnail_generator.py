# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from os import path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QColor, QFont

from cura.Snapshot import Snapshot
from .settings import Settings


class ThumbnailGenerator:
    """
    Thumbnail generator
    """

    COLORS: dict[str, QColor] = {
        "green": QColor(34, 236, 128),
        "red": QColor(209, 76, 81),
        "yellow": QColor(251, 226, 0),
        "white": QColor(255, 255, 255),
        "bg_dark": QColor(30, 36, 52),
        "bg_light": QColor(46, 54, 75),
        "bg_thumbnail": QColor(48, 57, 79),
        "own_gray": QColor(200, 200, 200)
    }
    BACKGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_thumbnail.png")
    PREVIEW_BACKGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_preview.png")
    FOREGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "benchy.png")
    NO_FOREGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "cross.png")
    THUMBNAIL_PREVIEW_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "thumbnail_preview.png")

    @classmethod
    def render_preview(cls, settings: Settings) -> None:
        """
        Render preview image based on settings
        """
        thumbnail: QImage = cls._render_thumbnail(settings=settings)
        thumbnail.save(cls.THUMBNAIL_PREVIEW_PATH)

    @classmethod
    def _render_thumbnail(cls, settings: Settings, is_preview: bool = True) -> QImage:
        """
        Renders a thumbnail based on settings
        """
        # Create background
        background: QImage
        if is_preview:
            background = QImage(cls.PREVIEW_BACKGROUND_IMAGE_PATH)
        else:
            background = QImage(cls.BACKGROUND_IMAGE_PATH)

        # Create foreground
        foreground: QImage
        if not settings.thumbnails_enabled:
            foreground = QImage(cls.NO_FOREGROUND_IMAGE_PATH)
        elif settings.use_current_model or not is_preview:
            foreground = Snapshot.snapshot(width=600, height=600)
        else:
            foreground = QImage(cls.FOREGROUND_IMAGE_PATH)

        # Paint foreground on background
        if foreground:
            painter = QPainter(background)
            painter.drawImage(150, 160, foreground)
            painter.end()

        # Don't add options if thumbnails disabled
        if not settings.thumbnails_enabled:
            return background

        # Generate option lines
        lines: list[str] = cls._generate_option_lines(settings=settings)

        # Add options
        painter = QPainter(background)
        font = QFont("Arial", 30)
        painter.setFont(font)
        painter.setPen(cls.COLORS["own_gray"])
        for i, line in enumerate(lines):
            if line:
                left: bool = i % 2 == 0
                top: bool = i < 2
                painter.drawText(30 if left else 470,
                                 20 if top else 790, 400, 100,
                                 (Qt.AlignmentFlag.AlignLeft if left else Qt.AlignmentFlag.AlignRight) +
                                 Qt.AlignmentFlag.AlignVCenter, line)
        painter.end()

        # Return
        return background

    @classmethod
    def _generate_option_lines(cls, settings: Settings) -> list[str]:
        lines: list[str] = []
        for i in settings.corner_options:  # TODO: Check on how to retrieve real values from Cura when not using G-code
            option: str = list(settings.OPTIONS.keys())[i]
            if option == "nothing":
                lines.append("")
            elif option == "includeTimeEstimate":
                lines.append(f"⧖ 1:06h")
            elif option == "includeFilamentGramsEstimate":
                lines.append(f"⭗ 12g")
            elif option == "includeLayerHeight":
                lines.append(f"⧗ 0.2mm")
            elif option == "includeModelHeight":
                lines.append(f"⭱ 48mm")
            elif option == "includeFilamentMetersEstimate":
                lines.append(f"⬌ 3.90m")
            elif option == "includeCostEstimate":
                lines.append(f"⛁ 0.25€")
        return lines
