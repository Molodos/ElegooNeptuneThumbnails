from .elegoo_neptune_3_thumbnails import ElegooNeptune3Thumbnails


def getMetaData():
    return {}


def register(app):
    """
    Init point: Register the extension
    """
    return {"extension": ElegooNeptune3Thumbnails()}
