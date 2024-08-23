import threading
from datetime import datetime
from queue import Queue

import numpy as np
import torch
from matplotlib import pyplot as plt
from torch.nn.functional import interpolate
from torchvision import transforms
import json
from models import get_model
from PIL import Image
from camera import CameraManager
from pathlib import Path
from utils.camera_utils import resize_density_map
import matplotlib
matplotlib.use('Agg')
import logging

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)
plt.rcParams['font.family'] = 'DejaVu Sans'

def resize_image(image, max_width: int, max_height: int):
    image_copy = image.copy()
    image_copy.thumbnail((max_width, max_height), Image.LANCZOS)
    return image_copy

class AI:

    def __init__(self, camera_manager: CameraManager,
                 model_name: str = "clip_resnet50",
                 input_size: int = 448,
                 reduction: int = 8,
                 dataset_name: str = "qnrf",
                 truncation: int = 4,
                 granularity: str = "fine",
                 device: str = "cuda"):

        self.camera_manager = camera_manager
        if device == "cuda" and not torch.cuda.is_available():
            print("CUDA is not available, using CPU instead.")
            device = "cpu"
        self.device = torch.device(device)

        try:
            with open(f"configs/reduction_{reduction}.json", "r") as f:
                config = json.load(f)[str(truncation)][dataset_name]
        except Exception as e:
            print(f"Error loading configuration: {e}")
            raise e

        self.bins = config["bins"][granularity]
        self.bins = [(float(b[0]), float(b[1])) for b in self.bins]
        self.anchor_points = config["anchor_points"][granularity]["average"]
        self.anchor_points = [float(p) for p in self.anchor_points]

        try:
            # Load the model
            self.model = get_model(
                backbone=model_name,
                input_size=input_size,
                reduction=reduction,
                bins=self.bins,
                anchor_points=self.anchor_points,
                prompt_type="word"
            )
            # Load the model checkpoint
            ckpt = torch.load("checkpoints/qnrf/clip_resnet50_word_448_8_4_fine_1.0_dmcount_aug/best_mae.pth",
                              map_location=self.device)
            self.model.load_state_dict(ckpt)
            self.model = self.model.to(self.device)
            self.model.eval()
        except Exception as e:
            print(f"Error loading model: {e}")
            raise e

        # Define the mean and std for normalization
        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        # Define the preprocessing transforms
        self.to_tensor = transforms.ToTensor()
        self.normalize = transforms.Normalize(mean=self.mean, std=self.std)

        # Store the last prediction result
        self.last_prediction_result = []

    def _predict(self, image: Image) -> tuple:
        image_width, image_height = image.size
        image = self.normalize(self.to_tensor(image)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            pred_density = self.model(image)
            pred_count = pred_density.sum().item()
            resized_pred_density = resize_density_map(pred_density, (image_height, image_width)).cpu()
        return round(pred_count), resized_pred_density.squeeze().numpy()

    def _predict_batch(self, images: list) -> list:
        """Predict on a batch of images, resizing them to a consistent size."""
        # Resize all images to the model's input size
        resized_images = [image.resize((448, 488), Image.LANCZOS) for image in
                          images]

        # Convert images to tensors and normalize them
        batch = torch.stack([self.normalize(self.to_tensor(image)) for image in resized_images]).to(self.device)

        with torch.no_grad():
            pred_densities = self.model(batch)
            pred_counts = pred_densities.sum(dim=[1, 2, 3]).cpu().tolist()

            # Resize densities back to the original image sizes
            resized_pred_densities = [
                interpolate(pred_density.unsqueeze(0), size=(image.size[1], image.size[0]), mode='bilinear',
                            align_corners=False).squeeze(0).squeeze(0).cpu().numpy()
                for pred_density, image in zip(pred_densities, images)
            ]

        return [(round(pred_count), pred_density) for pred_count, pred_density in
                zip(pred_counts, resized_pred_densities)]

    def capture_and_predict(self, save_images: bool = False, save_folder: str = None) -> dict:
        todays_date = datetime.now().strftime("%Y%m%d")

        if save_images:
            if save_folder is None:
                save_folder = Path("predictions")
                save_folder.mkdir(parents=True, exist_ok=True)
            else:
                save_folder = Path(save_folder)
                save_folder.mkdir(parents=True, exist_ok=True)

            original_images_folder = save_folder / "original_images" / f"{todays_date}"
            density_maps_folder = save_folder / "density_maps" / f"{todays_date}"
            original_images_folder.mkdir(parents=True, exist_ok=True)
            density_maps_folder.mkdir(parents=True, exist_ok=True)

        results = {}
        camera_frames: dict = self.camera_manager.get_frames()

        # Create a queue to handle image saving tasks
        image_queue = Queue()
        num_worker_threads = 4  # Number of threads for saving images
        threads = []
        for _ in range(num_worker_threads):
            t = threading.Thread(target=self.save_image_worker, args=(image_queue,))
            t.start()
            threads.append(t)

        for camera_frame in camera_frames:
            frame = camera_frame["frame"]
            camera_name = camera_frame["camera"]
            timestamp = camera_frame["timestamp"]
            if frame is not None:
                pred_count, pred_density = self._predict(frame)
                results[camera_name] = pred_count

                self.last_prediction_result.append({
                    "camera": camera_name,
                    "timestamp": timestamp,
                    "frame": frame,
                    "count": pred_count
                })

                camera_name = camera_name.lower().replace(" ", "_")
                timestamp = timestamp.replace(":", "").replace("-", "")

                if save_images:
                    original_image_path = original_images_folder / f"{camera_name}_{timestamp}_count_{pred_count}.png"
                    density_map_path = density_maps_folder / f"{camera_name}_{timestamp}_count_{pred_count}.png"

                    # Add image saving tasks to the queue
                    image_queue.put((self.save_original_image, (frame, original_image_path)))
                    image_queue.put((self.save_density_map, (frame, pred_density, density_map_path)))

        # Wait for all image saving tasks to complete
        image_queue.join()

        # Stop the worker threads
        for _ in range(num_worker_threads):
            image_queue.put(None)
        for t in threads:
            t.join()

        # Count the total number of people
        results["total"] = sum(results.values())

        return results

    def save_image_worker(self, queue: Queue):
        while True:
            item = queue.get()
            if item is None:
                break
            save_function, args = item
            try:
                save_function(*args)
            except Exception as e:
                logging.error(f"Error saving image: {e}")
            queue.task_done()

    def capture_and_predict_batch(self, save_images: bool = False, save_folder: str = None) -> dict:
        todays_date = datetime.now().strftime("%Y%m%d")

        if save_images:
            if save_folder is None:
                save_folder = Path("predictions")
                save_folder.mkdir(parents=True, exist_ok=True)
            else:
                save_folder = Path(save_folder)
                save_folder.mkdir(parents=True, exist_ok=True)

            original_images_folder = save_folder / "original_images" / f"{todays_date}"
            density_maps_folder = save_folder / "density_maps" / f"{todays_date}"
            original_images_folder.mkdir(parents=True, exist_ok=True)
            density_maps_folder.mkdir(parents=True, exist_ok=True)

        results = {}
        camera_frames: dict = self.camera_manager.get_frames()

        frames = [camera_frame["frame"] for camera_frame in camera_frames if camera_frame["frame"] is not None]
        metadata = [(camera_frame["camera"], camera_frame["timestamp"]) for camera_frame in camera_frames if
                    camera_frame["frame"] is not None]

        predictions = self._predict_batch(frames)

        # Create a queue to handle image saving tasks
        image_queue = Queue()
        num_worker_threads = 4  # Number of threads for saving images
        threads = []
        for _ in range(num_worker_threads):
            t = threading.Thread(target=self.save_image_worker, args=(image_queue,))
            t.start()
            threads.append(t)

        for (camera_name, timestamp), (pred_count, pred_density), frame in zip(metadata, predictions, frames):
            results[camera_name] = pred_count

            self.last_prediction_result.append({
                "camera": camera_name,
                "timestamp": timestamp,
                "frame": frame,
                "count": pred_count
            })

            camera_name = camera_name.lower().replace(" ", "_")
            timestamp = timestamp.replace(":", "").replace("-", "")

            if save_images:
                original_image_path = original_images_folder / f"{camera_name}_{timestamp}_count_{pred_count}.png"
                density_map_path = density_maps_folder / f"{camera_name}_{timestamp}_count_{pred_count}.png"

                # Add image saving tasks to the queue
                image_queue.put((self.save_original_image, (frame, original_image_path)))
                # image_queue.put((self.save_density_map, (frame, pred_density, density_map_path)))

        # Wait for all image saving tasks to complete
        image_queue.join()

        # Stop the worker threads
        for _ in range(num_worker_threads):
            image_queue.put(None)
        for t in threads:
            t.join()

        results["total"] = sum(results.values())
        return results

    def save_original_image(self, frame, path, max_width=800, max_height=600, format="JPEG", quality=70):
        try:
            resized_frame = frame # resize_image(frame, max_width, max_height)
            if format == "JPEG":
                jpeg_path = path.with_suffix(".jpg")
                resized_frame.save(jpeg_path, format, quality=quality)
            else:
                resized_frame.save(path, format, optimize=True, compress_level=9)
        except Exception as e:
            logging.error(f"Error saving original image: {e}")


    def save_density_map(self, frame, pred_density, path):
        try:
            frame_np = np.array(frame)
            if pred_density.ndim == 3 and pred_density.shape[0] == 1:
                frame_np = frame_np.squeeze()

            fig, ax = plt.subplots(figsize=(12, 8))
            ax.imshow(frame_np)
            ax.imshow(pred_density, cmap="jet", alpha=0.5, vmin=0, vmax=np.max(pred_density) * 0.5)
            ax.axis("off")
            plt.savefig(path, bbox_inches='tight', pad_inches=0, dpi=150)  # Reduced DPI for smaller size
            plt.close(fig)
        except Exception as e:
            logging.error(f"Error saving density map: {e}")



