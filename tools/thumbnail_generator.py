# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from os import path

from PyQt6.QtGui import QImage, QPainter

from .settings import Settings


class ThumbnailGenerator:
    """
    Thumbnail generator
    """

    BACKGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_preview.png")
    FOREGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "benchy.png")
    THUMBNAIL_PREVIEW_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "thumbnail_preview.png")

    @classmethod
    def render_thumbnail(cls, settings: Settings) -> None:
        """
        Renders a thumbnail based on settings
        """
        # Create new image parts
        thumbnail = QImage(cls.BACKGROUND_IMAGE_PATH)
        foreground = QImage(cls.FOREGROUND_IMAGE_PATH)

        # Combine paths
        painter = QPainter(thumbnail)
        painter.drawImage(150, 160, foreground)
        painter.end()

        # TODO: Add options in corners

        # Save
        thumbnail.save(cls.THUMBNAIL_PREVIEW_PATH)
