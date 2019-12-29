import ctypes
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot
import error_handler

# import configuration_wizard
import layouts_wrapper
# from configuration_wizard import ConfigurationWindow
# from read_common_config import CommonConfig, NoConfigFoundError
import layouts_helper
# import AppParameters
# from colorama import init as coloramaInit
# from setup_forms import *

qt_exception_hook = error_handler.UncaughtHook()


class SubVid (QtWidgets.QApplication):  # Subclass QApplication

  # Constructor, accepting list of arguments argv[]
  def __init__(self, argv):
    super(SubVid, self).__init__(argv)  # Call constructor of superclass

    # Create a main window; code is handled in other file.
    self._window = layouts_wrapper.MainDialog()
    self._window.show()

    # The important part!
    # Wrapped in a try/except block since user may not have launched this program from a context menu
    # When not launched by context menu, there is no sys.argv[1], so guard against that
    try:
      # sys.argv[1] contains the second command line argument, aka "%1"
      filepath = sys.argv[1]
      # filepath is passed in as a string
      self._window.generateFilepathList([filepath])
    except:
      pass

def main():
   setup_parameters()
   app = SubVid(sys.argv)
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
