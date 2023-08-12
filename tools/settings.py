# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import json
import uuid
from os import path
from typing import Any


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
        "includeFilamentMetersEstimate": "Filament Meters Estimate",
        "includeCostEstimate": "Cost Estimate"
    }
    PRINTER_MODELS: dict[str, str] = {
        "elegoo_neptune_2": "Elegoo Neptune 2",
        "elegoo_neptune_3_pro": "Elegoo Neptune 3 Pro",
        "elegoo_neptune_3_plus": "Elegoo Neptune 3 Plus",
        "elegoo_neptune_3_max": "Elegoo Neptune 3 Max"
    }
    STATISTICS_ID_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "..", "..", "statistics_id.json")
    PLUGIN_JSON_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "plugin.json")

    def __init__(self):
        # Read stuff from files
        self.statistics_id: str = self._generate_statistics_id()
        self.plugin_json: dict[str, Any] = self._read_plugin_json()

        # Define config
        self.thumbnails_enabled: bool = True
        self.printer_model: int = 1
        self.corner_options: list[int] = [1, 2, 3, 4]
        self.statistics_enabled: bool = True
        self.use_current_model: bool = False

    def get_printer_model_id(self) -> str:
        """
        Get str id of printer model
        """
        return list(self.PRINTER_MODELS.keys())[self.printer_model]

    def get_corner_option_ids(self) -> list[str]:
        """
        Get corner option ids (str) if not "Nothing"
        """
        # Find selected options
        option_ids: list[str] = list(self.OPTIONS.keys())
        selected_options: list[str] = [option_ids[i] for i in self.corner_options if i > 0]

        # Add "includeThumbnail" if thumbnails are enabled
        if self.thumbnails_enabled:
            selected_options.insert(0, "includeThumbnail")
        return selected_options

    @classmethod
    def _read_plugin_json(cls) -> dict[str, Any]:
        """
        Read the plugin json
        """
        # Read plugin json
        with open(cls.PLUGIN_JSON_PATH, "r") as file:
            return json.load(file)

    @classmethod
    def _generate_statistics_id(cls) -> str:
        """
        Generates an id for anonymous statistics
        """
        # Generate if not exists
        if not path.exists(cls.STATISTICS_ID_PATH):
            random_id: str = str(uuid.uuid4())
            with open(cls.STATISTICS_ID_PATH, "w") as file:
                file.write(json.dumps(
                    {
                        "statistics_id": random_id
                    },
                    indent=4
                ))

        # Read and return
        try:
            with open(cls.STATISTICS_ID_PATH, "r") as file:
                stats: dict[str, str] = json.load(file)
                return stats.get("statistics_id", "unknown")
        except Exception as e:
            return "unknown"
