import argparse
import json
import logging
import ast
import redis
import cv2
import numpy as np
from estimator import TfPoseEstimator
from estimator import Human
from networks import get_graph_path, model_wh
import base64
import pickle
import jsonpickle


# 这个文件只是用来参照，不可独立运行，是 opse_estimation工程 的一部分



#  打印debug信息
logger = logging.getLogger('TfPoseEstimator')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data.encode('UTF-8')), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='tf-pose-estimation run by folder')
    parser.add_argument('--folder', type=str, default='../images/')
    parser.add_argument('--resolution', type=str, default='432x368', help='network input resolution. default=432x368')
    parser.add_argument('--model', type=str, default='mobilenet_thin', help='cmu / mobilenet_thin')
    parser.add_argument('--scales', type=str, default='[None]', help='for multiple scales, eg. [1.0, (1.1, 0.05)]')
    args = parser.parse_args()
    scales = ast.literal_eval(args.scales)

    w, h = model_wh(args.resolution)
    e = TfPoseEstimator(get_graph_path(args.model), target_size=(w, h))

    db = redis.StrictRedis(host="localhost", port=6379, db=0)             # STEP1: 声明REDIS数据库
    i = 0
    print("Pose Estimation Waiting for picture input ......")
    while True:
        i = i + 1
        q = db.blpop("image_queue_to_pose_estimation", timeout=0)        # STEP2: 从image_queue_to_pose_estimation中 pop 图片

        if q:  #判断元组不为空
            # print(q)
            q = json.loads(q[1])
            image = q["image"]  # 此处的image是 base64格式的

            imageID = q["imageID"]
            userToken = q["userToken"]
            taskList = int(q["taskList"])

            db.hset(imageID, "userToken", userToken)
            db.hset(imageID, "image", image)  # 此处的image是 base64格式的 raw picture

            img_np = data_uri_to_cv2_img(image)

            print("face recognition %d" % i)

        # 2.  open pose deals imgs:
        #     # (1) get result picture
        #     humans = e.inference(img_np, scales=scales)
        #     imageRuselt = TfPoseEstimator.draw_humans(img_np, humans, imgcopy=False)  #mat格式
            # (2) get result json
            humans = e.inference(img_np, scales=scales)
            # imageRuseltDic = TfPoseEstimator.draw_humans(img_np, humans, imgcopy=False)

            frozen = jsonpickle.encode(humans,unpicklable=False)  # 序列化human对象并存入,humans是一个human对象的list，human对象里面包含BordParts, 其中有每个点的信息的x,y坐标值

            # # mat转base64, without 'data:image/jpeg;base64,' this head
            # imageRuselt1 = cv2.imencode('.jpg', imageRuselt)[1]
            # base64_data = base64.b64encode(imageRuselt1)
            # db.hset(imageID, "image", base64_data)  # 此处的image是 base64格式的

            db.hset(imageID, "poseResult", frozen)                              # 将识别的结果poseResult （不是图片是json数据，后面连图片一起取出来标注）存入 hashset


            taskDone = db.hget(imageID, "taskDone")                             # STEP3: 从redis里面的 hashset 查看imageID对应的taskDone字段
            if taskDone is None:
                taskDone = 0x01;  # face recognition task done
            else:
                taskDone = int(taskDone) | 0x01  # add face recognition task
            # print("taskDone is %d"%taskDone)
            # check if all tasks in tasklist are done or not
            if taskDone == taskList:
                imageData = {'imageID': imageID, 'userToken': userToken}
                db.rpush("image_queue_tasklist_done", json.dumps(imageData))     # STEP4: taskDone（已经做的==taskList（需要做的），face和pose都搞定了，就把imageData放入image_queue_tasklist_done
            else:
                db.hset(imageID, "taskDone", taskDone)
            # print("Received an image. imageID is %s, userToken is %s" %(imageID,userToken))