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
- 想做的架构
 ![Alt text] (https://github.com/zhutianpeng/ImgProcessPlatform/blob/master/readme_pic/%E5%9F%BA%E4%BA%8E%E5%A7%BF%E6%80%81%E4%BC%B0%E8%AE%A1%E7%9A%84%E5%BA%B7%E5%A4%8D%E5%8C%BB%E7%96%97%E5%B9%B3%E5%8F%B0%E7%9A%84%E7%B3%BB%E7%BB%9F%E6%9E%B6%E6%9E%84.png)

- 目前的结构
 ![Alt text] (https://github.com/zhutianpeng/ImgProcessPlatform/blob/master/readme_pic/%E9%A1%B9%E7%9B%AE%E7%BB%93%E6%9E%84.png)

<br>
