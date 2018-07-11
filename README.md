**项目说明** 
- 本项目是一个图像处理识别和展示的平台
- 从前端摄像头获取图像，一帧一帧传给后台服务器，中间通过activemq和redis做中间件，server端包含人脸识别和姿态估计两个工程（不完整）的各一份文件（参照）
- 局域网下基本实时传输图像，server处理完的图像，client能通过网页的形式访问。时延较少。
<br>

**项目结构** 
```
ImgProcessPlatform
├─Image_process                                 图像处理文件夹
│    ├─task_face_recognition.py         人脸识别工程的一个python文件
│    └─task_pose_estimate.py            姿态估计工程的一个python文件
│ 
├─Image_sendToProcess_dispatchToClient          图像接收分派控制文件夹
│    ├─setting.py                       配置文件
│    ├─task_send_to_process.py          从前端html的activemq中拿到图像文件，存入redis对应的图像处理队列，等待Image_process来识别或者估计
│    └─task_dispatch_to_clients.py      从redis的hashset里面取出文件，并且送到activemq中，html会自动从activemq中取文件显示在界面上
│
├─js                                            一些js
│ 
├─tools                                         一些tools，帮助task_dispatch_to_clients对图像进行标注（框个脸，标个关节等...）
│
├─index.html                                    前端页面，暂无样式
│
├─activemq.xml                                  这份配置文件要替换到activemq里面，帮助工程与activemq对接（减少大小限制）
│
```
<br>

**项目结构**

<br>
