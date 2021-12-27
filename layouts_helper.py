import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import layouts_wrapper
import os


class Theme():
    def __init__(self, name, func, customTheme=False):
        self.name = name
        self.func = func
        self.customTheme = customTheme

    def __repr__(self):
        return f"{self.name}"


def configure_default_params(self):
    self.setupUi(self)
    # self.setStyle(QtWidgets.QApplication.setStyle("Fusion"))
    # self.setStyle(QtWidgets.QApplication.setStyle("WindowsVista"))
    # self.setStyle(QtWidgets.QApplication.setStyle("Windows"))
    # self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath('.'), relative_path)

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
    msg.setStandardButtons(buttons)
    return msg.exec_()


def show_dialog_non_informative_text_timed(parent, window_title, message, informative_text, buttons=QtWidgets.QMessageBox.Ok |
                                           QtWidgets.QMessageBox.Cancel, icon=QtWidgets.QMessageBox.Critical):
    time_to_close = 900
    parent.timer_logout.start()
    msg = TimerMessageBox(time_to_close, parent)
    msg.setIcon(icon)
    msg.setText(message)
    msg.setInformativeText(informative_text)
    msg.setWindowTitle(window_title)
    msg.setStandardButtons(buttons)
    return msg.exec_()


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
        self.setStandardButtons(QtWidgets.QMessageBox.NoButton)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.changeContent)
        self.timer.start(1000)

    def changeContent(self):
        self.time_to_wait -= 1
        if self.time_to_wait <= 0:
            self.close()

    def closeEvent(self, event):
        self.timer.stop()
        event.accept()
