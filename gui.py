from os import path

from PyQt6.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal

from UM.Extension import Extension
from UM.Logger import Logger
from cura.CuraApplication import CuraApplication


class Settings(QObject):
    """
    Thumbnail settings
    """
    thumbnail_enabled_changed: pyqtSignal = pyqtSignal()

    def __init__(self, parent=None):
        QObject.__init__(self, parent)

        self.thumbnail_enabled: bool = True

    @pyqtSlot(bool, name="set_thumbnails_enabled")
    def set_thumbnails_enabled(self, enabled: bool) -> None:
        self.thumbnail_enabled = enabled

    @pyqtProperty(bool, notify=thumbnail_enabled_changed)
    def are_thumbnails_enabled(self) -> bool:
        return self.thumbnail_enabled


class GUIManager(QObject):
    """
    GUI controller
    """

    GUI_FILE_PATH: str = path.join(path.dirname(path.realpath(__file__)), "gui.qml")

    def __init__(self, extension: Extension, parent=None):
        QObject.__init__(self, parent)

        # Init settings
        self.settings: Settings = Settings()

        # Add menu items
        extension.setMenuName("Elegoo Neptune Thumbnails")
        extension.addMenuItem("Configure Thumbnail", self.show_popup)
        self._gui = None

    def show_popup(self) -> None:
        """
        Show the GUI popup
        """
        if self._gui is None:
            if self._create_view():
                Logger.log("d", "Post processing view created.")
                self._gui.show()
            else:
                Logger.log("e", "Failed to create ElegooNeptuneThumbnails settings window.")

    def _create_view(self) -> bool:
        """
        Initialize GUI
        :return: Success state
        """
        # Create the plugin dialog component
        self._gui = CuraApplication.getInstance().createQmlComponent(self.GUI_FILE_PATH, {
            "plugin": self,
            "settings": self.settings
        })
        if self._gui is None:
            return False

        # Create the save button component
        CuraApplication.getInstance().addAdditionalComponent("saveButton", self._gui.findChild(QObject,
                                                                                               "postProcessingSaveAreaButton"))
        return True

    @pyqtSlot(bool, name="popup_closed")
    def popup_closed(self) -> None:
        pass

    @pyqtSlot(bool, name="save_clicked")
    def save_clicked(self) -> None:
        pass
