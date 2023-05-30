# Elegoo Neptune 3 Pro/Plus/Max Thumbnails Plugin For Cura

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Cura 5 plugin for adding G-code thumbnail images for Elegoo Neptune 3 Pro/Plus/Max printers (tested for Elegoo Neptune 3
Pro)

Additional Features:

- The estimated print time can be added to the thumbnail for a better overview

> If you have some idea on how to improve the plugin, feel free to create an issue for that

<img src="images/neptune_3_pro_view.jpg" width="300">

## Installation

> TODO: Add download link (and create release)

1) Download
   the [plugin](https://github.com/Molodos/ElegooNeptune3Thumbnails/releases/latest/download/ElegooNeptune3Thumbnails.curapackage)
2) Drag the `.curapackage` file onto Cura and restart Cura

## Usage

### Possible Options

| Option                 | Description                                                                                 |
|------------------------|---------------------------------------------------------------------------------------------|
| `;includeThumbnail`    | Includes a thumbnail of the object to the gcode                                             |
| `;includeTimeEstimate` | Includes the estimated print time in the thumbnail (needs `;includeThumbnail` to be active) |

### Adding An Option

1) Open printer selection menu and choose `Manage printers` \
   <img src="images/cura_manage_printers.png" width="400">
2) Choose your Elegoo Neptune 3 Pro/Plus/Max printer and then `Machine Settings` \
   <img src="images/cura_manage_printers.png" width="400">
3) At the top of `Start G-code` add your preferred options \
   <img src="images/cura_edit_g_code.png" width="600">

## Development Guide

1) Install requirements `pip install -r requirements.txt`
2) Add `cura` folder from https://github.com/Ultimaker/Cura to base directory (needed as lib)
3) Add `UM` folder from https://github.com/Ultimaker/Uranium to base directory (needed as lib)
4) Develop
5) Create package `python -m package_plugin` (package will be
   under `packaget_plugin/ElegooNeptune3Thumbnails.curapackage`)
6) Use the `test.py` script for testing the formatting of image texts

## Contribution

This repository is based on [sigathi/ElegooN3Thumbnail](https://github.com/sigathi/ElegooN3Thumbnail) and therefore
released under the **AGPL v3** license.
