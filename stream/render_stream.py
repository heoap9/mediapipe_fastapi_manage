import cv2

import mediapipe as mp
from mediapipe import python
from starlette.websockets import WebSocket

from mediapipe_demo.utils import visualize

import base64
import json
import os
import time
import cv2




def render_detection(frame,detector):
    frame = cv2.flip(frame, 1)

    rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_image)

    current_frame = mp_image.numpy_view()
    current_frame = cv2.cvtColor(current_frame, cv2.COLOR_RGB2BGR)

    det_val = detector.detect(mp_image)
    vis_image = visualize(current_frame, det_val)
    return det_val,vis_image
