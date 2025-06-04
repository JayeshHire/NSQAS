import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy import ndimage
from scipy.signal import argrelextrema
from datetime import datetime, timedelta
from database.db_operations import get_dataset_by_id
from database.database import get_db
from io import BytesIO, StringIO

class DetermineDatasetAccuracy:
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        self.load_dataset()
        self.preprocess_dataset()

    def load_dataset(self):
        """Load the dataset from the database and convert to DataFrame."""
        db = next(get_db())  # Get database session
        try:
            dataset = get_dataset_by_id(db, self.dataset_id)  # Pass db session to get_dataset_by_id
            if dataset is None:
                raise ValueError(f"Dataset with ID {self.dataset_id} not found")
                
            self.dataset_name = dataset.name
            
            # Convert binary data to DataFrame
            try:
                if dataset.file_name.lower().endswith('.csv'):
                    self.data = pd.read_csv(StringIO(dataset.file_data.decode('utf-8')))
                else:  # Excel file
                    self.data = pd.read_excel(BytesIO(dataset.file_data))
            except Exception as e:
                raise ValueError(f"Error reading dataset: {str(e)}")
        finally:
            db.close()

    def preprocess_dataset(self):
        """Prepare the dataset for contamination analysis."""
        # Keep only numeric columns for analysis
        self.features = self.data.select_dtypes(include=[np.number]).columns.tolist()
        
        if not self.features:
            raise ValueError("No numeric columns found in the dataset")
        
        # Remove rows with missing values in numeric columns
        self.data = self.data.dropna(subset=self.features)
        
        if len(self.data) == 0:
            raise ValueError("No valid data rows after preprocessing")

    def find_contamination_elbow(self):
        """Find optimal contamination using the elbow method on anomaly scores."""
        X = self.data[self.features].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = IsolationForest(contamination=0.1, random_state=42, n_estimators=100)
        model.fit(X_scaled)
        scores = model.decision_function(X_scaled)

        sorted_scores = np.sort(scores)
        smoothed_scores = ndimage.gaussian_filter1d(sorted_scores, sigma=5)
        second_derivative = np.gradient(np.gradient(smoothed_scores))
        min_indices = argrelextrema(second_derivative, np.less)[0]
        
        if len(min_indices) > 0:
            elbow_idx = min_indices[0]  
            optimal_contamination = elbow_idx / len(sorted_scores)
        else:
            optimal_contamination = 0.05  

        return optimal_contamination
    
    def find_optimal_contamination_silhouette(self, contamination_range=np.arange(0.01, 0.2, 0.01)):
        """Find optimal contamination using silhouette score."""
        X = self.data[self.features].copy()
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        best_score = -1
        best_contamination = 0.05  # Default

        for contamination in contamination_range:
            model = IsolationForest(contamination=contamination, random_state=42, n_estimators=100)
            labels = model.fit_predict(X_scaled)

            if len(np.unique(labels)) < 2:
                continue

            score = silhouette_score(X_scaled, labels)
            if score > best_score:
                best_score = score
                best_contamination = contamination

        return best_contamination
    
    def find_contamination(self):
        """Combine elbow method and silhouette score for robust optimization."""
        try:
            # First, get a rough estimate using the elbow method (faster)
            elbow_contamination = self.find_contamination_elbow()

            # Define a narrow search range around the elbow estimate
            lower_bound = max(0.001, elbow_contamination * 0.5)
            upper_bound = min(0.2, elbow_contamination * 1.5)
            fine_range = np.linspace(lower_bound, upper_bound, 20)

            # Fine-tune using silhouette score
            silhouette_contamination = self.find_optimal_contamination_silhouette(
                contamination_range=fine_range)

            # Return the final contamination value
            return silhouette_contamination
            
        except Exception as e:
            raise ValueError(f"Error calculating contamination: {str(e)}")

    
