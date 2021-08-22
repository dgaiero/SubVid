from PIL import Image, ImageFont, ImageDraw
from AppParameters import Settings
from PyQt5 import QtGui


def draw_frame(appData: Settings, text: list):

    img: Image = Image.open(appData.background_frame)
    W, H = img.size
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(appData.font, appData.font_size)
    h = font.getsize('hg')[1]

    offset_factor = 0
    if appData.text_position == 'top':
        offset_factor = -1
    elif appData.text_position == 'bottom':
        offset_factor = 1

    # Draw background rectangles
    if appData.show_background_frame:
        for idx, ctext in enumerate(text):
            if ctext == '':
                continue
            w, ht = draw.textsize(ctext, font)
            x_cord = ((W-w)/2)+appData.text_offset[0]
            y_cord = (((H-ht*len(text))/2+(idx*ht))+offset_factor *
                      ((H-h*len(text))/2))-appData.text_offset[1]
            draw.rectangle(((x_cord-(h/6), y_cord),
                            (x_cord+w+(h/6), y_cord+h+(h/6))), fill=tuple(
                appData.background_color))

    # Draw text
    for i in range(len(text)):
        ctext = text[i]
        w, _ = draw.textsize(ctext, font)
        x_cord = ((W-w)/2)+appData.text_offset[0]
        y_cord = (((H-h*len(text))/2+(i*h))+offset_factor *
                  ((H-h*len(text))/2))-appData.text_offset[1]
        draw.text((x_cord, y_cord), ctext, tuple(
            appData.text_color), font=font)
    return img


def convert_to_qt(image):
    img = image.convert("RGB")
    data = img.tobytes("raw", "RGB")
    qim = QtGui.QImage(data, img.size[0],
                       img.size[1], QtGui.QImage.Format_RGB888)
    qim = QtGui.QPixmap.fromImage(qim)
    return qim
