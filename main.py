from dotenv import load_dotenv

load_dotenv()

from camera import CameraManager, CameraConfig, Camera
from ai import AI
import os
import json
import time
from logger import setup_logger
from sqlalchemy.orm import Session
from database.db import SessionLocal, init_db
from database import crud
import logging

setup_logger()
logger = logging.getLogger(__name__)


def save_results(area_id: int, results: dict):
    db: Session = SessionLocal()
    try:
        db_prediction = crud.create_prediction(db, area_id, results)
        return db_prediction
    except Exception as e:
        logger.error(f"Error saving results to database: {e}")
        db.rollback()
    finally:
        db.close()


def create_area(area_name: str, description: str = None):
    db: Session = SessionLocal()
    try:
        db_area = crud.create_area(db, area_name, description)
        return db_area
    except Exception as e:
        logger.error(f"Error creating area: {e}")
        db.rollback()
    finally:
        db.close()

def create_camera(camera_name: str, rtsp_url: str, area_id: int):
    db: Session = SessionLocal()
    try:
        db_camera = crud.create_camera(db, camera_name, rtsp_url, area_id)
        return db_camera
    except Exception as e:
        logger.error(f"Error creating camera: {e}")
        db.rollback()
    finally:
        db.close()


def main(config_file_path: str = "config.json"):
    save_images = os.getenv("SAVE_IMAGES", "false").lower() == "true"
    device = os.getenv("DEVICE", "cuda")
    logger.info("Starting application.")
    logger.info("Initializing database.")
    try:
        init_db()
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        exit(1)

    # Check if config.json exists
    if not os.path.exists(config_file_path):
        logger.warning("config.json not found, it's needed to run the application, exiting.")
        exit(1)

    with open(config_file_path, "r", encoding="utf-8") as f:
        config = json.load(f)
        logger.info("Loaded configuration from config.json.")

    camera_manager = CameraManager()

    # areas = config.get("areas", [])
    # if len(areas) == 0:
    #     logger.warning("No areas found in configuration, exiting.")
    #     exit(1)
    # # Create area in database
    # area = areas[0]

    # Only working with GLT as a start.
    db_area = create_area("GLT", "Gröna Lunds Tivoli")
    logger.info(f"Working with area: {db_area.area_name}")

    cameras = config["cameras"]
    logger.info(f"Found {len(cameras)} cameras in the first area.")
    for camera in cameras:
        try:
            name = camera["name"]
            rtsp_url = camera["rtsp_url"]
            # Create camera in database
            db_camera = create_camera(name, rtsp_url, db_area.area_id)
            camera_config = CameraConfig(name=name, rtsp_url=rtsp_url, user=os.getenv("CAMERA_USER"),
                                         password=os.getenv("CAMERA_PASSWORD"))
            camera_manager.add_camera(Camera(camera_config))
            logger.info(f"Added camera: {camera_config.name}")
        except Exception as e:
            logger.error(f"Error adding camera: {e}")

    logger.info("Initializing AI.")
    try:
        ai_system = AI(camera_manager=camera_manager, device=device)
        logger.info("AI initialized and ready.")
    except Exception as e:
        logger.error(f"Error initializing AI: {e}")
        exit(1)

    try:
        while True:
            logger.info("Capturing and predicting...")
            start_time = time.time()
            results = ai_system.capture_and_predict(save_images=save_images)
            save_results(db_area.area_id, results)
            logger.info(f"Prediction took {time.time() - start_time:.2f} seconds.")
            logger.info(f"Saved results. {results}")
            seconds_between_runs = 120
            time_to_wait = max(0, 120 - (time.time() - start_time))
            time.sleep(time_to_wait)
    except KeyboardInterrupt:
        logger.info("Received KeyboardInterrupt, exiting application.")
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        camera_manager.release_all()
        logger.info("Releasing all cameras.")
        logger.info("Exiting application.")
        exit(0)


if __name__ == "__main__":
    main("camera_definitions.json")
