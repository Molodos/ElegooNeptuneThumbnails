# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

class Settings:
    """
    Thumbnail settings
    """

    OPTIONS: dict[str, str] = {
        "nothing": "Nothing",
        "includeTimeEstimate": "Time Estimate",
        "includeFilamentGramsEstimate": "Filament Grams Estimate",
        "includeLayerHeight": "Layer Height",
        "includeModelHeight": "Model Height",
        "includeFilamentMetersEstimate": "Filament Meters Estimate"
    }
    PRINTER_MODELS: dict[str, str] = {
        "elegoo_neptune_2": "Elegoo Neptune 2",
        "elegoo_neptune_3_pro": "Elegoo Neptune 3 Pro",
        "elegoo_neptune_3_plus": "Elegoo Neptune 3 Plus",
        "elegoo_neptune_3_max": "Elegoo Neptune 3 Max"
    }

    def __init__(self):
        self.thumbnails_enabled: bool = True
        self.printer_model: int = 1
        self.corner_options: list[int] = [1, 2, 3, 4]
        self.statistics_enabled: bool = True
        self.use_current_model: bool = False
