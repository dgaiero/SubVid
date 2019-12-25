from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import moviepy.editor as mpe
from moviepy.editor import ColorClip
import numpy
from AppParameters import Settings
from draw_background import convert_to_qt, draw_frame
import os
import subprocess
import tempfile


class GenerateVideo(QThread):

   text: pyqtSignal = pyqtSignal(object)
   image: pyqtSignal = pyqtSignal(object)
   fail: pyqtSignal = pyqtSignal()
   update : pyqtSignal= pyqtSignal()

   def __init__(self):
      QThread.__init__(self)
      self.settings: Settings

   # def __del__(self):
   #    self.wait()

   def generateVideo(self):
      tempFile = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False)
      tempFile.close()
      print(tempFile.name)
      pilImg: Image = draw_frame(
          self.settings, self.settings.frameTextList[0].line)
      width, height = pilImg.size
      print(f"({width}, {height})")
      # Create the OpenCV VideoWriter
      video: cv2.VideoWriter = cv2.VideoWriter(tempFile.name,
                                               -1,
         self.settings.framerate,
         (width, height)
         )
      for i in range(len(self.settings.frameTextList)):
         # print(self.settings.frameTextList[i].line)
         # self.emit(pyqtSignal('add_post(QString)'),
         #           self.settings.frameTextList[i].line)
         self.text.emit(f"Processing: {self.settings.frameTextList[i].line}")
         pilImg: Image = draw_frame(
             self.settings, self.settings.frameTextList[i].line)
         self.image.emit(pilImg)
         # frame_length: int = self.settings.framerate*self.settings.frameTextList[i].delta.total_seconds()
         # print(self.settings.frameTextList[i].delta)
         # print(frame_length)
         for i in range(self.settings.frameTextList[i].num_frames):
            video.write(cv2.cvtColor(numpy.array(pilImg), cv2.COLOR_RGB2BGR))
         self.update.emit()
      video.release()
      self.text.emit('Writing audio to file')
      vclp = addAudioToVideo(tempFile.name, self.settings.sound_track,
         self.settings.output_location)
      if vclp != 0:
         self.fail.emit()
      self.update.emit()
      os.remove(tempFile.name)

   def run(self):
      self.generateVideo()

def addAudioToVideo(video, audio, output):
   spc = subprocess.call(['ffmpeg', '-y', '-i', video, '-i', audio, '-c:v', 'copy',
                    '-map', '0:v:0', '-map', '1:a:0', '-c:a', 'aac', '-b:a', '192k', output])
   return spc
# ffmpeg -i scb2018_2.mp4 -i "King Tut Scrubby_mixdown.wav" -c:v copy -map 0:v:0 -map 1:a:0 -c:a aac -b:a 192k output.mp4
