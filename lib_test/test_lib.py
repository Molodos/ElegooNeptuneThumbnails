# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from array import array
from ctypes import CDLL
from os import path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPainter


class TestLib:
    """
    Thumbnail generator
    """

    RGB_PATH: str = path.abspath(path.join(path.dirname(path.realpath(__file__)), "rgb_3x3.png"))
    BG_BLACK: str = path.abspath(path.join(path.dirname(path.realpath(__file__)), "..", "img", "bg_old.png"))

    @classmethod
    def test(cls, image_path: str, use_lib: bool) -> tuple[int, bytes]:
        image: QImage = QImage(3, 3, QImage.Format.Format_RGBA8888)
        painter = QPainter(image)
        painter.drawImage(0, 0, QImage(image_path))
        painter.end()
        if use_lib:
            return cls._parse_thumbnail_new(img=image, width=200, height=200)
        else:
            return 10, b'0123425678910'

    @classmethod
    def _parse_thumbnail_new(cls, img: QImage, width: int, height: int) -> tuple[int, bytes]:
        # Scale image
        b_image = img.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio)
        img_size = b_image.size()

        try:
            # 'H' stands for array of unsigned shorts (ushort_t*)
            color16 = array('H')

            # Encode image in array
            for y in range(img_size.height()):
                for x in range(img_size.width()):
                    # Get color at index and parse to 16bit color
                    pixel_color = b_image.pixelColor(x, y)
                    r = pixel_color.red() >> 3
                    g = pixel_color.green() >> 2
                    b = pixel_color.blue() >> 3
                    rgb = (r << 11) | (g << 5) | b

                    # Add color to array
                    color16.append(rgb)

            # Load dll
            p_dll = CDLL(path.abspath(path.join(path.dirname(__file__), "ColPic_X64.dll")))

            from_color16 = color16.tobytes()

            # 'B' stands for array of unsigned chars (uchar_t*) -> converted to fixed length bytes (pixel count)
            output_data: bytes = array('B', [0] * img_size.height() * img_size.width()).tobytes()

            # int ColPic_EncodeStr(U16* fromcolor16, int picw, int pich, U8* outputdata, int outputmaxtsize, int colorsmax);
            result_int = p_dll.ColPic_EncodeStr(from_color16, img_size.height(), img_size.width(), output_data,
                                                img_size.height() * img_size.width(), 1024)
            return result_int, output_data
        except Exception as e:
            raise e


def print_data(image_path: str, use_lib: bool) -> None:
    count, data = TestLib.test(image_path=image_path, use_lib=use_lib)
    print(f"Size: {count}")
    print(f"Data: {data[:count]}")


if __name__ == "__main__":
    print_data(image_path=TestLib.BG_BLACK, use_lib=True)
    print_data(image_path=TestLib.RGB_PATH, use_lib=True)
