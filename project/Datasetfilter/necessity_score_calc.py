from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor
import shap
import pandas as pd
import streamlit as st
from database.db_operations import get_ai_model_by_id, create_necessity_score, get_necessity_scores, get_all_datasets, get_user_by_email
from database.database import get_db
from io import StringIO

class NecessityScoreCalculator:
    def __init__(self, model_id: int):
        self.model_id = model_id
        db = next(get_db())
        self.data = pd.read_csv(StringIO(get_ai_model_by_id(db, self.model_id).training_data_set.decode('utf-8')))
        self.get_feature_contribution()

    def get_feature_contribution(self):
        
        db = next(get_db())
        model = get_ai_model_by_id(db, self.model_id)
        self.features = [feature for feature in model.training_data_set_metadata['columns'] if feature != model.target_field]
        x= self.data[self.features]
        y= self.data[model.target_field]

        current_user = get_user_by_email(db, str(st.user.email))

        # check if for the model id, feature is already in the necessity_scores table
        necessity_scores = get_necessity_scores(db, current_user.id, self.model_id)
        # print(f"[Inside get_feature_contribution] necessity_scores: {[score.feature_name for score in necessity_scores]}")
        if necessity_scores:
            scores = [score.score for score in necessity_scores]
            self.necessity_scores = pd.DataFrame(scores, index=self.features)
            return

        x_train, x_test, y_train, y_test= train_test_split(x, y, test_size=0.2, random_state=0)

        model = XGBRegressor(n_estimators=100, max_depth=4)
        model.fit(x_train, y_train)

        explainer = shap.Explainer(model, x_train)
        shap_values = explainer(x_test)
        shap_df= pd.DataFrame(shap_values.values, columns=x_test.columns)

        mean_contribution= shap_df.abs().mean()
        relative_contribution= mean_contribution/mean_contribution.sum()
        self.necessity_scores= pd.DataFrame(relative_contribution, index=self.features)

        for feature, score in zip(self.features, self.necessity_scores):
            create_necessity_score(db, current_user.id, self.model_id, feature, score)

    def get_necessity_scores(self):
        #get the feature from datasets table
        # get only those features which are equal to self.features
        # return the features which are equal to self.features  
        db = next(get_db())
        datasets = get_all_datasets(db)
        current_user = get_user_by_email(db, str(st.user.email))
        necessity_scores = []
        for dataset in datasets:
            if dataset.is_public or dataset.owner_id == current_user.id:
                dataset_df = pd.read_csv(StringIO(dataset.file_data.decode('utf-8')))
                dataset_score = []
                score_lst = []
                score = 0
                for feature in self.features:
                    if feature in dataset_df.columns:
                        # st.write(NecessityScoreCalculator(self.model_id).necessity_scores.loc[feature])
                        score += NecessityScoreCalculator(self.model_id).necessity_scores.loc[feature][0]
                # print(f"hello score: {score}")
                necessity_scores.append((score, dataset.id))

        # print(f"necessity_scores: {necessity_scores}")
        return necessity_scores
