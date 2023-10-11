# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import json
import uuid
from os import path
from typing import Any, Optional

from UM.Application import Application


class Settings:
    """
    Thumbnail settings
    """

    CURA_VERSION_KEY: str = "general/last_run_version"
    OPTIONS: dict[str, str] = {
        "nothing": "Nothing",
        "time_estimate": "Time Estimate",
        "filament_grams_estimate": "Filament Grams Estimate",
        "layer_height": "Layer Height",
        "model_height": "Model Height",
        "filament_cost_estimate": "Filament Cost Estimate",
        "filament_meters_estimate": "Filament Meters Estimate"
    }
    PRINTER_MODELS: dict[str, str] = {
        "elegoo_neptune_4": "Elegoo Neptune 4",
        "elegoo_neptune_4_pro": "Elegoo Neptune 4 Pro",
        "elegoo_neptune_3_pro": "Elegoo Neptune 3 Pro",
        "elegoo_neptune_3_plus": "Elegoo Neptune 3 Plus",
        "elegoo_neptune_3_max": "Elegoo Neptune 3 Max",
        "elegoo_neptune_2": "Elegoo Neptune 2",
        "elegoo_neptune_2_s": "Elegoo Neptune 2S",
        "elegoo_neptune_2_d": "Elegoo Neptune 2D",
        "elegoo_neptune_x": "Elegoo Neptune X",
    }

    def __init__(self, statistics_id: str, plugin_json: dict[str, Any]):
        # Read stuff from params
        self.plugin_json: dict[str, Any] = plugin_json
        self.statistics_id: str = statistics_id

        # Read stuff from config
        self.cura_version: str = Application.getInstance().getPreferences().getValue(self.CURA_VERSION_KEY)
        self.printer_id: str = Application.getInstance().getMachineManager().activeMachine.definition.getId()

        # Define config
        self.thumbnails_enabled: bool = True
        self.printer_model: int = list(self.PRINTER_MODELS.keys()).index("elegoo_neptune_3_pro")
        self.corner_options: list[int] = [1, 4, 3, 5]
        self.statistics_enabled: bool = True
        self.use_current_model: bool = False
        self.klipper_thumbnails_enabled: bool = True

    def get_printer_model_id(self) -> str:
        """
        Get str id of printer model
        """
        return list(self.PRINTER_MODELS.keys())[self.printer_model]

    def _set_printer_model_id(self, printer_model_id: str) -> None:
        """
        Set printer model from string id
        """
        self.printer_model = list(self.PRINTER_MODELS.keys()).index(printer_model_id)

    def get_corner_option_ids(self) -> list[str]:
        """
        Get corner option ids (str)
        """
        # Find selected options
        option_ids: list[str] = list(self.OPTIONS.keys())
        selected_options: list[str] = [option_ids[i] for i in self.corner_options]

        # Return
        return selected_options

    def _set_corner_option_ids(self, corner_option_ids: list[str]) -> None:
        """
        Set corner options from ids
        """
        if corner_option_ids:
            option_ids: list[str] = list(self.OPTIONS.keys())
            for i, option_id in enumerate(corner_option_ids):
                self.corner_options[i] = option_ids.index(option_id)

    def is_old_thumbnail(self) -> bool:
        """
        Check if old thumbnail is required
        """
        return list(self.PRINTER_MODELS.keys())[self.printer_model] in ["elegoo_neptune_2", "elegoo_neptune_2_s",
                                                                        "elegoo_neptune_2_d", "elegoo_neptune_x"]

    def load_json(self, data: dict[str, Any]) -> None:
        """
        Load from json
        """
        self.thumbnails_enabled = data.get("thumbnails_enabled", True)
        self._set_printer_model_id(data.get("printer_model", "elegoo_neptune_3_pro"))
        self._set_corner_option_ids(data.get("corner_options", None))
        self.statistics_enabled = data.get("statistics_enabled", True)
        self.use_current_model = data.get("use_current_model", False)
        self.klipper_thumbnails_enabled = data.get("klipper_thumbnails_enabled", True)

    def to_json(self) -> dict[str, Any]:
        """
        Parse to json
        """
        return {
            "thumbnails_enabled": self.thumbnails_enabled,
            "printer_model": self.get_printer_model_id(),
            "corner_options": self.get_corner_option_ids(),
            "statistics_enabled": self.statistics_enabled,
            "use_current_model": self.use_current_model,
            "klipper_thumbnails_enabled": self.klipper_thumbnails_enabled
        }


class SettingsManager:
    """
    Thumbnail settings manager
    """

    SETTINGS_KEY: str = "elegoo_neptune_thumbnails"
    STATISTICS_ID_KEY: str = "general/statistics_id"
    PLUGIN_JSON_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "plugin.json")

    _settings: Optional[Settings] = None

    @classmethod
    def get_settings(cls) -> Settings:
        """
        Get the settings instance
        """
        if not cls._settings:
            cls.load()
        return cls._settings

    @classmethod
    def load(cls) -> None:
        """
        Load settings (also used to discard changes)
        """
        # Init settings if None
        if not cls._settings:
            cls._settings = Settings(statistics_id=cls._generate_statistics_id(), plugin_json=cls._read_plugin_json())

        # Load settings and update
        plain_data: str = Application.getInstance().getGlobalContainerStack().getMetaDataEntry(cls.SETTINGS_KEY)
        if plain_data:
            data: dict[str, Any] = json.loads(plain_data)
            cls._settings.load_json(data=data)
        else:
            # Default settings
            cls._settings.thumbnails_enabled = True
            # Neptune 3 Pro is most probable
            cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_3_pro")
            cls._settings.corner_options = [1, 4, 3, 5]
            cls._settings.statistics_enabled = True
            cls._settings.use_current_model = False
            cls._settings.klipper_thumbnails_enabled = True

            # Try to recognize current printer model
            printer_id: str = Application.getInstance().getMachineManager().activeMachine.definition.getId()
            if printer_id in ["elegoo_neptune_4"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_4")
            elif printer_id in ["elegoo_neptune_4pro", "elegoo_neptune_4_pro"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_4_pro")
            elif printer_id in ["elegoo_neptune_3pro", "elegoo_neptune_3_pro"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_3_pro")
            elif printer_id in ["elegoo_neptune_3plus", "elegoo_neptune_3_plus"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_3_plus")
            elif printer_id in ["elegoo_neptune_3max", "elegoo_neptune_3_max"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_3_max")
            elif printer_id in ["elegoo_neptune_2"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_2")
            elif printer_id in ["elegoo_neptune_2s", "elegoo_neptune_2_s"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_2_s")
            elif printer_id in ["elegoo_neptune_2d", "elegoo_neptune_2_d"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_2_d")
            elif printer_id in ["elegoo_neptune_x"]:
                cls._settings.printer_model = list(Settings.PRINTER_MODELS.keys()).index("elegoo_neptune_x")
            else:
                # Disable thumbnails if printer is not recognized (to avoid slice errors)
                cls._settings.thumbnails_enabled = False

    @classmethod
    def save(cls) -> None:
        """
        Save settings
        """
        # Init settings if None
        if not cls._settings:
            cls.load()

        # Get data and save
        data: dict[str, Any] = cls._settings.to_json()
        Application.getInstance().getGlobalContainerStack().setMetaDataEntry(cls.SETTINGS_KEY, json.dumps(data))

    @classmethod
    def _generate_statistics_id(cls) -> str:
        """
        Generates an id for anonymous statistics
        """
        # Generate if not exists
        if not Application.getInstance().getPreferences().getValue(cls.STATISTICS_ID_KEY):
            Application.getInstance().getPreferences().addPreference(cls.STATISTICS_ID_KEY, "")
            Application.getInstance().getPreferences().setValue(cls.STATISTICS_ID_KEY, str(uuid.uuid4()))
            Application.getInstance().savePreferences()

        # Read and return
        return Application.getInstance().getPreferences().getValue(cls.STATISTICS_ID_KEY)

    @classmethod
    def _read_plugin_json(cls) -> dict[str, Any]:
        """
        Read the plugin json
        """
        # Read plugin json
        with open(cls.PLUGIN_JSON_PATH, "r") as file:
            return json.load(file)
