# initialize Redis connection settings
REDIS_HOST = "localhost"
REDIS_PORT = 6379
REDIS_DB = 0

# initialize constants used to control image spatial dimensions and
# data type
IMAGE_WIDTH = 224
IMAGE_HEIGHT = 224
IMAGE_CHANS = 3
IMAGE_DTYPE = "float32"

# initialize constants used for server queuing
IMAGE_QUEUE_TO_FACE_RECOGNITION = "image_queue_to_face_recognition"
IMAGE_QUEUE_TO_OBJECT_RECOGNITION = "image_queue_to_object_recognition"
IMAGE_QUEUE_TO_POSE_ESTIMATION = "image_queue_to_pose_estimation"
IMAGE_QUEUE_TASKLIST_DONE = "image_queue_tasklist_done"
BATCH_SIZE = 100
SERVER_SLEEP = 0.005
CLIENT_SLEEP = 0.005