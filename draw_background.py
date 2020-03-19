from PIL import Image, ImageFont, ImageDraw
from AppParameters import Settings
from PyQt5 import QtGui

def draw_frame(appData: Settings, text: list):

   img: Image = Image.open(appData.background_frame)
   W, H = img.size
   draw = ImageDraw.Draw(img)
   font = ImageFont.truetype(appData.font, appData.font_size)
   h = font.getsize('hg')[1]
   list_text_height = h * len(text)
   for i in range(len(text)):
      ctext = text[i]
      w, cth = draw.textsize(ctext, font)
      x_cord = (W-w)/2
      y_cord = (H-h*len(text))/2+(i*h)
      draw.text((x_cord, y_cord), ctext, tuple(appData.text_color), font=font)
   return img

def convert_to_qt(image):
   img = image.convert("RGB")
   data = img.tobytes("raw","RGB")
   qim = QtGui.QImage(data, img.size[0], img.size[1], QtGui.QImage.Format_RGB888)
   qim = QtGui.QPixmap.fromImage(qim)
   return qim
