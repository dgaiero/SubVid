from PyQt5.QtCore import QThread
import cv2
import moviepy.editor as mpe
import numpy
from AppParameters import Settings
from draw_background import convert_to_qt, draw_frame


class GenerateVideo(QThread):

   def __init__(self):
      QThread.__init__(self)
      self.settings: Settings

   def __del__(self):
      self.wait()

   def generateVideo(self):
      pilImg: Image = draw_frame(
          self.settings, self.settings.frameTextList[0].line)
      width, height = pilImg.size
      print(f"({width}, {height})")
      # Create the OpenCV VideoWriter
      video: cv2.VideoWriter = cv2.VideoWriter(self.settings.output_location,  # Filename
         -1,  # Negative 1 denotes manual codec selection. You can make this automatic by defining the "fourcc codec" with "cv2.VideoWriter_fourcc"
         # 10 frames per second is chosen as a demo, 30FPS and 60FPS is more typical for a YouTube video
         self.settings.framerate,
         # The width and height come from the stats of image1
         (width, height)
         )
      for i in range(len(self.settings.frameTextList)):
         print(self.settings.frameTextList[i].line)
         pilImg: Image = draw_frame(
             self.settings, self.settings.frameTextList[i].line)
         # frame_length: int = self.settings.framerate*self.settings.frameTextList[i].delta.total_seconds()
         # print(self.settings.frameTextList[i].delta)
         # print(frame_length)
         for i in range(self.settings.frameTextList[i].num_frames):
            video.write(cv2.cvtColor(numpy.array(pilImg), cv2.COLOR_RGB2BGR))
      video.release()
      vclp = mpe.VideoFileClip(self.settings.output_location)
      audio_background = mpe.AudioFileClip(self.settings.sound_track)
      audio_background.set_fps(float(self.settings.framerate))
      # final_audio = mpe.CompositeAudioClip([vclp.audio, audio_background])
      final_vclp = vclp.set_audio(audio_background)
      final_vclp.write_videofile(self.settings.output_location, fps=float(self.settings.framerate))

   def run(self):
      self.generateVideo()
