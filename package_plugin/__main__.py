# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

import os
import shutil
from zipfile import ZipFile

PACKAGE_PATH: str = os.path.dirname(os.path.realpath(__file__))

PLUGIN_FILES: list[str] = ["__init__.py", "elegoo_neptune_thumbnails.py", "LICENSE", "plugin.json", "README.md",
                           "changelog.txt", "img/benchy.png", "img/cross.png", "img/bg_old.png", "img/bg_new.png",
                           "tools/__init__.py", "tools/settings.py", "tools/thumbnail_generator.py", "tools/gui.qml",
                           "tools/gui.py", "tools/statistics_sender.py"]

BUILD_NAME = os.path.join(PACKAGE_PATH, "ElegooNeptuneThumbnails.curapackage")
PLUGIN_BUILD_NAME = os.path.join(PACKAGE_PATH, "ElegooNeptuneThumbnails.zip")

PACKAGE_JSON_PATH = os.path.join(PACKAGE_PATH, "package.json")

if __name__ == "__main__":
    """
    Package the plugin
    """

    # Clear old builds
    if os.path.exists(BUILD_NAME):
        os.remove(BUILD_NAME)

    # Clone base builds
    shutil.copyfile(os.path.join(PACKAGE_PATH, "base.curapackage"), BUILD_NAME)
    shutil.copyfile(os.path.join(PACKAGE_PATH, "base.zip"), PLUGIN_BUILD_NAME)

    # Add plugin files to package
    with ZipFile(BUILD_NAME, 'a') as file:
        file.write(PACKAGE_JSON_PATH, "/package.json")
        for plugin_file in PLUGIN_FILES:
            file.write(os.path.join(PACKAGE_PATH, "..", plugin_file),
                       f"/files/plugins/ElegooNeptune3Thumbnails/{plugin_file}")

    # Add plugin files to plugin (ultimaker upload)
    with ZipFile(PLUGIN_BUILD_NAME, 'a') as file:
        for plugin_file in PLUGIN_FILES:
            file.write(os.path.join(PACKAGE_PATH, "..", plugin_file),
                       f"/ElegooNeptune3Thumbnails/{plugin_file}")
