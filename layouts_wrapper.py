import datetime
import os
import sys
import webbrowser

import PyQt5.QtGui as QtGui
import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene

import layouts.license
import layouts.main_dialog
import layouts_helper
from draw_background import draw_frame, convert_to_qt
from AppParameters import Settings
from Timecode import Timecode, MalFormedDataException
import cv2

processes = set([])

class MainDialog(QtWidgets.QMainWindow, layouts.main_dialog.Ui_MainWindow):
   def __init__(self, settings, parent=None):
      super(MainDialog, self).__init__(parent)
      layouts_helper.configure_default_params(self)
      self.settings: Settings = settings
      self.fileOpenDialogDirectory = os.path.expanduser('~')
      self.bindLicenseActions()
      self.source_time_button.clicked.connect(self.getSourceTime)
      self.sound_track_button.clicked.connect(self.getSoundTrack)
      self.font_button.clicked.connect(self.getParamFont)
      self.font_size_tb.valueChanged.connect(self.setFontSize)
      self.red_spin_box_2.valueChanged.connect(self.changeRed)
      self.green_spin_box.valueChanged.connect(self.changeGreen)
      self.blue_spin_box.valueChanged.connect(self.changeBlue)
      self.background_button.clicked.connect(self.getBackgroundImage)
      self.generate_video_button.clicked.connect(self.generateVideo)
      self.refresh_button.clicked.connect(self.refreshVideo)
      self.video_location_button.clicked.connect(self.getVideoOutputLocation)
      self.frame_next_button.clicked.connect(self.showNextFrame)
      self.frame_previous_button.clicked.connect(self.showPreviousFrame)
      # self.frame_previous_button.setEnabled(False)
      # self.frame_next_button.setEnabled(False)
      # self.background_preview.showEvent()

      self.source_time_button.setShortcut('Ctrl+E')
      self.sound_track_button.setShortcut('Ctrl+T')
      self.background_button.setShortcut('Ctrl+B')
      self.generate_video_button.setShortcut('Ctrl+G')
      self.video_location_button.setShortcut('Ctrl+L')
      self.refresh_button.setShortcut('Ctrl+R')
      self.frame_previous_button.setShortcut('p')
      self.frame_next_button.setShortcut('n')

      timer100ms = QtCore.QTimer(self)
      timer100ms.timeout.connect(self.runUpdateEvents100ms)
      timer100ms.start(100) # 100 ms refesh rate
      

   def runUpdateEvents100ms(self):
      self.generate_video_button.setEnabled(self.settings.canGenerate())
      self.refresh_button.setEnabled(self.settings.canPreview())
      self.checkFramePosition()

   def resizeEvent(self, event):
      # print("resize")
      self.resizeBackgroundImage()
      self.resizePreview()
      QtWidgets.QMainWindow.resizeEvent(self, event)

   def showEvent(self, event):
      # print("show")
      self.resizeBackgroundImage()
      self.resizePreview()
      QtWidgets.QMainWindow.showEvent(self, event)

   def refreshVideo(self):
      self.setPreviewPicture()

   def checkFramePosition(self):
      if (self.settings.canPreview() == False):
         self.frame_previous_button.setEnabled(False)
         self.frame_next_button.setEnabled(False)
         return
      if self.settings.frameNumber == 0:
         self.frame_previous_button.setEnabled(False)
      else:
         self.frame_previous_button.setEnabled(True)
      if self.settings.frameNumber == len(self.settings.frameTextList):
         self.frame_next_button.setEnabled(False)
      else:
         self.frame_next_button.setEnabled(True)

   def showPreviousFrame(self):
      self.settings.frameNumber -= 1
      self.setPreviewPicture()

   def showNextFrame(self):
      self.settings.frameNumber += 1
      self.setPreviewPicture()

   def setPreviewPicture(self):
      pilImg = draw_frame(self.settings, self.settings.frameTextList[self.settings.frameNumber].line)
      self.settings.preview_frame = convert_to_qt(pilImg)
      self.resizePreview()

   def generateVideo(self):
      pilImg = draw_frame(self.settings, "TEST")
      self.settings.preview_frame = convert_to_qt(pilImg)
      self.resizePreview()

   def getSourceTime(self):
      filters = 'All Acceptable Formats (*.xlsx *.xls *.csv *.tsv);;\
         Excel Files (*.xlsx *.xls);;\
         CSV Files (*.csv);;\
         TSV Files (*.tsv);;\
         All Files (*.*)'
      fname = QFileDialog.getOpenFileName(self, 'Select Timecode File', self.fileOpenDialogDirectory,
         filters)
      if fname[0] != '':
         self.settings.source_time = fname[0]
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.source_time)
         self.source_time_tb.setText(self.settings.source_time)
         frameText = Timecode(self.settings.source_time)
         frameText.importData()
         try:
            frameText.readData()
            self.settings.frameTextList = frameText.timecode_frames
         except ValueError as e:
            layouts_helper.show_dialog_non_informative_text(
               self, "Error", "Value Error.", str(e), buttons=QtWidgets.QMessageBox.Ok, icon=QtWidgets.QMessageBox.Warning)
         except MalFormedDataException as e:
            extended_text = f"{e.message}\nActual Headers: {', '.join(e.actual_headers)}"
            layouts_helper.show_dialog_detailed_text(
                self, "Error", f"Error: {e.message}", "", extended_text)

   def getParamFont(self):
      filters = 'All Acceptable Formats (*.ttf *.otf);;\
         All Files (*.*)'
      file_open_dialog_directory = self.fileOpenDialogDirectory
      if sys.platform == 'win32':
         file_open_dialog_directory = '\\\\localhost\\c$\\windows\\fonts'
      elif sys.platform == 'darwin':
         file_open_dialog_directory = '~/Library/Fonts'
      fname = QFileDialog.getOpenFileName(self, 'Select Font File', file_open_dialog_directory,
         filters)
      if fname[0] != '':
         self.settings.font = fname[0]
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.sound_track)
         self.font_tb.setText(self.settings.font)

   def setFontSize(self):
      self.settings.font_size = self.font_size_tb.value()

   def changeRed(self):
      self.settings.text_color[0] = self.red_spin_box_2.value()

   def changeGreen(self):
      self.settings.text_color[1] = self.green_spin_box.value()

   def changeBlue(self):
      self.settings.text_color[2] = self.blue_spin_box.value()

   def getSoundTrack(self):
      filters = 'All Acceptable Formats (*.mp3 *.m4a *.wav *.aac);;\
         All Files (*.*)'
      fname = QFileDialog.getOpenFileName(self, 'Select Soundtrack File', self.fileOpenDialogDirectory,
         filters)
      if fname[0] != '':
         self.settings.sound_track = fname[0]
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.sound_track)
         self.sound_track_tb.setText(self.settings.sound_track)
   
   def getVideoOutputLocation(self):
      filters = 'MP4 File (*.mp4)'
      fname = QFileDialog.getSaveFileName(self, 'Save As', self.fileOpenDialogDirectory,
         filters)
      if fname[0] != '':
         self.settings.output_location = fname[0]
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.sound_track)
         self.video_location_tb.setText(self.settings.output_location)

   def getBackgroundImage(self):
      filters = 'Image files (*.jpg *.jpeg *.gif *.png)'
      fname = QFileDialog.getOpenFileName(self, 'Select Background File', self.fileOpenDialogDirectory,
         filters)
      if fname[0] != '':
         self.settings.background_frame = fname[0]
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.background_frame)
         self.resizeBackgroundImage()

   def resizeBackgroundImage(self):
      scene = QGraphicsScene()
      pixmap = QtGui.QPixmap(self.settings.background_frame)
      scene.addPixmap(pixmap)
      scale_factor = self.background_preview.width()/scene.width()
      self.background_preview.scale(scale_factor,scale_factor)
      self.background_preview.fitInView(scene.sceneRect(), mode=QtCore.Qt.KeepAspectRatio)
      self.background_preview.setScene(scene)

   def resizePreview(self):
      scene = QGraphicsScene()
      pixmap = QtGui.QPixmap(self.settings.preview_frame)
      scene.addPixmap(pixmap)
      scale_factor = self.preview_graphic.width()/scene.width()
      self.preview_graphic.scale(scale_factor,scale_factor)
      self.preview_graphic.fitInView(scene.sceneRect(), mode=QtCore.Qt.KeepAspectRatio)
      self.preview_graphic.setScene(scene)

   def bindLicenseActions(self):
      license_view_dialog = LicenseWindow()
      processes.add(license_view_dialog)
      self.actionAbout.triggered.connect(license_view_dialog.show)

class LicenseWindow(QtWidgets.QDialog, layouts.license.Ui_Dialog):
   def __init__(self, parent=None):
      super(LicenseWindow, self).__init__(parent)
      layouts_helper.configure_default_params(self)
      self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
      self.viewLicenseOnlineButton.clicked.connect(self.viewLicense)
      self.license_url = 'https://raw.githubusercontent.com/dgaiero/SubVid/master/LICENSE'
      license_text = requests.get(self.license_url)
      self.licenseText.setPlainText(license_text.text)

   def viewLicense(self):
      title = "View License"
      message = f"You are about to open the license in your default webrowser.  Do you want to continue?"
      choice = QtWidgets.QMessageBox.question(self, title,
         message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
      if choice == QtWidgets.QMessageBox.Yes:
         webbrowser.open_new_tab(self.license_url)
