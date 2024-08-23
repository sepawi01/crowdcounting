from datetime import datetime
import time
import cv2
import threading
from dataclasses import dataclass, field
import logging

import numpy as np
from PIL import Image
from utils.camera_utils import convert_to_pixel_coords, create_polygon_mask, apply_mask

logger = logging.getLogger(__name__)


@dataclass
class CameraConfig:
    name: str
    rtsp_url: str
    user: str
    password: str
    crop_polygon: list = field(default_factory=lambda: [[0, 100],
                                                        [0, 0],
                                                        [100, 0],
                                                        [100, 0],
                                                        [100, 100]
                                                        ])


class Camera:
    def __init__(self, camera_config: CameraConfig, max_retries=5, retry_delay=2):
        self.name = camera_config.name
        self.rtsp_stream_url = camera_config.rtsp_url
        self.user = camera_config.user
        self.password = camera_config.password
        self.crop_polygon = camera_config.crop_polygon
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self.__rtsp_url_with_auth = self.construct_url_with_auth()

        self.capture = cv2.VideoCapture(self.__rtsp_url_with_auth)
        if not self.capture.isOpened():
            raise Exception(f"Error: Could not open video stream: {self.__rtsp_url_with_auth}")

        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    @property
    def polygon_pixels(self):
        if self.crop_polygon is None:
            return None
        original_height = self.frame.shape[0]
        original_width = self.frame.shape[1]
        return convert_to_pixel_coords(self.crop_polygon, original_width, original_height)

    def construct_url_with_auth(self):
        protocol, rest = self.rtsp_stream_url.split("://")
        return f"{protocol}://{self.user}:{self.password}@{rest}"

    def reinitialize_capture(self):
        """Try to reinitialize the VideoCapture object."""
        self.capture.release()
        retry_count = 0
        while retry_count < self.max_retries:
            logger.info(f"Attempting to reinitialize camera {self.name} (Attempt {retry_count + 1}/{self.max_retries})")
            self.capture = cv2.VideoCapture(self.__rtsp_url_with_auth)
            if self.capture.isOpened():
                logger.info(f"Successfully reinitialized camera {self.name}")
                return True
            else:
                logger.warning(f"Failed to reinitialize camera {self.name}, retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                retry_count += 1
        logger.error(f"Failed to reinitialize camera {self.name} after {self.max_retries} attempts")
        return False

    def update(self):
        """Continuously read frames from the camera in a separate thread."""
        try:
            while self.running:
                with self.lock:
                    ret, frame = self.capture.read()
                    if ret:
                        self.frame = frame
                    else:
                        logger.error(f"Error capturing frame from {self.name}")
                        if not self.reinitialize_capture():
                            logger.error(f"Camera {self.name} will stop due to persistent failure.")
                            self.running = False
        except Exception as e:
            logger.exception(f"Unexpected error in camera {self.name}: {e}")
            self.running = False

    def get_frame(self) -> Image:
        with self.lock:
            if self.frame is None:
                return None

            # Convert frame to RGB
            frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            # Create the polygon mask
            mask = create_polygon_mask(frame.shape, self.polygon_pixels)

            # Apply the mask to the frame to set pixels outside the polygon to black
            masked_frame = apply_mask(frame, mask, fill_color=(0, 0, 0))

            # Find the bounding box of the mask
            # The mask is binary, so the boundingRect function will return the rectangle
            # surrounding all non-zero pixels
            x, y, w, h = cv2.boundingRect(mask.astype(np.uint8))

            # Crop the masked frame to the bounding box
            cropped_frame = masked_frame[y:y + h, x:x + w]

            # Convert the cropped frame to a PIL Image and return it
            return Image.fromarray(cropped_frame)

    def release(self):
        self.running = False
        self.thread.join()  # Ensure the thread is finished
        self.capture.release()

    def __str__(self):
        return f"Camera: {self.name}, RTSP URL: {self.rtsp_stream_url}"

    def __repr__(self):
        return f"Camera({self.name}, {self.rtsp_stream_url})"


class CameraManager:
    def __init__(self):
        self.cameras = []
        self.lock = threading.Lock()

    def add_camera(self, camera: Camera):
        """Add a new camera to the manager."""
        with self.lock:
            self.cameras.append(camera)

    def get_frames(self):
        """Retrieve the latest frames from all cameras."""
        camera_frames = []
        with self.lock:
            for camera in self.cameras:
                frame = camera.get_frame()
                if frame is not None:
                    camera_frames.append({
                        "camera": camera.name,
                        "frame": frame,
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S")
                    })
                else:
                    logger.warning(f"No frame received from {camera.name}")
        return camera_frames

    def display_frames(self, window_size=(320, 240)):
        """Display the frames from all cameras in resized windows."""
        while True:
            frames = self.get_frames()
            for cam_name, frame in frames.items():
                if frame is not None:
                    resized_frame = cv2.resize(frame, window_size)
                    cv2.imshow(cam_name, resized_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    def release_all(self):
        """Release all cameras."""
        with self.lock:
            for camera in self.cameras:
                camera.release()
