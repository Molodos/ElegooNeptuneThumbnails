# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from os import path

from PyQt6.QtGui import QImage, QPainter, QColor

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
    BACKGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_preview.png")
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
    def _render_thumbnail(cls, settings: Settings, enforce_snapshot: bool = False) -> QImage:
        """
        Renders a thumbnail based on settings
        """
        # Create new image parts
        thumbnail: QImage = QImage(cls.BACKGROUND_IMAGE_PATH)
        foreground: QImage
        if not settings.thumbnails_enabled:
            foreground = QImage(cls.NO_FOREGROUND_IMAGE_PATH)
        elif settings.use_current_model or enforce_snapshot:
            foreground = Snapshot.snapshot(width=600, height=600)
        else:
            foreground = QImage(cls.FOREGROUND_IMAGE_PATH)

        # Combine parts
        if foreground:
            painter = QPainter(thumbnail)
            painter.drawImage(150, 160, foreground)
            painter.end()

        # End don't add options if thumbnails disabled
        if not settings.thumbnails_enabled:
            return thumbnail

        # TODO: Add options in corners

        # Return
        return thumbnail
