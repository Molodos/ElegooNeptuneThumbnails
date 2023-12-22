# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from array import array
from ctypes import CDLL
from os import path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter

from lib_test import lib_col_pic


class TestLib:
    """
    Thumbnail generator
    """

    BG_BLACK: str = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_old.png"))
    BENCHY: str = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "img", "benchy.png"))

    @classmethod
    def test(cls, image_path: str, use_lib: bool, width: int = 200, height: int = 200, img_type: str = "gimage") -> str:
        image: QImage = QImage(3, 3, QImage.Format.Format_RGBA8888)
        painter = QPainter(image)
        painter.drawImage(0, 0, QImage(image_path))
        painter.end()
        if use_lib:
            return cls._parse_thumbnail_binary(img=image, width=width, height=height, img_type=img_type)
        else:
            return cls._parse_thumbnail_python(img=image, width=width, height=height, img_type=img_type)

    @classmethod
    def _parse_thumbnail_binary(cls, img: QImage, width: int, height: int, img_type: str) -> str:
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

    @classmethod
    def _parse_thumbnail_python(cls, img: QImage, width: int, height: int, img_type: str) -> str:
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
            raise e

        return result + '\r'


def print_data(image_path: str, use_lib: bool, width: int = 200, height: int = 200) -> None:
    data: str = TestLib.test(image_path=image_path, use_lib=use_lib, width=width, height=height)
    print(f"[{'Binary' if use_lib else 'Python'}] Image: {image_path}")
    print(f"Data: {data}")
    print()


if __name__ == "__main__":
    image: str = TestLib.BENCHY
    print_data(image_path=image, use_lib=True)
    print_data(image_path=image, use_lib=False)
