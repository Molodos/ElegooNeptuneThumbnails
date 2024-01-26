# Copyright (c) 2023 - 2024 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import math
from array import array
from os import path

from PyQt6.QtCore import Qt, QByteArray, QBuffer, QIODeviceBase
from PyQt6.QtGui import QImage, QPainter, QColor, QFont

from UM.Application import Application
from UM.Logger import Logger
from cura.Snapshot import Snapshot
from . import lib_col_pic
from .settings import SettingsManager


class SliceData:
    """
    Result data from slicing
    """

    def __init__(self, layer_height: float = 0.2, time_seconds: int = 3960, filament_meters: float = 3.9,
                 filament_grams: float = 11.6, model_height: float = 48.0, filament_cost: float = 0.25,
                 line_width: float = 0.4):
        self.layer_height: float = layer_height
        self.time_seconds: int = time_seconds
        self.filament_meters: float = filament_meters
        self.filament_grams: float = filament_grams
        self.model_height: float = model_height
        self.filament_cost: float = filament_cost
        self.line_width: float = line_width


class ThumbnailGenerator:
    """
    Thumbnail generator
    """

    KLIPPER_THUMBNAIL_BLOCK_SIZE: int = 78
    COLORS: dict[str, QColor] = {
        "green": QColor(34, 236, 128),
        "red": QColor(209, 76, 81),
        "yellow": QColor(251, 226, 0),
        "white": QColor(255, 255, 255),
        "bg_dark": QColor(30, 36, 52),
        "bg_light": QColor(46, 54, 75),
        "bg_thumbnail": QColor(48, 57, 79),
        "own_gray": QColor(200, 200, 200),
        "darker_gray": QColor(63, 63, 63)
    }
    BACKGROUND_OLD_PATH: str = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_old.png"))
    BACKGROUND_NEW_PATH: str = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_new.png"))
    BACKGROUND_ARTILLERY_PATH: str = path.abspath(
        path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_artillery.png"))
    BACKGROUND_ORANGESTORM_PATH: str = path.abspath(
        path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_orangestorm.png"))
    FOREGROUND_IMAGE_PATH: str = path.abspath(
        path.join(path.dirname(path.realpath(__file__)), "..", "img", "benchy.png"))
    NO_FOREGROUND_IMAGE_PATH: str = path.abspath(
        path.join(path.dirname(path.realpath(__file__)), "..", "img", "cross.png"))
    THUMBNAIL_PREVIEW_PATH: str = path.abspath(
        path.join(path.dirname(path.realpath(__file__)), "..", "img", "thumbnail_preview.png"))
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
        if SettingsManager.get_settings().is_elegoo_printer():
            if SettingsManager.get_settings().is_old_thumbnail():
                gcode_prefix += cls._parse_thumbnail_old(thumbnail, 100, 100, "simage")
                gcode_prefix += cls._parse_thumbnail_old(thumbnail, 200, 200, ";gimage")
            elif SettingsManager.get_settings().is_b64jpg_thumbnail():
                gcode_prefix += cls._parse_thumbnail_b64jpg(thumbnail, 400, 400, "gimage")
                gcode_prefix += cls._parse_thumbnail_b64jpg(thumbnail, 114, 114, "simage")
            else:
                gcode_prefix += cls._parse_thumbnail_new(thumbnail, 200, 200, "gimage")
                gcode_prefix += cls._parse_thumbnail_new(thumbnail, 160, 160, "simage")
        elif SettingsManager.get_settings().is_artillery_printer():
            gcode_prefix += cls._parse_thumbnail_new(thumbnail, 85, 85, "simage")
            gcode_prefix += cls._parse_thumbnail_new(thumbnail, 230, 230, "gimage")
            gcode_prefix += cls._parse_thumbnail_new(thumbnail, 170, 170, "mimage")
        gcode_prefix += f";Thumbnail generated by the {SettingsManager.get_settings().plugin_json['name']} plugin version {SettingsManager.get_settings().plugin_json['version']} (https://github.com/Molodos/ElegooNeptuneThumbnails)\r\r"

        # Return
        return gcode_prefix

    @classmethod
    def generate_klipper_thumbnail_gcode(cls, slice_data: SliceData) -> str:
        """
        Generate klipper thumbnail gcode for thumbnails in sizes 32x32 and 300x300
        """
        small_icon: QImage = Snapshot.snapshot(width=32, height=32)
        big_icon: QImage = cls._render_thumbnail(slice_data=slice_data, is_preview=False, add_background=False)
        big_icon = big_icon.scaled(300, 300)
        g_code: str = "\r"
        for icon in [small_icon, big_icon]:
            byte_array: QByteArray = QByteArray()
            byte_buffer: QBuffer = QBuffer(byte_array)
            byte_buffer.open(QIODeviceBase.OpenModeFlag.WriteOnly)
            icon.save(byte_buffer, "PNG")
            base64_string: str = str(byte_array.toBase64().data(), "UTF-8")
            g_code += f"; thumbnail begin {icon.width()} {icon.height()} {len(base64_string)}\r"
            while base64_string:
                g_code += f"; {base64_string[0:cls.KLIPPER_THUMBNAIL_BLOCK_SIZE]}\r"
                base64_string = base64_string[cls.KLIPPER_THUMBNAIL_BLOCK_SIZE:]
            g_code += "; thumbnail end\r\r"
        return g_code

    @classmethod
    def _render_thumbnail(cls, slice_data: SliceData, is_preview: bool = True, add_background: bool = True) -> QImage:
        """
        Renders a thumbnail based on settings
        """
        # Create background
        is_light_background: bool = False
        background: QImage = QImage(900, 900, QImage.Format.Format_RGBA8888)
        if add_background:
            if SettingsManager.get_settings().is_old_thumbnail():
                painter = QPainter(background)
                painter.drawImage(0, 0, QImage(cls.BACKGROUND_OLD_PATH))
                painter.end()
            elif SettingsManager.get_settings().is_b64jpg_thumbnail():
                is_light_background = True
                painter = QPainter(background)
                painter.drawImage(0, 0, QImage(cls.BACKGROUND_ORANGESTORM_PATH))
                painter.end()
            elif SettingsManager.get_settings().is_artillery_printer():
                painter = QPainter(background)
                painter.drawImage(0, 0, QImage(cls.BACKGROUND_ARTILLERY_PATH))
                painter.end()
            else:
                painter = QPainter(background)
                painter.drawImage(0, 0, QImage(cls.BACKGROUND_NEW_PATH))
                painter.end()

        # Create foreground
        foreground: QImage
        if not SettingsManager.get_settings().thumbnails_enabled and not SettingsManager.get_settings().klipper_thumbnails_enabled:
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
        if not SettingsManager.get_settings().thumbnails_enabled and not SettingsManager.get_settings().klipper_thumbnails_enabled:
            return background

        # Generate option lines
        lines: list[str] = cls._generate_option_lines(slice_data=slice_data)

        # Add options
        painter = QPainter(background)
        font = QFont("Arial", 60)
        painter.setFont(font)
        if is_light_background:
            painter.setPen(cls.COLORS["darker_gray"])
        else:
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
                if slice_data.layer_height < 0:
                    lines.append(f"⧗ N/A")
                else:
                    lines.append(f"⧗ {round(slice_data.layer_height, 2)}mm")
            elif option == "model_height":
                if slice_data.model_height < 0:
                    lines.append(f"⭱ N/A")
                else:
                    lines.append(f"⭱ {round(slice_data.model_height, 2)}mm")
            elif option == "filament_cost_estimate":
                currency: str = Application.getInstance().getPreferences().getValue(cls.CURRENCY_PREFERENCE)
                lines.append(f"⛁ {round(slice_data.filament_cost, 2):.02f}{currency}")
            elif option == "filament_meters_estimate":
                lines.append(f"⬌ {round(slice_data.filament_meters, 2):.02f}m")
            elif option == "line_width":
                lines.append(f"◯ {round(slice_data.line_width, 2):.02f}mm")
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
            output_data = bytearray(img_size.height() * img_size.width() * 10)
            result_int = lib_col_pic.ColPic_EncodeStr(color16, img_size.height(), img_size.width(), output_data,
                                                      img_size.height() * img_size.width() * 10, 1024)

            data0 = str(output_data).replace('\\x00', '')
            data1 = data0[2:len(data0) - 2]
            each_max = 1024 - 8 - 1
            max_line = int(len(data1) / each_max)
            append_len = each_max - 3 - int(len(data1) % each_max) + 10
            j = 0
            for i in range(len(output_data)):
                if output_data[i] != 0:
                    if j == max_line * each_max:
                        result += '\r;' + img_type + chr(output_data[i])
                    elif j == 0:
                        result += img_type + chr(output_data[i])
                    elif j % each_max == 0:
                        result += '\r' + img_type + chr(output_data[i])
                    else:
                        result += chr(output_data[i])
                    j += 1
            result += '\r;'
            for m in range(append_len):
                result += '0'

        except Exception as e:
            Logger.log("d", "Exception == " + str(e))

        return result + '\r'

    @classmethod
    def _parse_thumbnail_b64jpg(cls, img: QImage, width: int, height: int, img_type: str) -> str:
        """
        Parse thumbnail to string for new printers
        TODO: Maybe optimize at some time
        """
        img_type = f";{img_type}:"

        result = ""
        b_image = img.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)

        try:
            byte_array: QByteArray = QByteArray()
            byte_buffer: QBuffer = QBuffer(byte_array)
            byte_buffer.open(QIODeviceBase.OpenModeFlag.WriteOnly)
            b_image.save(byte_buffer, "JPEG")
            base64_string: str = str(byte_array.toBase64().data(), "UTF-8")

            each_max = 1024 - 8 - 1
            max_line = int(len(base64_string) / each_max)

            for i in range(len(base64_string)):
                if i == max_line * each_max:
                    result += '\r;' + img_type + base64_string[i]
                elif i == 0:
                    result += img_type + base64_string[i]
                elif i % each_max == 0:
                    result += '\r' + img_type + base64_string[i]
                else:
                    result += base64_string[i]

        except Exception as e:
            Logger.log("d", "Exception == " + str(e))

        return result + '\r'
