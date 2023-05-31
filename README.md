# Elegoo Neptune 3 Pro/Plus/Max Thumbnails Plugin For Cura

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Cura 5 plugin for adding G-code thumbnail images for Elegoo Neptune 3 Pro/Plus/Max printers (tested for Elegoo Neptune 3
Pro)

Additional Features:

- The estimated print time can be added to thumbnail
- Add estimated filament usage in meters to thumbnail
- Add estimated filament usage in grams (for 1.75mm diameter PLA) to thumbnail
- Add layer height to thumbnail

> If you have some idea on how to improve the plugin, feel free to create an issue for that

<img src="images/neptune_3_pro_view.jpg" width="300">

## Support This Project

If you like this project, every support is welcome :D

[![Buy Me A Coffee](https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png)](https://www.buymeacoffee.com/molodos)

## Installation

> TODO: Add download link (and create release)

1) Download
   the [plugin](https://github.com/Molodos/ElegooNeptune3Thumbnails/releases/latest/download/ElegooNeptune3Thumbnails.curapackage)
2) Drag the `.curapackage` file onto Cura and restart Cura

## Usage

### Possible Options

> **Note:** A maximum of 4 options more than `;includeThumbnail` is supported. \
> The order in which you specify your options in the start G-code will also be the display
> order (`top-left` > `top-right` > `bottom-left` > `bottom-right`)

| Option                           | Description                                                                                                                        |
|----------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| `;includeThumbnail`              | Includes a thumbnail of the object to the gcode                                                                                    |
| `;includeTimeEstimate`           | Includes the estimated print time in the thumbnail (needs `;includeThumbnail` to be active)                                        |
| `;includeFilamentMetersEstimate` | Includes the estimated filament usage in meters in the thumbnail (needs `;includeThumbnail` to be active)                          |
| `;includeFilamentGramsEstimate`  | Includes the estimated filament usage in grams (for 1.75mm diameter PLA) in the thumbnail (needs `;includeThumbnail` to be active) |
| `;includeLayerHeight`            | Includes the layer height in the thumbnail (needs `;includeThumbnail` to be active)                                                |                                                                                  |

### Adding An Option

1) Open printer selection menu and choose `Manage printers` \
   <img src="images/cura_manage_printers.png" width="400">
2) Choose your Elegoo Neptune 3 Pro/Plus/Max printer and then `Machine Settings` \
   <img src="images/cura_manage_printers.png" width="400">
3) At the top of `Start G-code` add your preferred options \
   <img src="images/cura_edit_g_code.png" width="600">

## FAQ

### Does my printer support this plugin?

I am pretty sure, that the plugin cannot break anything as it just generates a comment with an encoded image in the
G-code, that a printer will only interpret if it can. So I guess just try it out

## Development Guide

1) Install requirements `pip install -r requirements.txt`
2) Add `cura` folder from https://github.com/Ultimaker/Cura to base directory (needed as lib)
3) Add `UM` folder from https://github.com/Ultimaker/Uranium to base directory (needed as lib)
4) Develop
5) Create package `python -m package_plugin` (package will be
   under `packaget_plugin/ElegooNeptune3Thumbnails.curapackage`)
6) Use the `text/test.py` script for testing the formatting of image texts

## Contribution

This repository is based on [sigathi/ElegooN3Thumbnail](https://github.com/sigathi/ElegooN3Thumbnail) and therefore
released under the **AGPL v3** license.
