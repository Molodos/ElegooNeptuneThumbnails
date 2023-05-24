from . import ElegooN3Thumbnail


def getMetaData():
    return {}


def register(app):
    """
    Init point: Register the extension
    """
    return {"extension": ElegooN3Thumbnail.ElegooN3Thumbnail()}
