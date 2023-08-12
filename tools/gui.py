# Copyright (c) 2023 Molodos
# The ElegooNeptuneThumbnails plugin is released under the terms of the AGPLv3 or higher.

from os import path
from typing import Optional

from PyQt6.QtCore import QObject, pyqtSlot, pyqtProperty
from PyQt6.QtQuick import QQuickItem, QQuickWindow

from UM.Extension import Extension
from UM.Logger import Logger
from cura.CuraApplication import CuraApplication
from .settings import Settings
from .thumbnail_generator import ThumbnailGenerator


class SettingsManager(QObject):
    """
    Settings manager (integration between python code and gui)
    """

    THUMBNAIL_PREVIEW_PATH: str = "../img/thumbnail_preview.png"

    def __init__(self, settings: Settings):
        QObject.__init__(self)
        self._settings: Settings = settings

        self._thumbnail: Optional[QQuickItem] = None
        self._selected_corner: int = -1

    def set_thumbnail_ref(self, thumbnail: QQuickItem) -> None:
        """
        Set the thumbnail ref for updates
        """
        self._thumbnail = thumbnail
        self.render_thumbnail()

    def render_thumbnail(self) -> None:
        """
        Render a thumbnail image form settings (needs to be called on settings change)
        """
        ThumbnailGenerator.render_preview(settings=self._settings)
        if self._thumbnail:
            self._thumbnail.setProperty("source", "")
            self._thumbnail.setProperty("source", "../img/thumbnail_preview.png")

    # Thumbnails enabled state

    @pyqtProperty(bool)
    def thumbnails_enabled(self) -> bool:
        return self._settings.thumbnails_enabled

    @pyqtSlot(bool)
    def set_thumbnails_enabled(self, enabled: bool) -> None:
        self._settings.thumbnails_enabled = enabled
        self.render_thumbnail()  # Update preview

    # Printer dropdown

    @pyqtProperty(list)  # List must be untyped!
    def printer_model_list(self) -> list[str]:
        return list(self._settings.PRINTER_MODELS.values())

    @pyqtSlot(int)
    def select_printer_model(self, model: int) -> None:
        self._settings.printer_model = model

    @pyqtProperty(int)
    def selected_printer_model(self) -> int:
        return self._settings.printer_model

    # Options dropdowns

    @pyqtProperty(list)  # List must be untyped!
    def option_list(self) -> list[str]:
        return list(self._settings.OPTIONS.values())

    @pyqtSlot(int)
    def select_corner(self, corner: int) -> None:
        self._selected_corner = corner

    @pyqtProperty(int)
    def selected_corner_option(self) -> int:
        return self._settings.corner_options[self._selected_corner]

    @pyqtSlot(int, int)
    def set_corner_option(self, corner: int, option: int) -> None:
        self._settings.corner_options[corner] = option
        self.render_thumbnail()  # Update preview

    # Statistics enabled state

    @pyqtProperty(bool)
    def statistics_enabled(self) -> bool:
        return self._settings.statistics_enabled

    @pyqtSlot(bool)
    def set_statistics_enabled(self, enabled: bool) -> None:
        self._settings.statistics_enabled = enabled

    # Use current model enabled state

    @pyqtProperty(bool)
    def use_current_model(self) -> bool:
        return self._settings.use_current_model

    @pyqtSlot(bool)
    def set_use_current_model(self, enabled: bool) -> None:
        self._settings.use_current_model = enabled
        self.render_thumbnail()

    # Save/restore buttons

    @pyqtSlot()
    def restore(self) -> None:
        """
        Restore settings (discard changes)
        """
        pass  # TODO: Restore

    @pyqtSlot()
    def save(self) -> None:
        """
        Save the settings
        """
        pass  # TODO: Save


class GUIManager(QObject):
    """
    GUI manager (adds gui components to extension)
    """

    GUI_FILE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "gui.qml")

    def __init__(self, extension: Extension):
        QObject.__init__(self)

        # Init settings
        self._settings: Settings = Settings()
        self._settings_manager: SettingsManager = SettingsManager(settings=self._settings)

        # Add menu items with popup trigger
        extension.setMenuName("Elegoo Neptune Thumbnails")
        extension.addMenuItem("Thumbnail Settings", self.show_settings_popup)
        self._popup: Optional[QQuickWindow] = None

    def show_settings_popup(self) -> None:
        """
        Show the settings popup
        """
        # Initialize gui if not exists
        if self._popup is None and not self._init_gui():
            Logger.log("e", "Failed to create ElegooNeptuneThumbnails settings window.")

        if self._popup is not None:
            # Show
            self._popup.show()

            # Find thumbnail
            self._settings_manager.set_thumbnail_ref(self._popup.children()[1].children()[3].children()[0])

    def _init_gui(self) -> bool:
        """
        Initialize GUI
        :return: Success state
        """
        # Create the plugin dialog component
        self._popup = CuraApplication.getInstance().createQmlComponent(self.GUI_FILE_PATH, {
            "settings": self._settings_manager
        })
        return self._popup is not None
