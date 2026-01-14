from pyimager.main import *

img = new_img(name="Testing trackbars")
fs, tk = 100, 3

def p(event, x, y, flags, params):
    if event==cv2.EVENT_LBUTTONDOWN:
        an = params[0].get()
        print(f"Value: {an}")
        img:Image = params[1] ; img.img = img.new_image()
        img.multiline_text("Hey\nhello", ct, COL.green, 3, 200, an, align="right")

t = img.trackbar("TEST", min=0, fontSize=fs, thickness=tk)
b = img.button("Test", fontSize=fs, thickness=tk)
b.on_click(p, [t, img])
a = b.remove()
s = 100
img.text("A", ct, COL.blue, 3, 5, 26)
img.build()
while img.is_opened():
    wk = img.show()
    if wk == -1: pass