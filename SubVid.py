import ctypes
import os
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import pyqtSlot

# import configuration_wizard
import layouts_wrapper
# from configuration_wizard import ConfigurationWindow
# from read_common_config import CommonConfig, NoConfigFoundError
import layouts_helper
import AppParameters
# from colorama import init as coloramaInit
# from setup_forms import *

def main():
   setup_parameters()
   #  coloramaInit()
   app = QtWidgets.QApplication(sys.argv)
   script_dir = os.path.dirname(os.path.realpath(__file__))
   app.setWindowIcon(QtGui.QIcon(script_dir + os.path.sep + 'logo.png'))
   # query_user_form = layouts_helper.show_query()
   ApplicationSettings = AppParameters.Settings()

   main_window = layouts_wrapper.MainDialog(ApplicationSettings)
   main_window.show()
   # main_window.statusbar.showMessage('test',2000)
   # main_window.statusbar.setVisible(False)
   # print(QtWidgets.QApplication.instance().devicePixelRatio())
   sys.exit(app.exec_())

def setup_parameters():
   app_id = 'dgaiero.SubVid'
   ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)

   if hasattr(QtCore.Qt, 'AA_EnableHighDpiScaling'):
      QtWidgets.QApplication.setAttribute(
         QtCore.Qt.AA_EnableHighDpiScaling, True)

   if hasattr(QtCore.Qt, 'AA_UseHighDpiPixmaps'):
      QtWidgets.QApplication.setAttribute(
         QtCore.Qt.AA_UseHighDpiPixmaps, True)

if __name__ == "__main__":
   main()
