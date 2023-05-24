import os
from array import array
from ctypes import *

from PyQt6.QtCore import Qt

from UM.Application import Application
from UM.Extension import Extension
from UM.Logger import Logger
from UM.Platform import Platform
from cura.CuraApplication import CuraApplication
from cura.Snapshot import Snapshot


class ElegooN3Thumbnail(Extension):
    """
    Main class of the extension
    """

    def __init__(self):
        """
        Initializer of the extension
        """
        super().__init__()

        # Add a hook when a G-gode is about to be written to a file
        Application.getInstance().getOutputDeviceManager().writeStarted.connect(self.add_snapshot_to_gcode)

        # Get a scene handler fo late usage
        self.scene = Application.getInstance().getController().getScene()

    def add_snapshot_to_gcode(self, output_device) -> None:
        """
        Hook triggered on G-code write to file
        """

        # Return if there is no G-code
        if not hasattr(self.scene, "gcode_dict") or not self.scene.gcode_dict:
            Logger.log("w", "Scene does not contain any gcode")
            return

        # Enumerate G-code objects
        for build_plate_number, gcode_list in self.scene.gcode_dict.items():
            for index, g_code in enumerate(gcode_list):

                # If there is ";includeThumbnail" anywhere, add encoded snapshot image (simage and gimage)
                if ';includeThumbnail' in g_code:

                    # Take a screenshot
                    screenshot = self.take_screenshot()

                    # Add estimated print time if it should be added
                    if ';includeTimeEstimate' in g_code:
                        pass  # TODO

                    # Create the G-code for the screenshot depending on machine type
                    image_gcode = ""
                    machine_type = Application.getInstance().getMachineManager().activeMachine.definition.getId()
                    if machine_type in ["elegoo_neptune_3_pro", "elegoo_neptune_3_plus", "elegoo_neptune_3_max",
                                        "elegoo_neptune_3pro", "elegoo_neptune_3plus", "elegoo_neptune_3max"]:
                        image_gcode += self.parse_screenshot_new(screenshot, 200, 200, ";gimage:")
                        image_gcode += self.parse_screenshot_new(screenshot, 160, 160, ";simage:")
                        image_gcode += "\r"
                    elif machine_type != "elegoo_neptune_3":
                        image_gcode += self.parse_screenshot(screenshot, 200, 200, ";gimage:")
                        image_gcode += self.parse_screenshot(screenshot, 160, 160, ";simage:")
                        image_gcode += "\r"

                    # Add image G-code to the beginning of the G-code
                    self.scene.gcode_dict[0][0] = image_gcode + self.scene.gcode_dict[0][0]

    @classmethod
    def take_screenshot(cls):
        """
        Take a screenshot of the model
        """
        cut_image = Snapshot.snapshot(width=900, height=900)
        return cut_image

    @classmethod
    def parse_screenshot(cls, img, width, height, img_type) -> str:
        """
        Parse screenshot to string for old printers
        """
        Logger.log("d",
                   "add_screenshot." + CuraApplication.getInstance().getMachineManager().activeMachine.definition.id)
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
        Logger.log("d",
                   "add_screenshot_new." + CuraApplication.getInstance().getMachineManager().activeMachine.definition.id)
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
