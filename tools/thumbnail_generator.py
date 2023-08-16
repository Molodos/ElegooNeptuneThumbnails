# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import math
from array import array
from ctypes import CDLL
from os import path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QColor, QFont

from UM.Application import Application
from UM.Logger import Logger
from UM.Platform import Platform
from cura.Snapshot import Snapshot
from .settings import SettingsManager


class SliceData:
    """
    Result data from slicing
    """

    def __init__(self, layer_height: float = 0.2, time_seconds: int = 3960, filament_meters: float = 3.9,
                 filament_grams: float = 11.6, model_height: float = 48.0, filament_cost: float = 0.25):
        self.layer_height: float = layer_height
        self.time_seconds: int = time_seconds
        self.filament_meters: float = filament_meters
        self.filament_grams: float = filament_grams
        self.model_height: float = model_height
        self.filament_cost: float = filament_cost


class ThumbnailGenerator:
    """
    Thumbnail generator
    """

    COLORS: dict[str, QColor] = {
        "green": QColor(34, 236, 128),
        "red": QColor(209, 76, 81),
        "yellow": QColor(251, 226, 0),
        "white": QColor(255, 255, 255),
        "bg_dark": QColor(30, 36, 52),
        "bg_light": QColor(46, 54, 75),
        "bg_thumbnail": QColor(48, 57, 79),
        "own_gray": QColor(200, 200, 200)
    }
    BACKGROUND_OLD_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_old.png")
    BACKGROUND_NEW_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_new.png")
    FOREGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "benchy.png")
    NO_FOREGROUND_IMAGE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "cross.png")
    THUMBNAIL_PREVIEW_PATH: str = path.join(path.dirname(path.realpath(__file__)), "..", "img", "thumbnail_preview.png")
    CURRENCY_PREFERENCE: str = "cura/currency"

    @classmethod
    def generate_preview(cls) -> None:
        """
        Generate a preview image based on settings
        """
        thumbnail: QImage = cls._render_thumbnail(is_preview=True, slice_data=SliceData())
        thumbnail.save(cls.THUMBNAIL_PREVIEW_PATH)

    @classmethod
    def generate_gcode_prefix(cls, slice_data: SliceData) -> str:
        """
        Generate a g-code prefix string based on settings
        """
        # Generate thumbnail
        thumbnail: QImage = cls._render_thumbnail(is_preview=False, slice_data=slice_data)

        # Parse to g-code prefix
        gcode_prefix: str = ""
        if SettingsManager.get_settings().is_old_thumbnail():
            gcode_prefix += cls._parse_thumbnail_old(thumbnail, 200, 200, "gimage")
            gcode_prefix += cls._parse_thumbnail_old(thumbnail, 160, 160, "simage")
        else:
            gcode_prefix += cls._parse_thumbnail_new(thumbnail, 200, 200, "gimage")
            gcode_prefix += cls._parse_thumbnail_new(thumbnail, 160, 160, "simage")
        gcode_prefix += "\r"

        # Return
        return gcode_prefix

    @classmethod
    def _render_thumbnail(cls, slice_data: SliceData, is_preview: bool = True) -> QImage:
        """
        Renders a thumbnail based on settings
        """
        # Create background
        background: QImage
        if SettingsManager.get_settings().is_old_thumbnail():
            background = QImage(cls.BACKGROUND_OLD_PATH)
        else:
            background = QImage(cls.BACKGROUND_NEW_PATH)

        # Create foreground
        foreground: QImage
        if not SettingsManager.get_settings().thumbnails_enabled:
            foreground = QImage(cls.NO_FOREGROUND_IMAGE_PATH)
        elif SettingsManager.get_settings().use_current_model or not is_preview:
            foreground = Snapshot.snapshot(width=600, height=600)
        else:
            foreground = QImage(cls.FOREGROUND_IMAGE_PATH)

        # Paint foreground on background
        if foreground:
            painter = QPainter(background)
            painter.drawImage(150, 160, foreground)
            painter.end()

        # Don't add options if thumbnails disabled
        if not SettingsManager.get_settings().thumbnails_enabled:
            return background

        # Generate option lines
        lines: list[str] = cls._generate_option_lines(slice_data=slice_data)

        # Add options
        painter = QPainter(background)
        font = QFont("Arial", 30)
        painter.setFont(font)
        painter.setPen(cls.COLORS["own_gray"])
        for i, line in enumerate(lines):
            if line:
                left: bool = i % 2 == 0
                top: bool = i < 2
                painter.drawText(30 if left else 470,
                                 20 if top else 790, 400, 100,
                                 (Qt.AlignmentFlag.AlignLeft if left else Qt.AlignmentFlag.AlignRight) +
                                 Qt.AlignmentFlag.AlignVCenter, line)
        painter.end()

        # Return
        return background

    @classmethod
    def _generate_option_lines(cls, slice_data: SliceData) -> list[str]:
        """
        Generate the texts for the corners from settings
        """
        lines: list[str] = []
        for i in SettingsManager.get_settings().corner_options:
            option: str = list(SettingsManager.get_settings().OPTIONS.keys())[i]
            if option == "nothing":
                lines.append("")
            elif option == "time_estimate":
                time_minutes: int = math.floor(slice_data.time_seconds / 60)
                lines.append(f"⧖ {time_minutes // 60}:{time_minutes % 60:02d}h")
            elif option == "filament_grams_estimate":
                lines.append(f"⭗ {round(slice_data.filament_grams)}g")
            elif option == "layer_height":
                lines.append(f"⧗ {round(slice_data.layer_height, 2)}mm")
            elif option == "model_height":
                lines.append(f"⭱ {round(slice_data.model_height, 2)}mm")
            elif option == "filament_cost_estimate":
                currency: str = Application.getInstance().getPreferences().getValue(cls.CURRENCY_PREFERENCE)
                lines.append(f"⛁ {round(slice_data.filament_cost, 2)}{currency}")
            elif option == "filament_meters_estimate":
                lines.append(f"⬌ {round(slice_data.filament_meters, 2):.02f}m")
        return lines

    @classmethod
    def _parse_thumbnail_old(cls, img: QImage, width: int, height: int, img_type: str) -> str:
        """
        Parse thumbnail to string for old printers
        TODO: Maybe optimize at some time
        """
        img_type = f";{img_type}:"
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
    def _parse_thumbnail_new(cls, img: QImage, width: int, height: int, img_type: str) -> str:
        """
        Parse thumbnail to string for new printers
        TODO: Maybe optimize at some time
        """
        img_type = f";{img_type}:"
        if Platform.isOSX():
            p_dll = CDLL(path.join(path.dirname(__file__), "..", "libs", "libColPic.dylib"))
        elif Platform.isLinux():
            p_dll = CDLL(path.join(path.dirname(__file__), "..", "libs", "libColPic.so"))
        else:
            p_dll = CDLL(path.join(path.dirname(__file__), "..", "libs", "ColPic_X64.dll"))

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
