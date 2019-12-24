from PIL import Image, ImageFont, ImageDraw
from AppParameters import Settings
from PyQt5 import QtGui

def draw_frame(appData: Settings, text: str):

   img = Image.open(appData.background_frame)
   W, H = img.size
   draw = ImageDraw.Draw(img)
   # font = ImageFont.truetype(<font-file>, <font-size>)
   font = ImageFont.truetype(appData.font, appData.font_size)
   # draw.text((x, y),"Sample Text",(r,g,b))
   w, h = draw.textsize(text,font)
   draw.text(((W-w)/2,(H-h)/2),text,tuple(appData.text_color),font=font)
   return img

def convert_to_qt(image):
   img = image.convert("RGB")
   data = img.tobytes("raw","RGB")
   qim = QtGui.QImage(data, img.size[0], img.size[1], QtGui.QImage.Format_RGB888)
   qim = QtGui.QPixmap.fromImage(qim)
   return qim

if __name__ == "__main__":
   appData = Settings()
   appData.background_frame = 'C:\\Users\\dgaiero\\OneDrive - California Polytechnic State University\\Documents\\projects\\SubVid\\layouts\\image_assets\\background_image_placeholder.jpg'
   draw_frame(appData, "test text")