# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from array import array
from ctypes import CDLL
from os import path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter, QColor


class TestLib:
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
        "own_gray": QColor(200, 200, 200)
    }
    RGB_PATH: str = path.abspath(path.join(path.dirname(path.realpath(__file__)), "rgb_3x3.png"))

    @classmethod
    def test(cls) -> None:
        image: QImage = QImage(3, 3, QImage.Format.Format_RGBA8888)
        painter = QPainter(image)
        painter.drawImage(0, 0, QImage(cls.RGB_PATH))
        painter.end()
        parsed_data: str = cls._parse_thumbnail_new(img=image, width=30, height=30, img_type="gimage")
        print(parsed_data)

    @classmethod
    def _parse_thumbnail_new(cls, img: QImage, width: int, height: int, img_type: str) -> str:
        img_type = f";{img_type}:"

        p_dll = CDLL(path.abspath(path.join(path.dirname(__file__), "ColPic_X64.dll")))

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
            print(result_int)
            print(output_data)

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
            raise e

        return result + '\r'


if __name__ == "__main__":
    TestLib.test()
