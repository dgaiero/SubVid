import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import layouts_wrapper
# from setup_forms import *


def configure_default_params(self):
   self.setupUi(self)
   self.setStyle(QtWidgets.QApplication.setStyle("Fusion"))
   # self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())


def show_dialog_detailed_text(parent, window_title, message, informative_text, extended_text, buttons=QtWidgets.QMessageBox.Ok |
      QtWidgets.QMessageBox.Cancel, icon=QtWidgets.QMessageBox.Critical):
   msg = QtWidgets.QMessageBox(parent)
   msg.setIcon(icon)
   msg.setText(message)
   msg.setInformativeText(informative_text)
   msg.setWindowTitle(window_title)
   msg.setDetailedText(extended_text)
   msg.setStandardButtons(buttons)
   return msg.exec_()


def show_dialog_non_informative_text(parent, window_title, message, informative_text, buttons=QtWidgets.QMessageBox.Ok |
      QtWidgets.QMessageBox.Cancel, icon=QtWidgets.QMessageBox.Critical):
   msg = QtWidgets.QMessageBox(parent)
   msg.setIcon(icon)
   msg.setText(message)
   msg.setInformativeText(informative_text)
   msg.setWindowTitle(window_title)
   # msg.setDetailedText(extended_text)
   msg.setStandardButtons(buttons)
   return msg.exec_()

#    msg.buttonClicked.connect(msgbtn)

def show_dialog_non_informative_text_timed(parent, window_title, message, informative_text, buttons=QtWidgets.QMessageBox.Ok |
      QtWidgets.QMessageBox.Cancel, icon=QtWidgets.QMessageBox.Critical):
   time_to_close = 900
   parent.timer_logout.start()
   msg = TimerMessageBox(time_to_close, parent)
   msg.setIcon(icon)
   msg.setText(message)
   msg.setInformativeText(informative_text)
   msg.setWindowTitle(window_title)
   #msg.setDetailedText("This window will close in {0} seconds.".format(time_to_close))
   msg.setStandardButtons(buttons)
   return msg.exec_()

# def show_query(ldap_user):
#     query_user_form = layouts_wrapper.QueryUserSimple(ldap_user)
#     license_view_dialog = layouts_wrapper.LicenseWindow()
#     query_user_form.actionAbout.triggered.connect(
#         license_view_dialog.show)
#     query_user_form.show()
#     return query_user_form


def close_event(object, event, title='Quit Warning', message='Are you sure you want to exit this application?'):
   choice = QtWidgets.QMessageBox.question(object, title,
      message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
   if choice == QtWidgets.QMessageBox.Yes:
      event.accept()
   else:
      event.ignore()

class TimerMessageBox(QtWidgets.QMessageBox):
   def __init__(self, timeout, parent):
      super(TimerMessageBox, self).__init__(parent)
      self.time_to_wait = timeout
      #self.setDetailedText("Closing automatically in {0} seconds.)".format(self.time_to_wait))
      self.setStandardButtons(QtWidgets.QMessageBox.NoButton)
      self.timer = QtCore.QTimer(self)
      self.timer.timeout.connect(self.changeContent)
      self.timer.start(1000)

   def changeContent(self):
      #self.setDetailedTextText("wait (closing automatically in {0} secondes.)".format(self.time_to_wait))
      self.time_to_wait -= 1
      if self.time_to_wait <= 0:
         self.close()

   def closeEvent(self, event):
      self.timer.stop()
      event.accept()