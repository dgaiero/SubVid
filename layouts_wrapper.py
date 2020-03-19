import datetime
import json
import os
import sys
import webbrowser
from uuid import uuid4

import cv2
import numpy
import PyQt5.QtGui as QtGui
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QThread
from PyQt5.QtGui import QFont, QFontDatabase, QKeyEvent, QKeySequence
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QShortcut

import layouts.file_not_found
import layouts.image_viewer
import layouts.license
import layouts.main_dialog
import layouts_helper
from AppParameters import Settings
from decorators import _checkFileExists, _statusBarDecorator
from draw_background import convert_to_qt, draw_frame
from GenerateVideo import GenerateVideo
from Lyrics import Lyrics, MalFormedDataException

processes = set([])

ALL_KEYS_DISABLED = 0
NEXT_KEY_ENABLED = 1
PREVIOUS_KEY_ENABLED = 2
ALL_KEYS_ENABLED = 3

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

      self.actionOpen.triggered.connect(self.openConfig)
      self.actionSave_As.triggered.connect(self.saveAsConfig)
      self.actionSave.triggered.connect(self.saveConfig)
      self.actionNew.triggered.connect(self.newWindow)

      self.background_preview.setRenderHint(QtGui.QPainter.SmoothPixmapTransform )
      self.preview_graphic.setRenderHint(QtGui.QPainter.SmoothPixmapTransform )

      self.updateColors()

      self.preview_dialog = ImageViewer(self)
      processes.add(self.preview_dialog)
      self.previewClicked.connect(self.bindLargePreviewActions)

      self.checkFramePosition()

      timer100ms = QtCore.QTimer(self)
      timer100ms.timeout.connect(self.runUpdateEvents100ms)
      timer100ms.start(100) # 100 ms refesh rate

      self.fnf = FileNotFound(self)
      processes.add(self.fnf)
   
   
   @_statusBarDecorator("Open Configuration File")
   def openConfig(self):
      filters = 'SubVid Configuration File (*.svp);;\
         All Files (*.*)'
      fname = QFileDialog.getOpenFileName(self, 'Select SubVid Configuration File',
         self.fileOpenDialogDirectory, filters)
      if fname[0] == '' or fname is None:
         return
      self.readConfigFile(fname)
      
   def readConfigFile(self, fname):
      with open(fname[0], 'r') as handle:
         settings = json.load(handle)
      self.settings.saveFile = fname[0]
      self.settings.loadFromConfig(**settings)
      filesNotFoundList = self.checkFilesExist()
      if (filesNotFoundList != []):
         self.fnf.set_data(filesNotFoundList)
         self.fnf.show()
      else:
         self.loadConfigurationToUI(settings)

   def loadConfigurationToUI(self, settings):
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
      
   def checkFilesExist(self):
      filesToCheckList = ["source_time", "sound_track", "font", "background_frame"]
      filesNotFoundList = []
      for file in filesToCheckList:
         if not(self.settings.checkFileExists(file)):
            filesNotFoundList.append([file, self.settings.getFileName(file), eval(f"self.settings.{file}")])
      return filesNotFoundList


   @_statusBarDecorator("Save Configuration File")
   def saveAsConfig(self):
      filters = 'SubVid Configuration File (*.svp)'
      fname = QFileDialog.getSaveFileName(self, 'Save As',
         self.fileOpenDialogDirectory, filters)
      if (fname[0] == ''):
         return
      self.saveConfigFile(fname[0])
      self.settings.saveFile = fname[0]

   def saveConfig(self):
      if self.settings.saveFile is None:
         return self.saveAsConfig()
      self.saveConfigFile(self.settings.saveFile)

   def saveConfigFile(self, fname):
      with open(fname, 'w') as handle:
         json.dump(self.settings.configData(), handle)

   def runUpdateEvents100ms(self):
      self.generate_video_button.setEnabled(self.settings.canGenerate())
      self.refresh_button.setEnabled(self.settings.canPreview())
      self.setTitle()

   def setTitle(self):
      if self.settings.saveFile is not None:
         self.setWindowTitle(f"SubVideo ({self.settings.saveFile})")

   def resizeEvent(self, event):
      self.resizeBackgroundImage()
      self.resizePreview()
      QtWidgets.QMainWindow.resizeEvent(self, event)

   def showEvent(self, event):
      self.resizeBackgroundImage()
      self.resizePreview()
      QtWidgets.QMainWindow.showEvent(self, event)

   def closeEvent(self, event):
      closeAccept = True
      if (self.saveDataSame()) == False:
         ret = self.showSaveQuitDialog()
         if (ret == QtWidgets.QMessageBox.Save):
            self.saveConfig()
         elif (ret == QtWidgets.QMessageBox.Cancel):
            closeAccept = False
            event.ignore()
      if closeAccept:
         self.preview_dialog.close()
         self.close()
         del self.app._windows[self.uuid]
         QtWidgets.QMainWindow.closeEvent(self, event)

   def showSaveQuitDialog(self):
      filename = os.path.basename(self.settings.saveFile)

      msg = QtWidgets.QMessageBox(self)
      msg.setText(f'Do you want to save the changes you made to "{filename}"')
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
      if self.preview_graphic.underMouse():
         self.previewClicked.emit(QtCore.QPoint(event.pos()))
      QtWidgets.QMainWindow.mousePressEvent(self, event)

   def saveDataSame(self) -> bool:
      if (self.settings.saveFile is None):
         return
      currentData = json.dumps(self.settings.configData())
      saveData = open(self.settings.saveFile, 'r').read()
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
      self.settings.font = os.path.normpath(self.font_tb.text())

   def updateVideoLocationTextBox(self):
      self.settings.output_location = os.path.normpath(self.video_location_tb.text())

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

   def toggleButtoms(self, tstatus, video_in_progress_status):
      self.source_time_button.setEnabled(tstatus)
      self.sound_track_button.setEnabled(tstatus)
      self.font_button.setEnabled(tstatus)
      self.font_size_tb.setEnabled(tstatus)
      self.red_spin_box_2.setEnabled(tstatus)
      self.green_spin_box.setEnabled(tstatus)
      self.blue_spin_box.setEnabled(tstatus)
      self.background_button.setEnabled(tstatus)
      self.video_location_button.setEnabled(tstatus)
      self.actionOpen.setEnabled(tstatus)
      self.settings.videoInProgress = video_in_progress_status

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
      fname = self.settings.getSourceTime(self, self.fileOpenDialogDirectory)
      self.processSourceTimeData(fname)

   def processSourceTimeData(self, fname):
      if fname[0] != '':
         self.settings.source_time = os.path.normpath(fname[0])
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.source_time)
         self.source_time_tb.setText(self.settings.source_time)
         self.readSourceTimeData()

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
      fname = self.settings.getParamFont(self, self.fileOpenDialogDirectory)

   def processParamFont(self, fname):
      if fname[0] != '':
         self.settings.font = os.path.normpath(fname[0])
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
      fname = self.settings.getSoundTrack(self, self.fileOpenDialogDirectory)
      self.processSoundTrack(fname)

   def processSoundTrack(self, fname):
      if fname[0] != '':
         self.settings.sound_track = os.path.normpath(fname[0])
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.sound_track)
         self.sound_track_tb.setText(self.settings.sound_track)
   
   @_statusBarDecorator("Browse for output video location")
   def getVideoOutputLocation(self):
      filters = 'MP4 File (*.mp4)'
      fname = QFileDialog.getSaveFileName(self, 'Save As', self.fileOpenDialogDirectory,
         filters)
      if fname[0] != '':
         self.settings.output_location = os.path.normpath(fname[0])
         self.fileOpenDialogDirectory = os.path.dirname(self.settings.sound_track)
         self.video_location_tb.setText(self.settings.output_location)

   @_statusBarDecorator("Browse for background image")
   def getBackgroundImage(self):
      fname = self.settings.getBackgroundImage(self, self.fileOpenDialogDirectory)
      self.processBackgroundImage(fname)

   def processBackgroundImage(self, fname):
      if fname[0] != '':
         self.settings.background_frame = os.path.normpath(fname[0])
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
      self.license_url = 'https://raw.githubusercontent.com/dgaiero/SubVid/master/LICENSE.LGPL'
      self.addendum_url = 'https://raw.githubusercontent.com/dgaiero/SubVid/master/COPYING.LESSER'
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
      self.resizePreview()
      QtWidgets.QMainWindow.showEvent(self, event)

   def resizeEvent(self, event):
      self.resizePreview()
      QtWidgets.QMainWindow.resizeEvent(self, event)

   def keyPressEvent(self, event):
      pressEvent: QKeyEvent = event
      if (pressEvent.key() == QtCore.Qt.Key_Escape):
         self.hide()
      QtWidgets.QMainWindow.keyPressEvent(self, event)

   def toggleFullScreen(self):
      if self.isFullScreen():
         self.showNormal()
      else:
         self.showFullScreen()

   def mouseDoubleClickEvent(self, event):
      self.toggleFullScreen()
      QtWidgets.QMainWindow.mouseDoubleClickEvent(self, event)


class FileNotFound(QtWidgets.QMainWindow, layouts.file_not_found.Ui_FileNotFound):
   def __init__(self, parent=None):
      super(FileNotFound, self).__init__(parent)
      layouts_helper.configure_default_params(self)
      self.MainWindow: MainDialog = parent
      self.closeButton.clicked.connect(self.close)
      self.file_locator_view.setColumnCount(3)
      self.configure_headers()

      self.file_locator_view.cellClicked.connect(self.actionRow)
      self.file_locator_view.cellDoubleClicked.connect(self.locateFile)

      self.locateButton.setEnabled(False)
      self.clearFileButton.setEnabled(False)

      self.locateButton.clicked.connect(self.locateFile)
      self.clearFileButton.clicked.connect(self.initalizeFileValue)

   def actionRow(self):
      self.currentRow = self.file_locator_view.currentRow()
      self.currentItemUsedIn = self.file_locator_view.item(self.currentRow, 0).text()
      self.currentItemFileName = self.file_locator_view.item(self.currentRow, 1).text()
      self.currentItemFilePath = self.file_locator_view.item(
          self.currentRow, 2).text()

      self.locateButton.setEnabled(True)
      self.clearFileButton.setEnabled(True)

   def locateFileProc(self, findFileFunc, mainWindowProc):
      ret = findFileFunc
      if os.path.isfile(ret[0]):
         mainWindowProc(ret)
         self.removeRow(self.currentRow)

   def locateFile(self):
      if self.currentItemUsedIn == "source_time":
         self.locateFileProc(self.MainWindow.settings.getSourceTime(
             self, self.currentItemFilePath), self.MainWindow.processSourceTimeData)
      elif self.currentItemUsedIn == "sound_track":
         self.locateFileProc(self.MainWindow.settings.getSoundTrack(
             self, self.currentItemFilePath), self.MainWindow.processSoundTrack)
      elif self.currentItemUsedIn == "font":
         self.locateFileProc(self.MainWindow.settings.getParamFont(
             self, self.currentItemFilePath, True), self.MainWindow.processParamFont)
      elif self.currentItemUsedIn == "background_frame":
         self.locateFileProc(self.MainWindow.settings.getBackgroundImage(
             self, self.currentItemFilePath), self.MainWindow.processBackgroundImage)

   def removeRow(self, row: int):
      self.file_locator_view.removeRow(row)
      if self.file_locator_view.rowCount() == 0:
         self.hide()
         self.MainWindow.loadConfigurationToUI(self.MainWindow.settings)

   def initalizeFileValue(self):
      self.MainWindow.settings.initLine(self.currentItemUsedIn)
      self.removeRow(self.currentRow)

   def closeEvent(self, event):
      self.MainWindow.close()
      QtWidgets.QMainWindow.closeEvent(self, event)

   def configure_headers(self):
      column_labels = ["Description", "File Name", "File Path"]
      self.file_locator_view.setHorizontalHeaderLabels(column_labels)
      self.file_locator_view.horizontalHeader()

   def set_data(self, data: list):
      self.file_locator_view.setRowCount(0)
      for row in data:
         inx = data.index(row)
         self.file_locator_view.insertRow(inx)
         for i in range(len(row)):
            self.file_locator_view.setItem(inx,i,QtWidgets.QTableWidgetItem(str(row[i])))
