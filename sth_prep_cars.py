"""
Prepare clean, sharp car cutouts for the STH reel.

Each car is cropped from the 3x3 line-up image, upscaled 4x with EDSR
(OpenCV dnn_superres) and its background removed with rembg.

    pip install rembg onnxruntime opencv-contrib-python-headless
    curl -LO https://raw.githubusercontent.com/Saafke/EDSR_Tensorflow/master/models/EDSR_x4.pb
    python sth_prep_cars.py lineup.jpg cars_dir EDSR_x4.pb
"""
import sys, cv2, numpy as np
from PIL import Image, ImageFilter, ImageEnhance
from rembg import remove, new_session
src = Image.open(sys.argv[1]).convert("RGB"); out = sys.argv[2]; model = sys.argv[3]
CX=[(28,403),(418,793),(808,1182)]; CY=[(205,400),(412,602),(620,806)]
sr = cv2.dnn_superres.DnnSuperResImpl_create(); sr.readModel(model); sr.setModel("edsr",4)
sess = new_session("isnet-general-use")
for i in range(9):
    r,c = divmod(i,3); x0,x1=CX[c]; y0,y1=CY[r]
    crop = src.crop((x0+4,y0+40,x1-4,y1-36))
    up = sr.upsample(cv2.cvtColor(np.array(crop),cv2.COLOR_RGB2BGR))
    up = Image.fromarray(cv2.cvtColor(up,cv2.COLOR_BGR2RGB))
    up = up.filter(ImageFilter.UnsharpMask(radius=2,percent=60,threshold=2))
    up = ImageEnhance.Color(up).enhance(1.12)
    cut = remove(up, session=sess, post_process_mask=True)
    bb = cut.getchannel("A").point(lambda v:255 if v>20 else 0).getbbox()
    cut.crop(bb).save(f"{out}/car{i}.png"); print(i, cut.crop(bb).size, flush=True)
