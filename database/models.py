from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database.db import Base
from datetime import datetime


class Area(Base):
    __tablename__ = 'areas'

    area_id = Column(Integer, primary_key=True, autoincrement=True)
    area_name = Column(String, nullable=False)
    description = Column(Text)

    cameras = relationship("Camera", back_populates="area")
    predictions = relationship("Prediction", back_populates="area")

    def __repr__(self):
        return f"<Area(area_name={self.area_name})>"


class Camera(Base):
    __tablename__ = 'cameras'

    camera_id = Column(Integer, primary_key=True, autoincrement=True)
    camera_name = Column(String, nullable=False)
    rtsp_url = Column(String, nullable=False)
    area_id = Column(Integer, ForeignKey('areas.area_id'))

    area = relationship("Area", back_populates="cameras")
    prediction_details = relationship("PredictionDetail", back_populates="camera")


class Prediction(Base):
    __tablename__ = 'predictions'

    prediction_id = Column(Integer, primary_key=True, autoincrement=True)
    area_id = Column(Integer, ForeignKey('areas.area_id'))
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_estimate = Column(Integer, nullable=False)

    area = relationship("Area", back_populates="predictions")
    prediction_details = relationship("PredictionDetail", back_populates="prediction")


class PredictionDetail(Base):
    __tablename__ = 'prediction_details'

    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    prediction_id = Column(Integer, ForeignKey('predictions.prediction_id'))
    camera_id = Column(Integer, ForeignKey('cameras.camera_id'))
    image_path = Column(Text, nullable=False)
    estimated_count = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    prediction = relationship("Prediction", back_populates="prediction_details")
    camera = relationship("Camera", back_populates="prediction_details")
