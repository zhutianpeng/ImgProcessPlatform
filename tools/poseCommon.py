from enum import Enum

import tensorflow as tf
import cv2
import numpy as np
import base64
import tools.Utils as tools


regularizer_conv = 0.004
regularizer_dsconv = 0.0004
batchnorm_fused = True
activation_fn = tf.nn.relu


class CocoPart(Enum):
    Nose = 0
    Neck = 1
    RShoulder = 2
    RElbow = 3
    RWrist = 4
    LShoulder = 5
    LElbow = 6
    LWrist = 7
    RHip = 8
    RKnee = 9
    RAnkle = 10
    LHip = 11
    LKnee = 12
    LAnkle = 13
    REye = 14
    LEye = 15
    REar = 16
    LEar = 17
    Background = 18


class MPIIPart(Enum):
    RAnkle = 0
    RKnee = 1
    RHip = 2
    LHip = 3
    LKnee = 4
    LAnkle = 5
    RWrist = 6
    RElbow = 7
    RShoulder = 8
    LShoulder = 9
    LElbow = 10
    LWrist = 11
    Neck = 12
    Head = 13

    @staticmethod
    def from_coco(human):
        # t = {
        #     MPIIPart.RAnkle: CocoPart.RAnkle,
        #     MPIIPart.RKnee: CocoPart.RKnee,
        #     MPIIPart.RHip: CocoPart.RHip,
        #     MPIIPart.LHip: CocoPart.LHip,
        #     MPIIPart.LKnee: CocoPart.LKnee,
        #     MPIIPart.LAnkle: CocoPart.LAnkle,
        #     MPIIPart.RWrist: CocoPart.RWrist,
        #     MPIIPart.RElbow: CocoPart.RElbow,
        #     MPIIPart.RShoulder: CocoPart.RShoulder,
        #     MPIIPart.LShoulder: CocoPart.LShoulder,
        #     MPIIPart.LElbow: CocoPart.LElbow,
        #     MPIIPart.LWrist: CocoPart.LWrist,
        #     MPIIPart.Neck: CocoPart.Neck,
        #     MPIIPart.Nose: CocoPart.Nose,
        # }

        t = [
            (MPIIPart.Head, CocoPart.Nose),
            (MPIIPart.Neck, CocoPart.Neck),
            (MPIIPart.RShoulder, CocoPart.RShoulder),
            (MPIIPart.RElbow, CocoPart.RElbow),
            (MPIIPart.RWrist, CocoPart.RWrist),
            (MPIIPart.LShoulder, CocoPart.LShoulder),
            (MPIIPart.LElbow, CocoPart.LElbow),
            (MPIIPart.LWrist, CocoPart.LWrist),
            (MPIIPart.RHip, CocoPart.RHip),
            (MPIIPart.RKnee, CocoPart.RKnee),
            (MPIIPart.RAnkle, CocoPart.RAnkle),
            (MPIIPart.LHip, CocoPart.LHip),
            (MPIIPart.LKnee, CocoPart.LKnee),
            (MPIIPart.LAnkle, CocoPart.LAnkle),
        ]

        pose_2d_mpii = []
        visibilty = []
        for mpi, coco in t:
            if coco.value not in human.body_parts.keys():
                pose_2d_mpii.append((0, 0))
                visibilty.append(False)
                continue
            pose_2d_mpii.append((human.body_parts[coco.value].x, human.body_parts[coco.value].y))
            visibilty.append(True)
        return pose_2d_mpii, visibilty

CocoPairs = [
    (1, 2), (1, 5), (2, 3), (3, 4), (5, 6), (6, 7), (1, 8), (8, 9), (9, 10), (1, 11),
    (11, 12), (12, 13), (1, 0), (0, 14), (14, 16), (0, 15), (15, 17), (2, 16), (5, 17)
]   # = 19
CocoPairsRender = CocoPairs[:-2]
CocoPairsNetwork = [
    (12, 13), (20, 21), (14, 15), (16, 17), (22, 23), (24, 25), (0, 1), (2, 3), (4, 5),
    (6, 7), (8, 9), (10, 11), (28, 29), (30, 31), (34, 35), (32, 33), (36, 37), (18, 19), (26, 27)
 ]  # = 19

CocoColors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], [170, 255, 0], [85, 255, 0], [0, 255, 0],
              [0, 255, 85], [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], [0, 0, 255], [85, 0, 255],
              [170, 0, 255], [255, 0, 255], [255, 0, 170], [255, 0, 85]]


def read_imgfile(path, width, height):
    val_image = cv2.imread(path, cv2.IMREAD_COLOR)
    if width is not None and height is not None:
        val_image = cv2.resize(val_image, (width, height))
    return val_image

def draw_humans(base64img, humans):
    # change base64 to Mat
    npimg = tools.data_uri_to_cv2_img(base64img)

    image_h, image_w = npimg.shape[:2]
    centers = {}
    for human in humans:
        # draw point
        keys = list(map(lambda x: int(x), human['body_parts'].keys()))
        for i in range(CocoPart.Background.value):
            if i not in keys:
                continue

            body_part = human['body_parts'][str(i)]
            center = (int(body_part['x']['py/newargs'][0] * image_w + 0.5), int(body_part['y']['py/newargs'][0] * image_h + 0.5))
            centers[i] = center
            cv2.circle(npimg, center, 3, CocoColors[i], thickness=3, lineType=8, shift=0)
        # draw line
        for pair_order, pair in enumerate(CocoPairsRender):
            if pair[0] not in keys or pair[1] not in keys:
                continue
            npimg = cv2.line(npimg, centers[pair[0]], centers[pair[1]], CocoColors[pair_order], 3)  # Mat type

    base64_result = tools.npimg_to_base64data(npimg)
    return base64_result

# def data_uri_to_cv2_img(uri):
#     encoded_data = uri.split(',')[1]
#     nparr = np.fromstring(base64.b64decode(encoded_data.encode('UTF-8')), np.uint8)
#     img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
#     return img
#
# def npimg_to_base64data(imageRuselt):
#     # mat转base64, without 'data:image/jpeg;base64,' this head
#     imageRuselt1 = cv2.imencode('.jpg', imageRuselt)[1]
#     base64_data = base64.b64encode(imageRuselt1)
#     return base64_data