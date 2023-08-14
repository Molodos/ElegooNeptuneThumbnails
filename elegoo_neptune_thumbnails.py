# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import json
from os import path

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Scene.Scene import Scene
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
        # Return if there is no G-code - TODO: Maybe find slicing results other than g-code in scene
        # TODO: "Application.getInstance().getMachineManager().activeMachine.definition.getId()" could also have info
        if not hasattr(self.scene, "gcode_dict") or not self.scene.gcode_dict:
            Logger.log("w", "Scene does not contain any gcode")
            return

        # Enumerate G-code objects (spoiler: only one buildplate is possible, multiple buildplates are deprecated)
        for build_plate_number, g_code_segments in self.scene.gcode_dict.items():

            # Flag for existing thumbnail
            thumbnail_present: bool = False

            # Params G-code
            params_needed: list[str] = ["flavor", "time", "filament used", "layer height", "minx", "miny", "minz",
                                        "maxx", "maxy", "maxz"]
            params_g_code: str = ""

            # Go through all G-code segments
            for g_code in g_code_segments:

                # Add to params G-code if needed params exist withing G-code segment
                added: bool = False
                for param_needed in params_needed:
                    if param_needed in g_code.lower():

                        # Add once
                        if not added:
                            params_g_code += f"\n{g_code}"
                            added = True

                        # Remove needed params from list for efficiency
                        params_needed.remove(param_needed)

                # Check if thumbnail is already present
                if ';gimage' in g_code:
                    thumbnail_present = True

            # Cancel if thumbnail already present
            if thumbnail_present:
                # TODO: Remove existing thumbnail instead cancelling (maybe thumbnail options changed)
                return

            # Send statistics if enabled
            if SettingsManager.get_settings().statistics_enabled:
                StatisticsSender.send_statistics()

            # Cancel if thumbnail is disabled
            if not SettingsManager.get_settings().thumbnails_enabled:
                return

            # Get params from G-code
            g_code_params_list: list[str] = params_g_code.splitlines()
            g_code_params: dict[str, str] = {p[1:p.index(":")].lower(): p[p.index(":") + 1:] for p in
                                             g_code_params_list if ":" in p}
            """
            Example for g_code_params:
            {
                'flavor': 'Marlin',
                'time': '2432',
                'filament used': '2.02409m',
                'layer height': '0.2',
                'minx': '86.84',
                'miny': '101.226',
                'minz': '0.2',
                'maxx': '140.428',
                'maxy': '130.771',
                'maxz': '33'
            }
            """

            # Create slice data object from g-code params
            slice_data: SliceData = SliceData(layer_height=float(g_code_params["layer height"]),
                                              time_seconds=int(g_code_params["time"]),
                                              filament_meters=float(g_code_params["filament used"][:-1]),
                                              model_height=float(g_code_params["maxz"]))

            # Add encoded snapshot image (simage and gimage)
            g_code_prefix: str = ThumbnailGenerator.generate_gcode_prefix(slice_data=slice_data)

            # Add image G-code to the beginning of the G-code
            self.scene.gcode_dict[0][0] = g_code_prefix + self.scene.gcode_dict[0][0]
