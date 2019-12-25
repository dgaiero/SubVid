import sys, os
from PyQt5.QtGui import QFont

class Settings():
   def __init__(self, source_time = '', sound_track = '', font = '', font_size = 1, background_frame = '', output_location = ''):
      self.source_time = source_time
      self.sound_track = sound_track
      self.font = font
      self.font_size = font_size
      self.background_frame = ':/placeholders/image_assets/background_image_placeholder.jpg'
      self.preview_frame = ':/placeholders/image_assets/export_preview_placeholder.jpg'
      self.output_location = output_location
      self.frameNumber = 0
      self.frameTextList = []
      self.text_color = [0,0,0]
      self.framerate = 30
      self.videoInProgress = False

   def canPreview(self):
      if self.videoInProgress:
         return False
      if (self.source_time == '') or\
         (self.sound_track == '') or\
         (self.font == '') or\
         (self.background_frame == '') or\
         (self.background_frame.startswith(':')):
         return False
      return True
   
   def canGenerate(self):
      if (self.canPreview() == False):
         return False
      else:
         return not(self.output_location == '')
