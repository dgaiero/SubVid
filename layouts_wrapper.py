import datetime
import os
import sys
import webbrowser

import cv2
import moviepy.editor as mpe
import numpy
import PyQt5.QtGui as QtGui
import requests
from PIL import Image
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene

import layouts.license
import layouts.main_dialog
import layouts_helper
from AppParameters import Settings
from draw_background import convert_to_qt, draw_frame
from Lyrics import MalFormedDataException, Lyrics
from GenerateVideo import GenerateVideo
import functools

processes = set([])


def _statusBarDecorator(message):
   def statusBarDecorator(func):
      @functools.wraps(func)
      def statusBarMessage_wrapper(self, *args, **kwargs):
         self.statusbar.showMessage(message)
         func(self)
         self.statusbar.clearMessage()
      return statusBarMessage_wrapper
   return statusBarDecorator

class MainDialog(QtWidgets.QMainWindow, layouts.main_dialog.Ui_MainWindow):

   def __init__(self, settings, parent=None):
      super(MainDialog, self).__init__(parent)
      layouts_helper.configure_default_params(self)
      self.settings: Settings = settings
      self.fileOpenDialogDirectory = os.path.expanduser('~')
      self.bindLicenseActions()
      self.fps_options.addItems(["23.98", "24", "25", "29.97",
         "30", "50", "59.94", "60"])
      self.fps_options.setCurrentText("30")
      self.source_time_button.clicked.connect(self.getSourceTime)
      self.sound_track_button.clicked.connect(self.getSoundTrack)
      self.font_button.clicked.connect(self.getParamFont)
      self.font_size_tb.valueChanged.connect(self.setFontSize)
      self.red_spin_box_2.valueChanged.connect(self.changeRed)
      self.green_spin_box.valueChanged.connect(self.changeGreen)
      self.blue_spin_box.valueChanged.connect(self.changeBlue)
      self.fps_options.currentTextChanged.connect(self.updateFPS)
      self.background_button.clicked.connect(self.getBackgroundImage)
      self.generate_video_button.clicked.connect(self._generateVideo)
      self.refresh_button.clicked.connect(self.refreshVideo)
      self.video_location_button.clicked.connect(self.getVideoOutputLocation)
      self.frame_next_button.clicked.connect(self.showNextFrame)
      self.frame_previous_button.clicked.connect(self.showPreviousFrame)

      self.videoThread: QThread = GenerateVideo()
      self.videoThread.update.connect(self.updateProgress)
      self.videoThread.text.connect(self.updateVideoGenerationStatusText)
      self.videoThread.image.connect(self.updatePreviewWindowVG)
      self.videoThread.fail.connect(self.generationFailure)
      self.videoThread.finished.connect(self.cleanupVideoGeneration)

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
      if (self.settings.videoInProgress):
         self.frame_previous_button.setEnabled(False)
         self.frame_next_button.setEnabled(False)
      if (self.settings.canPreview() == False):
         self.frame_previous_button.setEnabled(False)
         self.frame_next_button.setEnabled(False)
         return
      if self.settings.frameNumber == 0:
         self.frame_previous_button.setEnabled(False)
      else:
         self.frame_previous_button.setEnabled(True)
      if self.settings.frameNumber == len(self.settings.frameTextList) - 1:
         self.frame_next_button.setEnabled(False)
      else:
         self.frame_next_button.setEnabled(True)

   def showPreviousFrame(self):
      self.settings.frameNumber -= 1
      self.statusbar.showMessage(
          f"Showing frame {self.settings.frameNumber}", msecs=1000)
      self.setPreviewPicture()

   def showNextFrame(self):
      self.settings.frameNumber += 1
      self.statusbar.showMessage(
          f"Showing frame {self.settings.frameNumber}", msecs=1000)
      self.setPreviewPicture()

   def setPreviewPicture(self):
      pilImg = draw_frame(self.settings, self.settings.frameTextList[self.settings.frameNumber].line)
      self.settings.preview_frame = convert_to_qt(pilImg)
      self.resizePreview()

   def _generateVideo(self):
      self.generate_video_status_label = QtWidgets.QLabel()
      self.statusbar.addPermanentWidget(
          self.generate_video_status_label, 100)
      self.toggleButtoms(False, True)

      self.videoThread.settings = self.settings
      self.videoThread.start()

   def toggleButtoms(self, tstatus, vIP):
      self.source_time_button.setEnabled(tstatus)
      self.sound_track_button.setEnabled(tstatus)
      self.font_button.setEnabled(tstatus)
      self.font_size_tb.setEnabled(tstatus)
      self.red_spin_box_2.setEnabled(tstatus)
      self.green_spin_box.setEnabled(tstatus)
      self.blue_spin_box.setEnabled(tstatus)
      self.fps_options.setEnabled(tstatus)
      self.background_button.setEnabled(tstatus)
      self.video_location_button.setEnabled(tstatus)
      self.settings.videoInProgress = vIP

   def updateVideoGenerationStatusText(self, text):
      self.generate_video_status_label.setText(text)

   def updateProgress(self):
      self.video_generation_progress.setValue(
          self.video_generation_progress.value() + 1)

   def updatePreviewWindowVG(self, pilImg):
      self.settings.preview_frame = convert_to_qt(pilImg)
      self.resizePreview()

   def generationFailure(self):
      self.statusbar.removeWidget(self.generate_video_status_label)
      self.toggleButtoms(True, False)
      self.video_generation_progress.setValue(0)
      layouts_helper.show_dialog_non_informative_text(self, "Error",
         f"Video Generation Failure",
         "",
         buttons=QtWidgets.QMessageBox.Ok,
         icon=QtWidgets.QMessageBox.Critical)

   def cleanupVideoGeneration(self):
      self.statusbar.removeWidget(self.generate_video_status_label)
      self.toggleButtoms(True, False)
      self.video_generation_progress.setValue(0)
      layouts_helper.show_dialog_non_informative_text(self, "Done",
         f"Video file located at <code>{self.settings.output_location}</code>",
         "",
         buttons=QtWidgets.QMessageBox.Ok,
         icon=QtWidgets.QMessageBox.NoIcon)

   @_statusBarDecorator("Browse for Source Time Spreadsheet")
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
         self.readSourceTimeData()
      # self.statusbar.clearMessage()

   @_statusBarDecorator("Reading source time data")
   def readSourceTimeData(self):
         frameText = Lyrics(self.settings.source_time,
            str(self.settings.framerate))
         frameText.importData()
         try:
            frameText.readData()
            self.settings.frameTextList = frameText.timecode_frames
            self.video_generation_progress.setMaximum(len(self.settings.frameTextList) + 1)
         except ValueError as e:
            layouts_helper.show_dialog_non_informative_text(
                self, "Error", f"<b>Value Error:</b> {str(e)}", "", buttons=QtWidgets.QMessageBox.Ok)
         except MalFormedDataException as e:
            extended_text = f"{e.message}\nActual Headers: {', '.join(e.actual_headers)}"
            layouts_helper.show_dialog_detailed_text(
                self, "Error", f"Error: {e.message}", "Informative Text", extended_text)

   @_statusBarDecorator("Browse for a font")
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

   def updateFPS(self):
      self.settings.framerate = float(self.fps_options.currentText())
      if (self.settings.source_time != ''):
         self.readSourceTimeData()

   @_statusBarDecorator("Browse for soundtrack")
   def getSoundTrack(self):
      filters = 'All Acceptable Formats (*.mp3 *.m4a *.wav  *.aac);;\
         All Files (*.*)'
      fname = QFileDialog.getOpenFileName(self, 'Select Soundtrack File', self.fileOpenDialogDirectory,
         filters)
      if fname[0] != '':
         self.settings.sound_track = fname[0]
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.sound_track)
         self.sound_track_tb.setText(self.settings.sound_track)
   
   @_statusBarDecorator("Browse for output video location")
   def getVideoOutputLocation(self):
      filters = 'MP4 File (*.mp4)'
      fname = QFileDialog.getSaveFileName(self, 'Save As', self.fileOpenDialogDirectory,
         filters)
      if fname[0] != '':
         self.settings.output_location = fname[0]
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.sound_track)
         self.video_location_tb.setText(self.settings.output_location)

   @_statusBarDecorator("Browse for background image")
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
