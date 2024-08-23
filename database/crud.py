from sqlalchemy.orm import Session
from . import models
from database.fabric_lakehouse import save_predictions_to_lakehouse
import logging

logger = logging.getLogger(__name__)


def create_area(db: Session, area_name: str, description: str = None):
    # Create area if it doesn't exist with same name
    db_area = db.query(models.Area).filter(models.Area.area_name == area_name).first()
    if db_area:
        return db_area
    else:
        db_area = models.Area(area_name=area_name, description=description)
        db.add(db_area)
        db.commit()
        db.refresh(db_area)

    return db_area


def get_areas(db: Session):
    return db.query(models.Area).all()


def create_camera(db: Session, camera_name: str, rtsp_url: str, area_id: int):
    # Check if camera already exists, then update
    db_camera = db.query(models.Camera).filter(models.Camera.camera_name == camera_name).first()
    if db_camera:
        db_camera.rtsp_url = rtsp_url
        db_camera.area_id = area_id
        db.commit()
        db.refresh(db_camera)
        return db_camera

    db_camera = models.Camera(camera_name=camera_name, rtsp_url=rtsp_url, area_id=area_id)
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera


def get_cameras(db: Session):
    return db.query(models.Camera).all()

def get_camera(db: Session, camera_id: int):
    return db.query(models.Camera).filter(models.Camera.camera_id == camera_id).first()

def get_camera_by_name(db: Session, camera_name: str):
    return db.query(models.Camera).filter(models.Camera.camera_name == camera_name).first()


def create_prediction(db: Session, area_id: int, results: dict):
    try:
        total_estimate = results["total"]
        db_prediction = models.Prediction(area_id=area_id, total_estimate=total_estimate)
        db.add(db_prediction)
        db.commit()
        db.refresh(db_prediction)
        prediction_details = []
        # Create prediction details
        for camera_name, count in results.items():
            if camera_name != "total":
                db_camera = db.query(models.Camera).filter(models.Camera.camera_name == camera_name).first()
                db_prediction_detail = models.PredictionDetail(
                    prediction_id=db_prediction.prediction_id,
                    camera_id=db_camera.camera_id,
                    estimated_count=count,
                    image_path=f"camera_{camera_name}_{db_prediction.timestamp.strftime('%Y-%m-%dT%H%M%S')}_count_{count}.jpg"
                )
                db.add(db_prediction_detail)
                prediction_details.append(db_prediction_detail)

        db.commit()

        # Save to lakehouse
        # try:
        #     # Having a bunch of trouble working with directly writing to the lakehouse. We skip this for now.
        #     save_predictions_to_lakehouse(db_prediction, prediction_details)
        #     logger.info("Saved predictions to lakehouse.")
        # except Exception as e:
        #     logger.error(f"Error saving predictions to lakehouse: {e}")

    except Exception as e:
        logger.error(f"Error saving predictions to database: {e}")
        db.rollback()
        raise e


    return db_prediction
