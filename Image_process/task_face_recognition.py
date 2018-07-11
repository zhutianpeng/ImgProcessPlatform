import face_recognition
from readdata import read_data
import time
import cv2
import numpy as np
import base64
import redis
import json
import jsonpickle

# 这个文件只是用来参照，不可独立运行，是 face_recognition 工程 的一部分

class facerec(object):
    def __init__(self):
        self.all_encoding, self.lable_list, self.counter = read_data.read_file('./dataset')
        self.name_list = read_data.read_name_list('./dataset')
    def pridict(self, img):
        face_names = []
        # 若输入为图像路径
        # frame = face_recognition.load_image_file(img)

        # 若输入为图像数组
        frame = img
        known_image = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        face_locations = face_recognition.face_locations(known_image)

        a1 = time.time()
        face_encodings = face_recognition.face_encodings(known_image, face_locations)
        #匹配，并赋值
        a2 = time.time()
        print("编码时间", a2 - a1)
        for face_encoding in face_encodings:
            i = 0
            j = 0
            for t in self.all_encoding:
                for k in t:
                    match = face_recognition.compare_faces([k], face_encoding, tolerance=0.3)
                    if match[0]:
                        name = self.name_list[i]
                        print(name)
                        j=1
                i = i+1
            if j == 0:
                name = "unknown"
            face_names.append(name)


        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255),  2)

            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left+6, bottom-6), font, 1.0, (255, 255, 255), 1)

        return frame

    def pridict_result(self, img):
        face_names = []
        frame = img
        known_image = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        face_locations = face_recognition.face_locations(known_image)

        a1 = time.time()
        face_encodings = face_recognition.face_encodings(known_image, face_locations)
        #匹配，并赋值
        a2 = time.time()
        print("编码时间", a2 - a1)
        for face_encoding in face_encodings:
            i = 0
            j = 0
            for t in self.all_encoding:
                for k in t:
                    match = face_recognition.compare_faces([k], face_encoding, tolerance=0.3)
                    if match[0]:
                        name = self.name_list[i]
                        print(name)
                        j=1
                i = i+1
            if j == 0:
                name = "unknown"
            face_names.append(name)

        face_dict = {"face_locations":face_locations,"face_names":face_names}
        return face_dict

def data_uri_to_cv2_img(uri):
    encoded_data = uri.split(',')[1]
    nparr = np.fromstring(base64.b64decode(encoded_data.encode('UTF-8')), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

if __name__ == '__main__':
    # 初始化并导入模型
    face = facerec()
    db = redis.StrictRedis(host="localhost", port=6379, db=0)                    # STEP 1: 声明redis数据库
    i = 0
    print("Face recognition Waiting for picture input ......")
    while True:
        i = i + 1
        q = db.blpop("image_queue_to_face_recognition", timeout=0)               # STEP 2: 从image_queue_to_face_recognition中 pop 图片

        if q:  # 判断元组不为空
            # print(q)
            q = json.loads(q[1])
            image = q["image"]  # 此处的image是 base64格式的

            imageID = q["imageID"]
            userToken = q["userToken"]
            taskList = int(q["taskList"])

            db.hset(imageID, "userToken", userToken)
            db.hset(imageID, "image", image)  # 此处的image是 base64格式的 raw picture

            img_np = data_uri_to_cv2_img(image)  # mat格式的，可以直接给opencv

            print("face recognition %d" % i)
            face_dict = face.pridict_result(img_np)

            frozen = jsonpickle.encode(face_dict,unpicklable=False)  # 序列化  （返回的不是图片，是识别的结果）

            db.hset(imageID, "faceResult", frozen)

            taskDone = db.hget(imageID, "taskDone")                              # STEP3: 从redis里面的 hashset 查看imageID对应的taskDone字段
            if taskDone is None:
                taskDone = 0x02;  # face recognition task done
            else:
                taskDone = int(taskDone) | 0x02  # add face recognition task
            # print("taskDone is %d"%taskDone)
            # check if all tasks in tasklist are done or not
            if taskDone == taskList:
                imageData = {'imageID': imageID, 'userToken': userToken}
                db.rpush("image_queue_tasklist_done", json.dumps(imageData))     # STEP4: taskDone（已经做的==taskList（需要做的），face和pose都搞定了，就把imageData放入image_queue_tasklist_done
            else:
                db.hset(imageID, "taskDone", taskDone)



