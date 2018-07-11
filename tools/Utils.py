import numpy as np
import base64
import cv2

def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data.encode('UTF-8')), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def npimg_to_base64data(imageRuselt):
    # mat转base64, without 'data:image/jpeg;base64,' this head
    imageRuselt1 = cv2.imencode('.jpg', imageRuselt)[1]
    base64_data = base64.b64encode(imageRuselt1)
    return base64_data