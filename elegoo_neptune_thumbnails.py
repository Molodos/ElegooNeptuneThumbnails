# Copyright (c) 2023 - 2024 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import json
from os import path
from typing import Optional

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Qt import Duration
from UM.Scene.Scene import Scene
from cura.CuraApplication import CuraApplication
from cura.Settings.ExtruderStack import ExtruderStack
from cura.UI.PrintInformation import PrintInformation
from .tools import SettingsManager, StatisticsSender, GUIManager, SliceData, ThumbnailGenerator


class ElegooNeptune3Thumbnails(Extension):
    """
    Main class of the extension
    """

    PLUGIN_JSON_PATH: str = path.join(path.dirname(path.realpath(__file__)), "plugin.json")

    def __init__(self) -> None:
        """
        Initializer of the extension
        """
        # Init super objects
        Extension.__init__(self)

        # Create GUI stuff
        self._gui: GUIManager = GUIManager(extension=self)

        # Add a hook when G-gode is about to be written to a file -> add thumbnail
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self.add_snapshot_to_gcode)

        # Add a hook when the selected printer changes -> load settings
        Application.getInstance().globalContainerStackChanged.connect(self.printer_switched)

        # Init popup on load to keep popup open time low
        CuraApplication.getInstance().mainWindowChanged.connect(self._gui.init_gui)

        # Get a scene handler for later usage
        self.scene: Scene = Application.getInstance().getController().getScene()

        # Read plugin version
        with open(self.PLUGIN_JSON_PATH, "r") as file:
            self.plugin_version: str = json.load(file)["version"]

    @classmethod
    def printer_switched(cls) -> None:
        """
        Hook triggered on printer switch (also triggered on startup)
        """
        SettingsManager.load()

    def add_snapshot_to_gcode(self, output_device) -> None:
        """
        Hook triggered on G-code write to file
        """
        # Send statistics if enabled
        if SettingsManager.get_settings().statistics_enabled:
            StatisticsSender.send_statistics()

        # Cancel if thumbnail is disabled
        if not SettingsManager.get_settings().thumbnails_enabled and not SettingsManager.get_settings().klipper_thumbnails_enabled:
            return

        # Return if there is no G-code
        if not hasattr(self.scene, "gcode_dict") or not self.scene.gcode_dict:
            Logger.log("w", "Scene does not contain any gcode")
            return

        # Only get first build plate (spoiler: there is only one possible, multiple buildplates are deprecated)
        g_code_segments: list[str] = self.scene.gcode_dict[0]

        # Flag for existing thumbnail
        thumbnail_segments: list[int] = []

        # Params G-code
        g_code_params: dict[str, Optional[str]] = {}
        """
        Example for g_code_params:
        {
            'flavor': 'Marlin',
            'time': '2432',
            'filament_used': '2.02409m',
            'layer_height': '0.2',
            'minx': '86.84',
            'miny': '101.226',
            'minz': '0.2',
            'maxx': '140.428',
            'maxy': '130.771',
            'maxz': '33',
            'machine_name': 'ELEGOO NEPTUNE 4 Pro',
        }
        """

        # Param mappings
        param_mappings: dict[str, dict[str, str]] = {
            "elegoo": {
                "flavor": "flavor",
                "time": "time",
                "filament used": "filament_used",
                "layer height": "layer_height",
                "minx": "minx",
                "miny": "miny",
                "minz": "minz",
                "maxx": "maxx",
                "maxy": "maxy",
                "maxz": "maxz",
                "target_machine.name": "machine_name",
            },
            "ultimaker": {
                "flavor": "flavor",
                "print.time": "time",
                "print.size.min.x": "minx",
                "print.size.min.y": "miny",
                "print.size.min.z": "minz",
                "print.size.max.x": "maxx",
                "print.size.max.y": "maxy",
                "print.size.max.z": "maxz",
                "target_machine.name": "machine_name",
            }
        }

        # Go through all G-code segments and extract information
        for i, g_code in enumerate(g_code_segments):

            # Go through segment lines and extract parameters from mapping
            for line in g_code.splitlines():
                for param_mapping in param_mappings.values():
                    for key, mapping in param_mapping.items():
                        prefix: str = f";{key}:"
                        if line.lower().startswith(prefix):
                            value: str = line[len(prefix):]
                            g_code_params[mapping] = value

            # Check if thumbnail is already present
            if SettingsManager.get_settings().thumbnails_enabled and (";gimage:" in g_code or ";simage:" in g_code):
                thumbnail_segments.append(i)
            elif SettingsManager.get_settings().klipper_thumbnails_enabled and "; thumbnail begin " in g_code:
                thumbnail_segments.append(i)

            # Find end of head to break
            if ";Generated with Cura_SteamEngine" in g_code:
                break

        # Remove thumbnail parts from gcode
        for i in reversed(thumbnail_segments):
            del g_code_segments[i]

        # Get extruder line width
        extruders: list[ExtruderStack] = Application.getInstance().getGlobalContainerStack().extruderList
        extruder: ExtruderStack = extruders[0]
        line_width = extruder.getProperty("line_width", "value")

        # Get more print information (independent of gcode)
        print_info: PrintInformation = CuraApplication.getInstance().getPrintInformation()
        print_time_duration: Duration = print_info.currentPrintTime
        print_time: int = (((print_time_duration.days * 24) + print_time_duration.hours) * 60
                           + print_time_duration.minutes) * 60 + print_time_duration.seconds
        material_length: float = print_info.materialLengths[0]
        material_cost: float = print_info.materialCosts[0]
        material_weight: float = print_info.materialWeights[0]
        # TODO: Find Model height and layer height independent of gcode (but not from settings because they could change between slice and save)

        # Create slice data object from g-code params and print information (prioritized)
        slice_data: SliceData = SliceData(layer_height=float(g_code_params.get("layer_height", "-1.0")),
                                          time_seconds=print_time,
                                          filament_meters=material_length,
                                          filament_grams=material_weight,
                                          model_height=float(g_code_params.get("maxz", "-1.0")),
                                          filament_cost=material_cost,
                                          line_width=line_width)

        # Clear gcode
        self.scene.gcode_dict[0] = []

        # Add thumbnail if enabled
        if SettingsManager.get_settings().thumbnails_enabled:
            thumbnail_prefix: str = ThumbnailGenerator.generate_gcode_prefix(slice_data=slice_data)
            self.scene.gcode_dict[0].append(thumbnail_prefix)

        # Add klipper thumbnails if enabled
        if SettingsManager.get_settings().klipper_thumbnails_enabled:
            klipper_thumbnail_prefix: str = ThumbnailGenerator.generate_klipper_thumbnail_gcode(slice_data=slice_data)
            self.scene.gcode_dict[0].append(klipper_thumbnail_prefix)

        # Add original gcode
        self.scene.gcode_dict[0] += g_code_segments
