# Copyright (c) 2023 Molodos
# Copyright (c) 2023 sigathi
# Copyright (c) 2020 DhanOS
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import json
import math
import os
import uuid
from array import array
from ctypes import *
from os import path
from typing import Any

import requests
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QFont, QColor

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Platform import Platform
from UM.Scene.Scene import Scene
from cura.Snapshot import Snapshot


class ElegooNeptune3Thumbnails(Extension):
    """
    Main class of the extension
    """

    colors: dict[str, QColor] = {
        "green": QColor(34, 236, 128),
        "red": QColor(209, 76, 81),
        "yellow": QColor(251, 226, 0),
        "white": QColor(255, 255, 255),
        "bg_dark": QColor(30, 36, 52),
        "bg_light": QColor(46, 54, 75),
        "bg_thumbnail": QColor(48, 57, 79),
        "own_gray": QColor(200, 200, 200)
    }
    thumbnail_bg_path: str = path.join(path.dirname(path.realpath(__file__)), "bg_thumbnail.png")
    statistics_id_path: str = path.join(path.dirname(path.realpath(__file__)), "statistics_id.json")
    plugin_json_path: str = path.join(path.dirname(path.realpath(__file__)), "plugin.json")

    def __init__(self):
        """
        Initializer of the extension
        """
        super().__init__()

        # Add a hook when a G-gode is about to be written to a file
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self.add_snapshot_to_gcode)

        # Get a scene handler fo late usage
        self.scene: Scene = Application.getInstance().getController().getScene()

        # Generate if for anonymous statistics
        self.statistics_id: str = self.generate_statistics_id()

        # Read plugin json
        with open(self.plugin_json_path, "r") as file:
            self.plugin_json: dict[str, Any] = json.load(file)

    @classmethod
    def generate_statistics_id(cls) -> str:
        """
        Generates an id for anonymous statistics
        """
        # Generate if not exists
        if not path.exists(cls.statistics_id_path):
            random_id: str = str(uuid.uuid4())
            with open(cls.statistics_id_path, "w") as file:
                file.write(json.dumps(
                    {
                        "statistics_id": random_id
                    },
                    indent=4
                ))

        # Read and return
        try:
            with open(cls.statistics_id_path, "r") as file:
                stats: dict[str, str] = json.load(file)
                return stats.get("statistics_id", "unknown")
        except Exception as e:
            return "unknown"

    def add_snapshot_to_gcode(self, output_device) -> None:
        """
        Hook triggered on G-code write to file
        """

        # Return if there is no G-code
        if not hasattr(self.scene, "gcode_dict") or not self.scene.gcode_dict:
            Logger.log("w", "Scene does not contain any gcode")
            return

        # Enumerate G-code objects
        for build_plate_number, g_code_segments in self.scene.gcode_dict.items():

            # Info
            thumbnail_present: bool = False

            # Set commands
            disable_statistics: bool = False
            include_thumbnail: bool = False
            include_options: dict[str, int] = {}

            # Params G-code
            params_needed: list[str] = ["flavor", "time", "filament used", "layer height", "minx", "miny", "minz",
                                        "maxx", "maxy", "maxz"]
            params_g_code: str = ""

            for g_code in g_code_segments:  # List of G-code segments

                # Check it this is the params G-code segment
                added: bool = False
                for param_needed in params_needed:
                    if param_needed in g_code.lower():

                        # Add once
                        if not added:
                            params_g_code += f"\n{g_code}"
                            added = True

                        # Remove needed params from list for efficiency
                        params_needed.remove(param_needed)

                # Check for info
                if ';gimage' in g_code:
                    thumbnail_present = True

                # Check for options
                if ';includeThumbnail' in g_code:
                    include_thumbnail = True
                if ';disableStatistics' in g_code:
                    disable_statistics = True
                if ';includeTimeEstimate' in g_code:
                    include_options["includeTimeEstimate"] = g_code.index(";includeTimeEstimate")
                if ';includeFilamentMetersEstimate' in g_code:
                    include_options["includeFilamentMetersEstimate"] = g_code.index(";includeFilamentMetersEstimate")
                if ';includeFilamentGramsEstimate' in g_code:
                    include_options["includeFilamentGramsEstimate"] = g_code.index(";includeFilamentGramsEstimate")
                if ';includeLayerHeight' in g_code:
                    include_options["includeLayerHeight"] = g_code.index(";includeLayerHeight")
                if ';includeModelHeight' in g_code:
                    include_options["includeModelHeight"] = g_code.index(";includeModelHeight")

            # Cancel if thumbnail already present
            if thumbnail_present:
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
                'filament used':' 2.02409m',
                'layer height': ' 0.2',
                'minx': '86.84',
                'miny': '101.226',
                'minz': '0.2',
                'maxx': '140.428',
                'maxy': '130.771',
                'maxz': '33'
            }
            """

            # Print info
            Logger.log("d", f"Plugin version is {self.plugin_json['version']}")

            # Parse params
            minutes: int = math.floor(int(g_code_params["time"]) / 60)
            est_time: str = f"⧖ {minutes // 60}:{minutes % 60:02d}h"
            Logger.log("d", f"Estimated time: {est_time}")

            filament_meters: float = float(g_code_params["filament used"][:-1])
            est_filament_meters: str = f"⬌ {round(filament_meters, 2)}m"
            est_filament_grams: str = f"⭗ {round(filament_meters * 2.98)}g"
            Logger.log("d", f"Estimated filament: {est_filament_meters}, {est_filament_grams}")

            layer_height: str = f"⧗ {g_code_params['layer height']}mm"
            Logger.log("d", f"Layer height: {layer_height}")

            model_height: str = f"⭱ {g_code_params['maxz']}mm"
            Logger.log("d", f"Model height: {model_height}")

            # Send statistics
            if not disable_statistics:

                # Collect
                options: list[str] = ["includeThumbnail"] if include_thumbnail else []
                for option, _ in sorted(include_options.items(), key=lambda item: item[1]):
                    options.append(option)
                printer: str = Application.getInstance().getMachineManager().activeMachine.definition.getId()

                # Send
                self.send_statistics(printer=printer, options=options)

            # Add encoded snapshot image if wanted (simage and gimage)
            if include_thumbnail:

                # Data
                data_lines: list[str] = []

                # Fill data
                for option, _ in sorted(include_options.items(), key=lambda item: item[1]):
                    if option == "includeTimeEstimate":
                        data_lines.append(est_time)
                    if option == "includeFilamentMetersEstimate":
                        data_lines.append(est_filament_meters)
                    if option == "includeFilamentGramsEstimate":
                        data_lines.append(est_filament_grams)
                    if option == "includeLayerHeight":
                        data_lines.append(layer_height)
                    if option == "includeModelHeight":
                        data_lines.append(model_height)

                # Take a screenshot
                screenshot: QImage = self.take_screenshot(data_lines)

                # Create the G-code for the screenshot depending on machine type
                image_gcode = ""
                machine_type = Application.getInstance().getMachineManager().activeMachine.definition.getId()
                if machine_type in ["elegoo_neptune_3_pro", "elegoo_neptune_3_plus", "elegoo_neptune_3_max",
                                    "elegoo_neptune_3pro", "elegoo_neptune_3plus", "elegoo_neptune_3max",
                                    "elegoo_neptune_4", "elegoo_neptune_4_pro", "elegoo_neptune_4pro"]:
                    # Neptune 3 Pro/Plus/Max have another thumbnail format
                    image_gcode += self.parse_screenshot_new(screenshot, 200, 200, ";gimage:")
                    image_gcode += self.parse_screenshot_new(screenshot, 160, 160, ";simage:")
                    image_gcode += "\r"
                elif machine_type != "elegoo_neptune_3" and "neptune" in machine_type:
                    # Neptune 3 is not supported for now (also not supported in Elegoo Cura)
                    image_gcode += self.parse_screenshot(screenshot, 200, 200, ";gimage:")
                    image_gcode += self.parse_screenshot(screenshot, 160, 160, ";simage:")
                    image_gcode += "\r"

                # Add image G-code to the beginning of the G-code
                self.scene.gcode_dict[0][0] = image_gcode + self.scene.gcode_dict[0][0]

    @classmethod
    def take_screenshot(cls, lines: list[str]) -> QImage:
        """
        Take a screenshot of the model
        """
        Logger.log("d", f"Taking a screenshot with text {lines}")
        screen: QImage = Snapshot.snapshot(width=600, height=600)

        # Add background
        screen = cls.add_background(screen)

        # Add text if options are set
        for i, line in enumerate(reversed(lines)):
            if i < 4:
                screen = cls.add_text(screen, line, i > 1, i % 2 == 1)

        return screen

    @classmethod
    def add_background(cls, image: QImage) -> QImage:
        """
        Adds a background to replace the transparent one
        """
        background = QImage(cls.thumbnail_bg_path)
        painter = QPainter(background)
        painter.drawImage(150, 160, image)
        painter.end()
        return background

    @classmethod
    def add_text(cls, image: QImage, line: str, top: bool, left: bool) -> QImage:
        """
        Adds text line to the image
        """
        painter = QPainter(image)
        font = QFont("Arial", 30)
        painter.setFont(font)
        painter.setPen(cls.colors["own_gray"])
        painter.drawText(30 if left else 470, 20 if top else 790, 400, 100,
                         (Qt.AlignmentFlag.AlignLeft if left else Qt.AlignmentFlag.AlignRight) +
                         Qt.AlignmentFlag.AlignVCenter, line)
        painter.end()
        return image

    @classmethod
    def parse_screenshot(cls, img, width, height, img_type) -> str:
        """
        Parse screenshot to string for old printers
        """
        result = ""
        b_image = img.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
        img_size = b_image.size()
        result += img_type
        datasize = 0
        for i in range(img_size.height()):
            for j in range(img_size.width()):
                pixel_color = b_image.pixelColor(j, i)
                r = pixel_color.red() >> 3
                g = pixel_color.green() >> 2
                b = pixel_color.blue() >> 3
                rgb = (r << 11) | (g << 5) | b
                str_hex = "%x" % rgb
                if len(str_hex) == 3:
                    str_hex = '0' + str_hex[0:3]
                elif len(str_hex) == 2:
                    str_hex = '00' + str_hex[0:2]
                elif len(str_hex) == 1:
                    str_hex = '000' + str_hex[0:1]
                if str_hex[2:4] != '':
                    result += str_hex[2:4]
                    datasize += 2
                if str_hex[0:2] != '':
                    result += str_hex[0:2]
                    datasize += 2
                if datasize >= 50:
                    datasize = 0
            # if i != img_size.height() - 1:
            result += '\rM10086 ;'
            if i == img_size.height() - 1:
                result += "\r"
        return result

    @classmethod
    def parse_screenshot_new(cls, img, width, height, img_type) -> str:
        """
        Parse screenshot to string for new printers
        """
        if Platform.isOSX():
            p_dll = CDLL(os.path.join(os.path.dirname(__file__), "libs/libColPic.dylib"))
        elif Platform.isLinux():
            p_dll = CDLL(os.path.join(os.path.dirname(__file__), "libs/libColPic.so"))
        else:
            p_dll = CDLL(os.path.join(os.path.dirname(__file__), "libs/ColPic_X64.dll"))

        result = ""
        b_image = img.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
        img_size = b_image.size()
        color16 = array('H')
        try:
            for i in range(img_size.height()):
                for j in range(img_size.width()):
                    pixel_color = b_image.pixelColor(j, i)
                    r = pixel_color.red() >> 3
                    g = pixel_color.green() >> 2
                    b = pixel_color.blue() >> 3
                    rgb = (r << 11) | (g << 5) | b
                    color16.append(rgb)

            # int ColPic_EncodeStr(U16* fromcolor16, int picw, int pich, U8* outputdata, int outputmaxtsize, int colorsmax);
            from_color16 = color16.tobytes()
            output_data = array('B', [0] * img_size.height() * img_size.width()).tobytes()
            result_int = p_dll.ColPic_EncodeStr(from_color16, img_size.height(), img_size.width(), output_data,
                                                img_size.height() * img_size.width(), 1024)

            data0 = str(output_data).replace('\\x00', '')
            data1 = data0[2:len(data0) - 2]
            each_max = 1024 - 8 - 1
            max_line = int(len(data1) / each_max)
            append_len = each_max - 3 - int(len(data1) % each_max)

            for i in range(len(data1)):
                if i == max_line * each_max:
                    result += '\r;' + img_type + data1[i]
                elif i == 0:
                    result += img_type + data1[i]
                elif i % each_max == 0:
                    result += '\r' + img_type + data1[i]
                else:
                    result += data1[i]
            result += '\r;'
            for j in range(append_len):
                result += '0'

        except Exception as e:
            Logger.log("d", "Exception == " + str(e))

        return result + '\r'

    def send_statistics(self, printer: str, options: list[str]) -> None:
        """
        Sends anonymous statistics
        """
        # Anonymous statistics target url
        target_url: str = "http://statistics.molodos.com:8090/cura"

        # Collect statistics
        statistics: dict[str, Any] = {
            "plugin": self.plugin_json["id"],
            "version": self.plugin_json["version"],
            "id": self.statistics_id,
            "printer": printer,
            "options": options
        }

        # Send statistics
        try:
            requests.post(url=target_url, json=statistics, timeout=1)
        except Exception:
            pass
