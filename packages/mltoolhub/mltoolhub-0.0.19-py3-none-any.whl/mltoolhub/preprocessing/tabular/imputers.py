
# 
import numpy as np
import pandas as pd
from tqdm import tqdm

import warnings
warnings.filterwarnings('ignore')

import lightgbm as lgb
from sklearn.preprocessing import  OrdinalEncoder

from mltoolhub.basics import get_quick_summary
from sklearn.base import BaseEstimator, TransformerMixin



class TabImputer(BaseEstimator, TransformerMixin):

    def __init__(self, no_of_iterations: int = 5, regressor=None, classifier=None, device: str = "cpu", max_missing_prcnt: float = 75.0):

        self.no_of_iterations = no_of_iterations
        self.regressor = regressor
        self.classifier = classifier
        self.device = device
        self.max_missing_prcnt = max_missing_prcnt
        
        self._encoder = None
        self._summary = None
        self._high_missing_feats = []
        self._trained_models = {} 

        self._lgb_params = dict(
            device='gpu' if device == 'cuda' else device,verbosity=-1)

    def _get_models(self):

        reg = self.regressor if self.regressor is not None else lgb.LGBMRegressor(**self._lgb_params)
        clf = self.classifier if self.classifier is not None else lgb.LGBMClassifier(**self._lgb_params)
        return reg, clf

    def fit(self, X, y=None):
      

        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X)

        self._summary = get_quick_summary(X, classify=True)
        
        self._high_missing_feats = self._summary.loc[self._summary['missing_percentage'] > self.max_missing_prcnt, 'feature'].tolist()
        
        categorical_features = self._summary.loc[self._summary['nature'] == 'category', 'feature'].to_list()
        if categorical_features:
            self._encoder = OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=np.nan)
            self._encoder.fit(X[categorical_features])
            
        return self
    

    def _stats_impute_internal(self, df, summary):

        for _, row in summary.iterrows():
            feat = row['feature']
            if feat not in df.columns: continue
            
            if row['nature'] == "numeric":
                fill_val = df[feat].median() if "skewed" in str(row['skew_type']) else df[feat].mean()
                df[feat] = df[feat].fillna(fill_val)
            elif row['nature'] == "category":
                if not df[feat].mode().empty:
                    df[feat] = df[feat].fillna(df[feat].mode().values[0])
        return df

    def transform(self, X):
        
        if self._summary is None:
            raise RuntimeError("Transformer must be fitted before calling transform.")

        df = X.copy()

        if self._high_missing_feats:
            df = df.drop(columns=self._high_missing_feats)

        categorical_features = self._summary.loc[self._summary['nature'] == 'category', 'feature'].to_list()
        categorical_features = [f for f in categorical_features if f in df.columns]
        
        if self._encoder and categorical_features:
            df[categorical_features] = self._encoder.transform(df[categorical_features])

        current_summary = get_quick_summary(df, classify=True)
        imputed_df = self._stats_impute_internal(df.copy(), current_summary)
        
        missing_feats = current_summary.loc[current_summary['missing_count'] > 0, ['feature', 'nature']]
        reg_model, clf_model = self._get_models()

        for _ in tqdm(range(self.no_of_iterations),desc="TabImputer in service"):
            for _, row in missing_feats.iterrows():
                feat, nature = row['feature'], row['nature']
                
                null_mask = df[feat].isna()
                if not null_mask.any(): continue

                X_train = imputed_df.loc[~null_mask].drop(columns=[feat])
                y_train = imputed_df.loc[~null_mask, feat]
                X_test = imputed_df.loc[null_mask].drop(columns=[feat])

                if y_train.nunique() <= 1:
                    continue

                model = reg_model if nature == "numeric" else clf_model
                try:
                    model.fit(X_train, y_train)
                    imputed_df.loc[null_mask, feat] = model.predict(X_test)
                except Exception as e:
                    pass 

        if self._encoder and categorical_features:
            imputed_df[categorical_features] = self._encoder.inverse_transform(imputed_df[categorical_features])

        return imputed_df


