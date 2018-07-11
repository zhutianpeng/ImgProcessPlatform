import cv2
import tools.Utils as tools

def drawface(base64img, faceResultDic):
    frame = tools.data_uri_to_cv2_img(base64img)
    face_locations = faceResultDic["face_locations"]
    face_names = faceResultDic["face_names"]
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    base64_result = tools.npimg_to_base64data(frame)
    return base64_result