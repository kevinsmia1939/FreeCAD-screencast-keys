"""Registration with the FreeCAD GUI."""

import FreeCAD
import FreeCADGui
import os
from .controller import ScreencastController
from .qt import QtCore


_controller = None
ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "Resources", "icons")


def get_controller():
    return _controller


def _initialize_now():
    global _controller
    if _controller is not None:
        return

    main_window = FreeCADGui.getMainWindow()
    if main_window is None:
        return
    _controller = ScreencastController(main_window)
    _controller.start()


def initialize():
    """Register preferences, then create widgets after GUI startup."""
    from .preferences import ScreencastKeysPreferencesPage

    FreeCADGui.addIconPath(ICON_DIR)
    FreeCADGui.addPreferencePage(ScreencastKeysPreferencesPage, "Screencast Keys")
    QtCore.QTimer.singleShot(0, _initialize_now)


class CommandScreencast:
    def GetResources(self):
        return {
            "Pixmap": "screencast-keys",
            "Accel": "S, K",
            "MenuText": "Screencast Keys",
            "ToolTip": "Screencast Keys displays keyboard and mouse input",
        }

    def IsActive(self):
        main_window = FreeCADGui.getMainWindow()
        self.controller = main_window.findChild(QtCore.QObject, "ScreencastKeys")
        return bool(self.controller)

    def Activated(self):
        if self.controller:
            self.controller.toggle()

if FreeCAD.GuiUp:
    # register the FreeCAD command
    FreeCADGui.addCommand("ScreencastKeys", CommandScreencast())
