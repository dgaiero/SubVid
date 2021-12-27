import ctypes
import os
import sys
from uuid import uuid4

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QSplashScreen

import constants
import error_handler
import layouts_helper
import layouts_wrapper

qt_exception_hook = error_handler.UncaughtHook()


class SubVid (QtWidgets.QApplication):  # Subclass QApplication

    # Constructor, accepting list of arguments argv[]
    def __init__(self, argv):
        super(SubVid, self).__init__(argv)  # Call constructor of superclass

        self.setOrganizationName(constants.ORGANIZATION_NAME)
        self.setOrganizationDomain(constants.ORGANIZATION_DOMAIN)
        self.setApplicationName(constants.APPLICATION_NAME)

        # Create a main window; code is handled in other file.
        startUUID = uuid4()
        self.license_view_dialog = layouts_wrapper.LicenseWindow()
        self._windows: dict = {
            startUUID: layouts_wrapper.MainDialog(app=self, uuid=startUUID)}
        #  self._window = layouts_wrapper.ImageViewer()
        self._windows[startUUID].show()

        # The important part!
        # Wrapped in a try/except block since user may not have launched this program from a context menu
        # When not launched by context menu, there is no sys.argv[1], so guard against that
        try:
            # sys.argv[1] contains the second command line argument, aka "%1"
            filepath = sys.argv[1]
            # filepath is passed in as a string
            self._windows[startUUID].readConfigFile(filepath)
        except:
            pass

    def newWindow(self):
        uuid = uuid4()
        self._windows[uuid] = layouts_wrapper.MainDialog(
            app=self, uuid=uuid)
        self._windows[uuid].show()


def main():
    setup_parameters()
    app = SubVid(sys.argv)
    app.processEvents()
    app.setWindowIcon(QtGui.QIcon(':generalAssets/image_assets/logo.png'))
    sys.exit(app.exec_())


def setup_parameters():
    app_id = 'firelight.SubVid'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

    if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.AA_EnableHighDpiScaling, True)

    if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
        QtWidgets.QApplication.setAttribute(
            QtCore.Qt.AA_UseHighDpiPixmaps, True)


if __name__ == "__main__":
    main()
