import json
import os
import sys
import time

import jsonpickle
import redis
import stomp

import tools.facePaintTool as faceTool
import tools.poseCommon as poseTool
from Image_sendToProcess_dispatchToClient import settings

user = os.getenv("ACTIVEMQ_USER") or "admin"
password = os.getenv("ACTIVEMQ_PASSWORD") or "password"
host = os.getenv("ACTIVEMQ_HOST") or "localhost"
port = os.getenv("ACTIVEMQ_PORT") or 61613
destination = sys.argv[1:2] or ["/queue/event"]
destination = destination[0]
db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

def dispatch_to_client(activeMQConn):
	print("Waiting for images from recognition process and dispatch to different clients......")

	# continually pool for new images to classify
	while True:
		# attempt to grab a batch of images from the database
		queue = db.lrange(settings.IMAGE_QUEUE_TASKLIST_DONE, 0, settings.BATCH_SIZE - 1)
		imageIDs = []

		# loop over the queue
		for q in queue:
			# deserialize the object and obtain the input image
			q = json.loads(q)
			imageID = q["imageID"]
			# update the list of image IDs
			imageIDs.append(imageID)
			
			#get image and recognition result from redis hashset
			imageContent = db.hget(imageID,"image")
			userToken = db.hget(imageID,"userToken")
			
			#get userID from redis according to userToken
			userID = db.get(userToken)
			userID_str = str(userID, "utf-8")

			#construct the user video queue
			destination = "/user/"+ userID_str +"/video"
			
			#construct the output message which would be sent to web client
			# print(type(imageContent))

			imageResult = imageContent  # 初始化
			imageContentResult = imageContent  # 初始化
# paint result to the raw image [pose]
# 			if int(taskList) & 0x01 > 0:
			poseResult = db.hget(imageID, "poseResult")  # get pose str(json) result
			if poseResult:
				humans = jsonpickle.decode(poseResult)		 #反序列化human对象
				imageResult = poseTool.draw_humans(str(imageContent, "utf-8"), humans)  # draw result to raw picture
				imageContentResult = 'data:image/jpeg;base64,' + str(imageResult, "utf-8")
# paint result to the raw image [face]
# 			if int(taskList) & 0x02 > 0:
			faceResult = db.hget(imageID, "faceResult")
			if faceResult:
				faceResultDic = jsonpickle.decode(faceResult)
				imageResult = faceTool.drawface(imageContentResult,faceResultDic)
				imageContentResult = 'data:image/jpeg;base64,' + str(imageResult, "utf-8")



			output = {"image":imageContentResult}

			#dispatch the result to activeMQ, then send to web client by activeMQ
			activeMQConn.send(destination,json.dumps(output), persistent='false')

				# store the output predictions in the database, using
				# the image ID as the key so we can fetch the results
				#db.set(imageID, json.dumps(output))

		# remove the set of images from our queue
		if len(imageIDs) > 0:
			db.ltrim(settings.IMAGE_QUEUE_TASKLIST_DONE, len(imageIDs), -1)

		# sleep for a small amount
		time.sleep(settings.SERVER_SLEEP)


conn = stomp.Connection(host_and_ports = [(host, port)])
conn.start()
conn.connect(login=user,passcode=password)

dispatch_to_client(conn)

conn.disconnect()