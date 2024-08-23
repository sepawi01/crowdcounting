import os
from dataclasses import dataclass
from typing import Literal
from datetime import datetime, timezone

import pandas as pd
from deltalake import DeltaTable, write_deltalake
from pyarrow.dataset import ParquetFileFormat


STORAGE_OPTIONS = {
    "azure_storage_client_id": os.getenv("AZURE_CLIENT_ID"),
    "azure_storage_client_secret": os.getenv("AZURE_CLIENT_SECRET"),
}


def write_to_lakehouse(table_name: str, df: pd.DataFrame, mode: Literal["append", "overwrite"] = "append"):
    workspace = "FabricTest"
    lakehouse = "AdHocLakeHouse"
    abfss_path = f"abfss://{workspace}@onelake.dfs.fabric.microsoft.com/{lakehouse}.Lakehouse/Tables/"
    # Fabric don't support dictionary encoding
    file_options = ParquetFileFormat().make_write_options(use_dictionary=False)
    write_deltalake(abfss_path + table_name, df, mode=mode, storage_options=STORAGE_OPTIONS, file_options=file_options)


def save_predictions_to_lakehouse(prediction, prediction_details):
    """Save prediction and prediction details to the lakehouse"""
    # Convert Prediction and PredictionDetail to DataFrames
    # prediction_timestamp = datetime.strptime(prediction.timestamp, "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).isoformat()

    prediction_dict = {
        "prediction_id": prediction.prediction_id,
        "area_id": prediction.area_id,
        "prediction_timestamp": prediction.timestamp,
        "total_estimate": prediction.total_estimate
    }

    prediction_df = pd.DataFrame([prediction_dict])


    prediction_details_dicts = [
        {
            "detail_id": detail.detail_id,
            "prediction_id": detail.prediction_id,
            "image_path": detail.image_path,
            "estimated_count": detail.estimated_count,
            "prediction_timestamp": prediction.timestamp
        }
        for detail in prediction_details
    ]

    prediction_details_df = pd.DataFrame(prediction_details_dicts)
    prediction_details_df["prediction_timestamp"] = prediction_details_df["prediction_timestamp"].dt.strftime('%Y-%m-%d %H:%M:%S')

    # Write to Lakehouse
    write_to_lakehouse("crowdcounting_predictions", prediction_df, mode="append")
    write_to_lakehouse("crowdcounting_prediction_details", prediction_details_df, mode="append")
