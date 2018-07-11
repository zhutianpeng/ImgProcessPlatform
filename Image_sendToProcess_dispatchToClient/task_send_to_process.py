import hashlib
import json
import os
import sys
import time

import redis
import stomp

from Image_sendToProcess_dispatchToClient import settings

user = os.getenv("ACTIVE    MQ_USER") or "admin"
password = os.getenv("ACTIVEMQ_PASSWORD") or "password"
host = os.getenv("ACTIVEMQ_HOST") or "localhost"
port = os.getenv("ACTIVEMQ_PORT") or 61613
destination = sys.argv[1:2] or ["/queue/video"]
destination = destination[0]
db = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)

class MyListener(object):
  
  def __init__(self, conn):
    self.conn = conn
    self.count = 0
    self.start = time.time()
  
  def on_error(self, headers, message):
    print('received an error %s' % message)

  def on_message(self, headers, message):
    if message == "SHUTDOWN":
    
      diff = time.time() - self.start
      print("Received %s in %f seconds" % (self.count, diff))
      conn.disconnect()
      sys.exit(0)
      
    else:
      if 'user-token' in headers:
      	userToken = headers['user-token']
      	taskList = headers['task']
      	userID = userToken
      	#print("user-token is %s"%headers['user-token'])
      imageID = hashlib.sha1(os.urandom(24)).hexdigest()   #generate unique image ID
      imageData = {'imageID':imageID, 'userToken':userToken, 'image':message,'taskList':taskList}
      
      #store the userToken and ID relationship into redis
      db.set(userToken,userID)
      
      #dispatch image to different redis queue according to task list
      if int(taskList)&0x01 > 0:
      	db.rpush(settings.IMAGE_QUEUE_TO_POSE_ESTIMATION, json.dumps(imageData))
      if int(taskList)&0x02 > 0:
      	db.rpush(settings.IMAGE_QUEUE_TO_FACE_RECOGNITION, json.dumps(imageData))
      if int(taskList)&0x04 > 0:
      	db.rpush(settings.IMAGE_QUEUE_TO_OBJECT_RECOGNITION, json.dumps(imageData))
      #else:
      #	print("unrecognized image task!")
      #conn.send("/user/video",json.dumps(imageData), persistent='false')

conn = stomp.Connection(host_and_ports = [(host, port)])
conn.set_listener('', MyListener(conn))
conn.start()
conn.connect(login=user,passcode=password)
conn.subscribe(destination=destination, id=1,ack='auto')
print("Waiting for images from clients, then dispatch to different recognition process...")
while 1: 
  time.sleep(10) 