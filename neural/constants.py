import threading
import numpy as np

GOSU_WEBSOCKET_URL = "ws://localhost:24050/ws"

EXIT_KEY = 'q'
TRAIN_KEY = '+'

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

PLAYGROUND_WIDTH = 1300
PLAYGROUND_HEIGHT = 1010
MARGIN_TOP = 45
MARGIN_LEFT = 310

ACTIONS_COUNT = 3
REWARD_PRICE = np.asarray([50, -10, -40, -100, -100], dtype=np.int8)

THREAD_CLOSE_EVENT = threading.Event()