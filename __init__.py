# Copyright (c) 2023 - 2024 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from .elegoo_neptune_thumbnails import ElegooNeptune3Thumbnails


def getMetaData():
    return {}


def register(app):
    """
    Init point: Register the extension
    """
    return {"extension": ElegooNeptune3Thumbnails()}
