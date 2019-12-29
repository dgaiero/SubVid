from PIL import Image, ImageFont, ImageDraw
from AppParameters import Settings
from PyQt5 import QtGui

def draw_frame(appData: Settings, text: list):

   img = Image.open(appData.background_frame)
   W, H = img.size
   draw = ImageDraw.Draw(img)
   # font = ImageFont.truetype(<font-file>, <font-size>)
   font = ImageFont.truetype(appData.font, appData.font_size)
   # draw.text((x, y),"Sample Text",(r,g,b))
   # width, total_height = draw.textsize("abcdefghijklmnopqrstuvwxyz", font)
   h = font.getsize('hg')[1]
   list_text_height = h * len(text)
   # print(list_text_height)
   # print(h)
   # for i in range(len(text)):
   if (len(text) == 2):
      ctext = text[0]
      w, cth = draw.textsize(ctext,font)
      draw.text(((W-w)/2, ((H-h)/2) - h/2),
                  ctext, tuple(appData.text_color), font=font)

      ctext = text[1]
      w, cth = draw.textsize(ctext, font)
      draw.text(((W-w)/2, ((H-h)/2) + h/2),
               ctext, tuple(appData.text_color), font=font)
   if (len(text) == 1):
      ctext = text[0]
      w, cth = draw.textsize(ctext, font)
      draw.text(((W-w)/2, ((H-h)/2)),
               ctext, tuple(appData.text_color), font=font)
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
   appData.font_size = 88
   appData.text_color = [0,42,37]
   appData.font = "C:\\Users\\dgaiero\\OneDrive - California Polytechnic State University\\Documents\\projects\\Scrubby\\2019\\video\\The Wildeast Clean.ttf"
   appData.background_frame = "C:\\Users\\dgaiero\\OneDrive - California Polytechnic State University\\Documents\\projects\\Scrubby\\2019\\video\\background.jpg"
   pilImg = draw_frame(
       appData, ["test text", "another text"])
   pilImg.show()
   pilImg.save("output.jpg")
