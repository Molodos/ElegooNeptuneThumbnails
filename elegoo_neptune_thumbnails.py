# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import json
from os import path

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Qt import Duration
from UM.Scene.Scene import Scene
from cura.CuraApplication import CuraApplication
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
        if not SettingsManager.get_settings().thumbnails_enabled:
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
        params_needed: list[str] = ["flavor", "time", "filament used", "layer height", "minx", "miny", "minz",
                                    "maxx", "maxy", "maxz"]
        params_g_code: str = ""

        # Go through all G-code segments and extract information
        for i, g_code in enumerate(g_code_segments):

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
            if ';gimage:' in g_code or ';simage:' in g_code:
                thumbnail_segments.append(i)

        # Remove thumbnail parts from gcode
        for i in reversed(thumbnail_segments):
            del g_code_segments[i]

        # Get params from params G-code
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
        slice_data: SliceData = SliceData(layer_height=float(g_code_params["layer height"]),
                                          time_seconds=print_time,
                                          filament_meters=material_length,
                                          filament_grams=material_weight,
                                          model_height=float(g_code_params["maxz"]),
                                          filament_cost=material_cost)

        # Add encoded snapshot image (simage and gimage)
        thumbnail_prefix: str = ThumbnailGenerator.generate_gcode_prefix(slice_data=slice_data)

        # Add image G-code to the beginning of the G-code
        self.scene.gcode_dict[0] = [thumbnail_prefix] + g_code_segments
