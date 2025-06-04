import pandas as pd
import numpy as np
from io import BytesIO, StringIO
from sqlalchemy.orm import Session
from sqlalchemy import select, create_engine
import sys
import os

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from database.database import get_db
from database.models import Dataset
from typing import Optional
import logging
from Datasetfilter.determine_accuracy import DetermineDatasetAccuracy
import threading
import time
from datetime import datetime
import json

# Set up logging
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, f'contamination_calculation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')),
        logging.StreamHandler()
    ]
)

# Global variables for tracking progress
PROCESS_STATUS = {
    "is_running": False,
    "total_datasets": 0,
    "processed_datasets": 0,
    "failed_datasets": 0,
    "start_time": None,
    "end_time": None,
    "current_dataset": None,
    "errors": []
}

def save_status():
    """Save the current process status to a file."""
    status_file = os.path.join(log_dir, "contamination_process_status.json")
    with open(status_file, 'w') as f:
        # Create a copy of the status dict with datetime objects converted to strings
        status_copy = PROCESS_STATUS.copy()
        if status_copy["start_time"]:
            status_copy["start_time"] = status_copy["start_time"].isoformat()
        if status_copy["end_time"]:
            status_copy["end_time"] = status_copy["end_time"].isoformat()
        json.dump(status_copy, f, indent=4)

def process_datasets():
    """Process all datasets that don't have contamination values."""
    global PROCESS_STATUS
    
    if PROCESS_STATUS["is_running"]:
        logging.warning("Process is already running")
        return
    
    PROCESS_STATUS["is_running"] = True
    PROCESS_STATUS["start_time"] = datetime.now()
    PROCESS_STATUS["errors"] = []
    save_status()
    
    db = next(get_db())
    try:
        # Get all datasets without contamination values
        datasets = db.execute(
            select(Dataset).where(Dataset.contamination.is_(None))
        ).scalars().all()
        
        PROCESS_STATUS["total_datasets"] = len(datasets)
        logging.info(f"Found {len(datasets)} datasets to process")
        save_status()
        
        for dataset in datasets:
            try:
                PROCESS_STATUS["current_dataset"] = f"Dataset {dataset.id}: {dataset.name}"
                save_status()
                
                # Create DetermineDatasetAccuracy instance for this dataset
                accuracy_determiner = DetermineDatasetAccuracy(dataset.id)
                
                # Calculate contamination using the existing class
                contamination = accuracy_determiner.find_contamination()
                
                if contamination is not None:
                    # Update dataset with contamination value
                    dataset.contamination = contamination
                    db.commit()
                    logging.info(f"Updated contamination value for dataset {dataset.id}: {contamination}")
                    PROCESS_STATUS["processed_datasets"] += 1
                else:
                    logging.warning(f"Could not calculate contamination for dataset {dataset.id}")
                    PROCESS_STATUS["failed_datasets"] += 1
                    PROCESS_STATUS["errors"].append(f"Dataset {dataset.id}: Could not calculate contamination")
                
            except Exception as e:
                error_msg = f"Error processing dataset {dataset.id}: {str(e)}"
                logging.error(error_msg)
                PROCESS_STATUS["failed_datasets"] += 1
                PROCESS_STATUS["errors"].append(error_msg)
                db.rollback()
                continue
            
            save_status()
                
    except Exception as e:
        error_msg = f"Error in batch process: {str(e)}"
        logging.error(error_msg)
        PROCESS_STATUS["errors"].append(error_msg)
    finally:
        PROCESS_STATUS["is_running"] = False
        PROCESS_STATUS["end_time"] = datetime.now()
        PROCESS_STATUS["current_dataset"] = None
        save_status()
        db.close()

def start_background_process():
    """Start the contamination calculation process in the background."""
    thread = threading.Thread(target=process_datasets)
    thread.daemon = False  # Make it a non-daemon thread so it continues after main thread exits
    thread.start()
    return "Process started in background"

def get_process_status():
    """Get the current status of the contamination calculation process."""
    return PROCESS_STATUS

if __name__ == "__main__":
    print("Starting contamination calculation process in background...")
    start_background_process()
    print("Process is running in the background. You can check the logs directory for progress.")
    print("To check status, look for contamination_process_status.json in the logs directory.")
    
    # Keep the main thread alive briefly to show initial status
    time.sleep(2)
    if PROCESS_STATUS["total_datasets"] > 0:
        processed = PROCESS_STATUS["processed_datasets"]
        failed = PROCESS_STATUS["failed_datasets"]
        total = PROCESS_STATUS["total_datasets"]
        print(f"Found {total} datasets to process")
        if processed + failed > 0:
            progress = (processed + failed) / total * 100
            print(f"Current progress: {progress:.1f}% ({processed + failed}/{total} datasets)")
    
    print("\nProcess will continue running in the background.")
    # Don't exit, let the background thread complete
    while PROCESS_STATUS["is_running"]:
        time.sleep(1) 