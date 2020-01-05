import datetime
import functools
import json
import os
import pickle
import sys
import webbrowser

import cv2
import numpy
import PyQt5.QtGui as QtGui
import requests
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QFont, QFontDatabase, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QShortcut

import layouts.image_viewer
import layouts.license
import layouts.main_dialog
import layouts_helper
from AppParameters import Settings
from draw_background import convert_to_qt, draw_frame
from GenerateVideo import GenerateVideo
from Lyrics import Lyrics, MalFormedDataException
from uuid import uuid4

processes = set([])

ALL_KEYS_DISABLED = 0
NEXT_KEY_ENABLED = 1
PREVIOUS_KEY_ENABLED = 2
ALL_KEYS_ENABLED = 3

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

   previewClicked = QtCore.pyqtSignal(QtCore.QPoint)
   imageChanged = QtCore.pyqtSignal(object)

   def __init__(self, app, uuid, parent=None):
      super(MainDialog, self).__init__(parent)
      layouts_helper.configure_default_params(self)
      self.app = app
      self.uuid = uuid
      self.settings: Settings = Settings()
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
      self.generate_video_button.clicked.connect(self._generateVideo)
      self.refresh_button.clicked.connect(self.refreshVideo)
      self.video_location_button.clicked.connect(self.getVideoOutputLocation)
      self.frame_next_button.clicked.connect(self.showNextFrame)
      self.frame_previous_button.clicked.connect(self.showPreviousFrame)
      self.source_time_tb.textChanged.connect(self.updateSourceTimeTextBox)
      self.sound_track_tb.textChanged.connect(self.updateSoundTrackTextBox)
      self.font_tb.textChanged.connect(self.updateFontTextBox)
      self.video_location_tb.textChanged.connect(self.updateVideoLocationTextBox)

      self.videoThread: QThread = GenerateVideo()
      self.videoThread.update.connect(self.updateProgress)
      self.videoThread.text.connect(self.updateVideoGenerationStatusText)
      self.videoThread.image.connect(self.updatePreviewWindowVG)
      self.videoThread.success.connect(self.generationSuccessCheck)
      self.videoThread.finished.connect(self.cleanupVideoGeneration)

      self.actionOpen.triggered.connect(self.openPickle)
      self.actionSave_As.triggered.connect(self.saveAsPickle)
      self.actionSave.triggered.connect(self.savePickle)
      self.actionNew.triggered.connect(self.newWindow)

      self.background_preview.setRenderHint(QtGui.QPainter.SmoothPixmapTransform )
      self.preview_graphic.setRenderHint(QtGui.QPainter.SmoothPixmapTransform )

      self.updateColors()

      self.preview_dialog = ImageViewer(self)
      processes.add(self.preview_dialog)
      # self.actionAbout.triggered.connect(self.bindLargePreviewActions)
      self.previewClicked.connect(self.bindLargePreviewActions)

      self.checkFramePosition()

      timer100ms = QtCore.QTimer(self)
      timer100ms.timeout.connect(self.runUpdateEvents100ms)
      timer100ms.start(100) # 100 ms refesh rate

   @_statusBarDecorator("Open Configuration File")
   def openPickle(self):
      filters = 'SubVid Configuration File (*.svp);;\
         All Files (*.*)'
      fname = QFileDialog.getOpenFileName(self, 'Select SubVid Pickle File',
         self.fileOpenDialogDirectory, filters)
      # print(fname)
      if fname[0] == '' or fname is None:
         return
      self.readPickleFile(fname)
      
   def readPickleFile(self, fname):
      with open(fname[0], 'rb') as handle:
         settings = pickle.load(handle)
      # print(**settings)
      self.settings.saveFile = fname[0]
      self.settings.loadFromPickle(**settings)
      self.updateTextBoxFromSettings()
      if self.settings.background_frame != '':
         self.resizeBackgroundImage()
      if self.settings.source_time != '':
         self.readSourceTimeData()
      self.font_size_tb.setValue(self.settings.font_size)
      self.red_spin_box_2.setValue(self.settings.text_color[0])
      self.green_spin_box.setValue(self.settings.text_color[1])
      self.blue_spin_box.setValue(self.settings.text_color[2])
      self.color_preview.setStyleSheet(
          f"background-color: rgb({self.settings.text_color[0]}, \
            {self.settings.text_color[1]}, \
            {self.settings.text_color[2]});")
      
   @_statusBarDecorator("Save Configuration File")
   def saveAsPickle(self):
      filters = 'SubVid Configuration File (*.svp)'
      fname = QFileDialog.getSaveFileName(self, 'Save As',
         self.fileOpenDialogDirectory, filters)
      if (fname[0] == ''):
         return
      self.savePickleFile(fname[0])
      self.settings.saveFile = fname[0]

   def savePickle(self):
      if self.settings.saveFile is None:
         return self.saveAsPickle()
      self.savePickleFile(self.settings.saveFile)

   def savePickleFile(self, fname):
      with open(fname, 'wb') as handle:
         pickle.dump(self.settings.pickleData(), handle,
                     protocol=pickle.HIGHEST_PROTOCOL)

   def runUpdateEvents100ms(self):
      self.generate_video_button.setEnabled(self.settings.canGenerate())
      self.refresh_button.setEnabled(self.settings.canPreview())
      self.setTitle()
      # self.checkFramePosition()

   def setTitle(self):
      if self.settings.saveFile is not None:
         self.setWindowTitle(f"SubVideo ({self.settings.saveFile})")

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

   def closeEvent(self, event):
      # self.app.exit()
      # print(self.saveDataSame())
      if (self.saveDataSame()) == False:
         ret = self.showSaveQuitDialog()
         if (ret == QtWidgets.QMessageBox.Save):
            self.savePickle()
         elif (ret == QtWidgets.QMessageBox.Cancel):
            return
      self.preview_dialog.close()
      self.close()
      del self.app._windows[self.uuid]
      QtWidgets.QMainWindow.closeEvent(self, event)

   def showSaveQuitDialog(self):
      filename = os.path.basename(self.settings.saveFile)

      msg = QtWidgets.QMessageBox(self)
      # msg.setIcon(icon)
      msg.setText(f'Do you want to save the changes you made to "{filename}"')
      # msg.setInformativeText(informative_text)
      msg.setWindowTitle('Unsaved Changes')
      msg.setStandardButtons(QtWidgets.QMessageBox.Save)
      msg.addButton("Don't Save", QtWidgets.QMessageBox.RejectRole)
      msg.addButton(QtWidgets.QMessageBox.Cancel)
      return msg.exec_()

      layouts_helper.show_dialog_non_informative_text(self, "Done",
         f'Do you want to save the changes you made to "{filename}"',
         "",
         buttons=QtWidgets.QMessageBox.Save |
         QtWidgets.QMessageBox.Discard |
         QtWidgets.QMessageBox.Cancel,
         icon=QtWidgets.QMessageBox.NoIcon)

   def mousePressEvent(self, event):
      # print("clicked")
      if self.preview_graphic.underMouse():
         self.previewClicked.emit(QtCore.QPoint(event.pos()))
      QtWidgets.QMainWindow.mousePressEvent(self, event)

   def saveDataSame(self) -> bool:
      if (self.settings.saveFile is None):
         return
      currentData = pickle.dumps(self.settings.pickleData(),
                                protocol=pickle.HIGHEST_PROTOCOL)
      saveData = open(self.settings.saveFile, 'rb').read()
      # print(currentData)
      # print(saveData)
      return currentData == saveData

   def newWindow(self):
      uuid = uuid4()
      self.app._windows[uuid] = MainDialog(
          app=self.app, uuid=uuid)
      self.app._windows[uuid].show()

   def refreshVideo(self):
      self.setPreviewPicture()

   def updateSourceTimeTextBox(self):
      self.settings.source_time = self.source_time_tb.text()
      if os.path.exists(self.settings.source_time):
         self.readSourceTimeData()

   def updateSoundTrackTextBox(self):
      self.settings.sound_track = self.sound_track_tb.text()

   def updateFontTextBox(self):
      self.settings.font = self.font_tb.text()

   def updateVideoLocationTextBox(self):
      self.settings.output_location = self.video_location_tb.text()

   def updateTextBoxFromSettings(self):
      self.source_time_tb.setText(self.settings.source_time)
      self.sound_track_tb.setText(self.settings.sound_track)
      self.font_tb.setText(self.settings.font)
      self.video_location_tb.setText(self.settings.output_location)

   def checkFramePosition(self):
      if (self.settings.videoInProgress):
         self.frame_previous_button.setEnabled(False)
         self.frame_next_button.setEnabled(False)
         return ALL_KEYS_DISABLED
      if (self.settings.canPreview() == False):
         self.frame_previous_button.setEnabled(False)
         self.frame_next_button.setEnabled(False)
         return ALL_KEYS_DISABLED
      enabled = ALL_KEYS_DISABLED
      if self.settings.frameNumber == 0:
         self.frame_previous_button.setEnabled(False)
      else:
         self.frame_previous_button.setEnabled(True)
         enabled |= PREVIOUS_KEY_ENABLED
      if self.settings.frameNumber == len(self.settings.frameTextList) - 1:
         self.frame_next_button.setEnabled(False)
      else:
         self.frame_next_button.setEnabled(True)
         enabled |= NEXT_KEY_ENABLED
      return enabled

   def showPreviousFrame(self):
      if ((self.checkFramePosition() & PREVIOUS_KEY_ENABLED) >= 1):
         self.settings.frameNumber -= 1
         self.statusbar.showMessage(
            f"Showing frame {self.settings.frameNumber + 1}", msecs=1000)
         self.setPreviewPicture()

   def showNextFrame(self):
      if ((self.checkFramePosition() & NEXT_KEY_ENABLED) >= 1):
         self.settings.frameNumber += 1
         self.statusbar.showMessage(
            f"Showing frame {self.settings.frameNumber + 1}", msecs=1000)
         self.setPreviewPicture()

   def setPreviewPicture(self):
      if self.checkFramePosition() >= 1:
         pilImg = draw_frame(self.settings, self.settings.frameTextList[self.settings.frameNumber].line)
         self.settings.preview_frame = convert_to_qt(pilImg)
         self.resizePreview()

   def _generateVideo(self):
      self.generate_video_status_label = QtWidgets.QLabel()
      self.statusbar.addPermanentWidget(
          self.generate_video_status_label, 100)
      self.toggleButtoms(False, True)
      self.toggleTextBoxes(False)

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
      self.background_button.setEnabled(tstatus)
      self.video_location_button.setEnabled(tstatus)
      self.settings.videoInProgress = vIP

   def toggleTextBoxes(self, tstatus):
      self.source_time_tb.setEnabled(tstatus)
      self.sound_track_tb.setEnabled(tstatus)
      self.font_tb.setEnabled(tstatus)
      self.video_location_tb.setEnabled(tstatus)

   def updateVideoGenerationStatusText(self, text):
      self.generate_video_status_label.setText(text)

   def updateProgress(self):
      self.video_generation_progress.setValue(
          self.video_generation_progress.value() + 1)

   def updatePreviewWindowVG(self, pilImg):
      self.settings.preview_frame = convert_to_qt(pilImg)
      self.resizePreview()

   def generationSuccessCheck(self, check):
      if check == False:
         layouts_helper.show_dialog_non_informative_text(self, "Error",
            f"Video Generation Failure",
            "",
            buttons=QtWidgets.QMessageBox.Ok,
            icon=QtWidgets.QMessageBox.Critical)
      else:
         QtWidgets.QApplication.beep()
         layouts_helper.show_dialog_non_informative_text(self, "Done",
            f"Video file located at <br /><code>{self.settings.output_location}</code>",
            "",
            buttons=QtWidgets.QMessageBox.Ok,
            icon=QtWidgets.QMessageBox.NoIcon)

   def cleanupVideoGeneration(self):
      self.statusbar.removeWidget(self.generate_video_status_label)
      self.toggleButtoms(True, False)
      self.toggleTextBoxes(True)
      self.video_generation_progress.setValue(0)

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
      # print(json.dumps(self.settings.__dict__()))
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
      self.updateColors()

   def changeGreen(self):
      self.settings.text_color[1] = self.green_spin_box.value()
      self.updateColors()

   def changeBlue(self):
      self.settings.text_color[2] = self.blue_spin_box.value()
      self.updateColors()

   def updateColors(self):
      self.color_preview.setStyleSheet(
          f"background-color: rgb({self.settings.text_color[0]}, \
            {self.settings.text_color[1]}, \
            {self.settings.text_color[2]});")

   @_statusBarDecorator("Browse for soundtrack")
   def getSoundTrack(self):
      filters = 'All Acceptable Formats (*.mp3 *.m4a *.wav  *.aac *.aif *.aiff);;\
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
      self.preview_dialog.qScene = scene
      self.preview_dialog.resizePreview()
      if self.settings.canPreview():
         self.preview_dialog.setWindowTitle(f"Scene Viewer: Frame {self.settings.frameNumber + 1}")
      # Emit to signal here with QGraphicsScene

   def bindLicenseActions(self):
      self.actionAbout.triggered.connect(self.app.license_view_dialog.show)

   def bindLargePreviewActions(self):
      self.preview_dialog.show()

class LicenseWindow(QtWidgets.QDialog, layouts.license.Ui_Dialog):
   def __init__(self, parent=None):
      super(LicenseWindow, self).__init__(parent)
      layouts_helper.configure_default_params(self)
      self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint | QtCore.Qt.WindowCloseButtonHint)
      self.viewLicenseOnlineButton.clicked.connect(self.viewLicense)
      self.viewAddendumOnlineButton.clicked.connect(self.viewAddendum)
      license_text = open('LICENSE.LGPL').read()
      addendum_text = open('COPYING.LESSER').read()
      self.licenseText.setPlainText(license_text)
      self.addendumText.setPlainText(addendum_text)
      id = QFontDatabase.addApplicationFont(":/fonts/FiraCode-Regular.ttf")
      _fontstr = QFontDatabase.applicationFontFamilies(id)[0]
      _font = QFont(_fontstr, 8)
      self.licenseText.setFont(_font)
      self.addendumText.setFont(_font)

   def viewLicense(self):
      title = "View License"
      message = f"You are about to open the license in your default webrowser. Do you want to continue?"
      choice = QtWidgets.QMessageBox.question(self, title,
         message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
      if choice == QtWidgets.QMessageBox.Yes:
         webbrowser.open_new_tab(self.license_url)

   def viewAddendum(self):
      title = "View Addendum"
      message = f"You are about to open the addendum in your default webrowser. Do you want to continue?"
      choice = QtWidgets.QMessageBox.question(self, title,
                                              message, QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
      if choice == QtWidgets.QMessageBox.Yes:
         webbrowser.open_new_tab(self.addendum_url)

class ImageViewer(QtWidgets.QMainWindow, layouts.image_viewer.Ui_ImageViewer):
   def __init__(self, parent=None):
      super(ImageViewer, self).__init__(parent)
      layouts_helper.configure_default_params(self)
      self.qScene = QGraphicsScene()
      self.MainWindow: MainDialog = parent

      nextShortcut = QShortcut(QKeySequence('Ctrl+N'), self)
      nextShortcut.activated.connect(self.MainWindow.showNextFrame)

      nextShortcut2 = QShortcut(QKeySequence('N'), self)
      nextShortcut2.activated.connect(self.MainWindow.showNextFrame)

      prevShortcut = QShortcut(QKeySequence('Ctrl+P'), self)
      prevShortcut.activated.connect(self.MainWindow.showPreviousFrame)

      prevShortcut2 = QShortcut(QKeySequence('P'), self)
      prevShortcut2.activated.connect(self.MainWindow.showPreviousFrame)

      refreshShortcut = QShortcut(QKeySequence('Ctrl+R'), self)
      refreshShortcut.activated.connect(self.MainWindow.refreshVideo)

      refreshShortcut2 = QShortcut(QKeySequence('R'), self)
      refreshShortcut2.activated.connect(self.MainWindow.refreshVideo)

      fullScreenShortcut = QShortcut(QKeySequence('Ctrl+F'), self)
      fullScreenShortcut.activated.connect(self.toggleFullScreen)

      fullScreenShortcut2 = QShortcut(QKeySequence('F'), self)
      fullScreenShortcut2.activated.connect(self.toggleFullScreen)

      self.preview_graphic.setRenderHint(QtGui.QPainter.SmoothPixmapTransform )

   def resizePreview(self):
      scale_factor = self.preview_graphic.width()/self.qScene.width()
      self.preview_graphic.scale(scale_factor,scale_factor)
      self.preview_graphic.fitInView(self.qScene.sceneRect(), mode=QtCore.Qt.KeepAspectRatio)
      self.preview_graphic.setScene(self.qScene)

   def showEvent(self, event):
      # print("show")
      self.resizePreview()
      QtWidgets.QMainWindow.showEvent(self, event)

   def resizeEvent(self, event):
      # print("resize")
      self.resizePreview()
      QtWidgets.QMainWindow.resizeEvent(self, event)

   def keyPressEvent(self, event):
      pressEvent: QKeyEvent = event
      if (pressEvent.key() == QtCore.Qt.Key_Escape):
         self.hide()
      QtWidgets.QMainWindow.keyPressEvent(self, event)

   # def mousePressEvent(self, event):
   #    # print("clicked")
   #    if self.preview_graphic.underMouse():
   #       # print("clickedd")
   #       self.hide()
   #       # self.showFullScreen()
   #    QtWidgets.QMainWindow.mousePressEvent(self, event)

   def toggleFullScreen(self):
      if self.isFullScreen():
         self.showNormal()
      else:
         self.showFullScreen()

   def mouseDoubleClickEvent(self, event):
      self.toggleFullScreen()
      QtWidgets.QMainWindow.mouseDoubleClickEvent(self, event)
