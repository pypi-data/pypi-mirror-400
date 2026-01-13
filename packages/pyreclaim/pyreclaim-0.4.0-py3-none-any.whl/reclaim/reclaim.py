import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import  r2_score, mean_absolute_error,  root_mean_squared_error
import joblib

# Model libraries
import xgboost as xgb
import lightgbm as lgb
from catboost import  Pool, CatBoostRegressor


class Reclaim:
    """
    A stacked ensemble predictor for Sedimentation Rate (SR) combining
    XGBoost, LightGBM, and CatBoost base models with a meta-model.

    Parameters
    ----------
    model : string, optional
        Any regression model to use for model predictions (default: ensemble of base models). 
        It can be "ensemble", "XGBoost", "LightGBM", or "CatBoost".
    feature_order_list : list, optional
        List of feature names in the order they should be used in the model.
    """
    def __init__(self, model=None, feature_order_list=None):
        self.feature_order_list = feature_order_list
        self.xgb_model = None
        self.lgb_model = None
        self.cat_model = None
        self.main_model = model if model in ['XGBoost', 'LightGBM', 'CatBoost'] else 'ensemble'
        self.cat_features = None
        self.feature_order_list = None

    def fit(self, X_train, y_train, weight_train=None, cat_features=None,
            X_val=None, y_val=None, weight_val=None):
        """
        Train the stacked ensemble model.

        Parameters
        ----------
        X_train : pd.DataFrame or np.array
            Features for training the base models.
        y_train : pd.Series or np.array
            Target variable for training.
        weight_train : pd.Series or np.array, optional
            Sample weights for training base models.
        cat_features : list, optional
            List of categorical feature indices for CatBoost.
        X_val : pd.DataFrame or np.array, optional
            Validation features for early stopping.
        y_val : pd.Series or np.array, optional
            Validation target for early stopping.
        weight_val : pd.Series or np.array, optional
            Validation sample weights.
        """
        self.cat_features = cat_features
        
        if isinstance(X_train, pd.DataFrame):
            # Store the column order
            self.feature_order_list = list(X_train.columns)
        elif isinstance(X_train, np.ndarray):
            if self.feature_order_list is None:
                raise ValueError(
                    "X_train is a NumPy array without column names. "
                    "Please provide 'feature_order_list' explicitly when creating model instance."
                )

        # ---- Train XGBoost ----
        self.xgb_model = xgb.XGBRegressor(
            n_estimators=800,
            learning_rate=0.05,
            tweedie_variance_power=1.5,
            max_depth=5,
            subsample=0.7,
            colsample_bytree=0.7,
            objective='reg:tweedie',
            reg_alpha=70,
            reg_lambda=30,
            # objective='reg:squaredlogerror',  # robust for skewed targets
            random_state=42,
            n_jobs=-1
        )
        self.xgb_model.fit(
            X_train, y_train,
            sample_weight=weight_train,
            eval_set=[(X_val, y_val)] if X_val is not None else None,
            sample_weight_eval_set=[weight_val] if weight_val is not None else None,
            verbose=False
        )

        # ---- Train LightGBM ----
        train_data = lgb.Dataset(X_train, label=y_train, weight=weight_train)
        val_data = lgb.Dataset(X_val, label=y_val, weight=weight_val, reference=train_data) if X_val is not None else None
        self.lgb_model = lgb.train(
            {
                'objective': 'tweedie',
                'tweedie_variance_power': 1.7,
                'metric': 'rmse',
                'learning_rate': 0.01,
                'num_leaves': 31,
                'feature_fraction': 0.7,
                'bagging_fraction': 0.7,
                'bagging_freq': 5,
                'seed': 42,
                'verbosity': -1,
                'lambda_l1': 70,
                'lambda_l2': 5,
            },
            train_data,
            num_boost_round=2000,
            valid_sets=[val_data] if val_data is not None else None
        )

        # ---- Train CatBoost ----
        train_pool = Pool(
            data=X_train,
            label=y_train,
            weight=weight_train,
            cat_features=cat_features
        )
        val_pool = Pool(
            data=X_val,
            label=y_val,
            weight=weight_val,
            cat_features=cat_features
        ) if X_val is not None else None

        self.cat_model = CatBoostRegressor(
            iterations=2000,
            learning_rate=0.12,
            depth=6,
            objective='Huber:delta=12.0',
            l2_leaf_reg=8,
            random_seed=42,
            eval_metric='MAE',
            verbose=100
        )
        self.cat_model.fit(
            train_pool,
            eval_set=val_pool,
            early_stopping_rounds=100,
            use_best_model=True
        )


    def predict(self, X, log_transform=True, dynamic_weight=True, threshold=30, sat_point=70, smooth_factor=0.2, return_weights=False):
        """
        Predict using a stacked ensemble with dynamic, instance-wise weights using sigmoid scaling.

        Weighting Rules
        ---------------
        1. Above threshold (CatBoost as reference):
            - CatBoost weight fixed at 0.6
            - XGBoost weight decays sigmoid-shaped from 0.15 → 0.05
            - LightGBM weight grows sigmoid-shaped from 0.25 → 0.35
            - Saturation occurs near `sat_point`
        2. Below threshold:
            - CatBoost weight grows sigmoid-shaped 0.30 → 0.55 near threshold
            - XGBoost weight decays sigmoid-shaped 0.45 → 0.25 farther below threshold
            - LightGBM weight grows sigmoid-shaped 0.25 → 0.30 near threshold

        Sigmoid scaling ensures smooth transitions instead of abrupt linear changes.

        Parameters
        ----------
        X : pd.DataFrame or np.array
            Features for prediction.
        log_transform : bool
            If True, apply log1p to stabilize high-value predictions.
        dynamic_weight : bool
            If True, use instance-wise weights based on CatBoost prediction.
        threshold : float
            Threshold separating low/high predictions.
        sat_point : float
            Point where above-threshold weights saturate (~70).
        smooth_factor : float
            Controls the sharpness of the sigmoid transition.

        Returns
        -------
        np.array
            Blended predictions.
        pd.DataFrame
            Weights used for the three models.
        """
        if isinstance(X, pd.DataFrame):
            if self.feature_order_list is not None:
                # Reorder columns automatically
                X = X[self.feature_order_list]
                # for col in self.cat_features:
                #     X[col] = X[col].astype("category")
        elif isinstance(X, np.ndarray):
            warnings.warn(
                    "Predicting with NumPy array: assumes column order matches training order. "
                    "Safer to use DataFrame with feature names."
                )
            
            
        # Base model predictions
        pred_xgb = self.xgb_model.predict(X)
        pred_lgb = self.lgb_model.predict(X)
        pred_cat = self.cat_model.predict(X)
        
        if self.main_model == 'ensemble':

            # Log-space transform if needed
            if log_transform:
                pred_xgb = np.log1p(pred_xgb)
                pred_lgb = np.log1p(pred_lgb)
                pred_cat = np.log1p(pred_cat)
                threshold = np.log1p(threshold)
                sat_point = np.log1p(sat_point)

            if dynamic_weight:
                blended_preds = []
                weights = []

                for px, pl, pc in zip(pred_xgb, pred_lgb, pred_cat):
                    if pc >= threshold:
                        # Above threshold: sigmoid scales XGB/LGB weights from threshold → sat_point
                        sig = 1 / (1 + np.exp(-smooth_factor * (pc - threshold)))  # sigmoid at current pc
                        sig_sat = 1 / (1 + np.exp(-smooth_factor * (sat_point - threshold)))  # sigmoid at saturation
                        factor = (sig - 0.5) / (sig_sat - 0.5)  # scale so 0 → threshold, 1 → sat_point
                        factor = np.clip(factor, 0, 1)

                        w_cat = 0.6
                        w_xgb = 0.15 - 0.10 * factor  # decays 0.15 → 0.05
                        w_lgb = 0.25 + 0.10 * factor  # grows 0.25 → 0.35

                    else:
                        # Below threshold: sigmoid scales weights from 0 → threshold
                        sig = 1 / (1 + np.exp(-smooth_factor * (pc)))       # raw sigmoid
                        sig_min = 1 / (1 + np.exp(-smooth_factor * 0))      # sigmoid at 0
                        sig_max = 1 / (1 + np.exp(-smooth_factor * threshold))  # sigmoid at threshold
                        sig_scaled = (sig - sig_min) / (sig_max - sig_min)  # scale 0 → 1
                        sig_scaled = np.clip(sig_scaled, 0, 1)

                        w_cat = 0.30 + 0.25 * sig_scaled   # grows 0.30 → 0.55
                        w_xgb = 0.45 - 0.20 * sig_scaled   # decays 0.45 → 0.25
                        w_lgb = 0.25 + 0.05 * sig_scaled   # grows 0.25 → 0.30

                    # Normalize weights
                    total = w_cat + w_xgb + w_lgb
                    w_cat, w_xgb, w_lgb = w_cat/total, w_xgb/total, w_lgb/total
                    weights.append([w_xgb, w_lgb, w_cat])
                    
                    # Weighted prediction
                    blended_preds.append(w_cat * pc + w_xgb * px + w_lgb * pl)
                
                weight_df = pd.DataFrame(weights, columns=['XGBoost','LightGBM','CatBoost'])
                pred_blend = np.array(blended_preds)

            else:
                # Simple average
                pred_blend = (pred_xgb + pred_lgb + pred_cat) / 3

            # Convert back from log-space if applied
            if log_transform:
                pred_blend = np.expm1(pred_blend)
            
            if return_weights:
                return (pred_blend,weight_df)
            else:
                return pred_blend
        
        elif self.main_model == 'XGBoost':
            return pred_xgb
        elif self.main_model == 'LightGBM':
            return pred_lgb
        elif self.main_model == 'CatBoost':
            return pred_cat
        else:
            return None
            

    def evaluate(self, X, y_true):
        """
        Evaluate the ensemble model on a dataset.

        Parameters
        ----------
        X : pd.DataFrame or np.array
            Features for evaluation.
        y_true : pd.Series or np.array
            True target values.

        Returns
        -------
        dict
            Dictionary containing RMSE, MAE, and R2 metrics.
        """
        preds = self.predict(X)
        rmse = root_mean_squared_error(y_true, preds)
        mae = mean_absolute_error(y_true, preds)
        r2 = r2_score(y_true, preds)
        return {'RMSE': rmse, 'MAE': mae, 'R2': r2}
    
    def eval_metrics(self, y_true, y_pred):
        rmse = root_mean_squared_error(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        r2 = r2_score(y_true, y_pred)
        return {'RMSE': rmse, 'MAE': mae, 'R2': r2}
    
    def _extract_importance(self, model, model_name):
        """Helper to get importance + feature names for any base model."""
        if model is None:
            raise ValueError(f"{model_name} model is not trained or assigned.")

        if model_name == "xgb":
            # XGBoost can be sklearn wrapper or Booster
            try:
                imp = model.feature_importances_
                names = getattr(model, "feature_names_in_", np.arange(len(imp)))
            except AttributeError:
                imp_dict = model.get_score(importance_type="weight")
                names, imp = zip(*imp_dict.items())
                imp = np.array(imp)
        elif model_name == "lgb":
            try:
                imp = model.feature_importance(importance_type="split")
                names = model.feature_name()
            except AttributeError:
                imp = model.feature_importances_
                names = getattr(model, "feature_names_in_", np.arange(len(imp)))
        elif model_name == "cat":
            try:
                imp = model.get_feature_importance()
                names = model.feature_names_
            except AttributeError:
                imp = model.feature_importances_
                names = getattr(model, "feature_names_in_", np.arange(len(imp)))
        else:
            raise ValueError(f"Unknown model name {model_name}")

        return np.array(imp, dtype=float), np.array(names)

    def get_feature_importance(self, model_name: str = "average", normalize: bool = True, percentage: bool = False, weights=None):
        """
        Get feature importance from base models or their weighted average.

        Parameters
        ----------
        model_name : str, default="average"
            - "average": return importance across all models (with weighted average column)
            - "xgb", "lgb", "cat": return importance from that specific model
        normalize : bool, default=True
            Whether to normalize importances so they sum to 1 for each model
            (before averaging in case of "average").
        percentage : bool, default=False
            Whether to scale importances to percentages (0–100).
            - For "average": returns DataFrame with each model + weighted average.
            - For single model: returns Series.
        weights : list of float or None, default=None
            Weights for ["xgb", "lgb", "cat"] when computing the average.
            - If None, defaults to equal weights for available models.
            - Length must equal the number of models used.

        Returns
        -------
        pd.DataFrame or pd.Series
            - If model_name="average": DataFrame with each model + weighted average.
            - If specific model: Series with feature importances.
        """
        models = {
            "xgb": self.xgb_model,
            "lgb": self.lgb_model,
            "cat": self.cat_model
        }

        if model_name == "average":
            df_list = []
            available_models = []
            for name, model in models.items():
                if model is None:
                    continue
                imp, names = self._extract_importance(model, name)
                imp_series = pd.Series(imp, index=names)

                if normalize or percentage:
                    imp_series = imp_series / imp_series.sum()
                if percentage:
                    imp_series = imp_series * 100

                df = pd.DataFrame({name: imp_series})
                df_list.append(df)
                available_models.append(name)

            if not df_list:
                raise ValueError("No fitted models found with feature importance.")

            # Merge on feature names
            all_importances = pd.concat(df_list, axis=1).fillna(0)

            # Handle weights
            if weights is None:
                weights = [1.0] * len(available_models)
            if len(weights) != len(available_models):
                raise ValueError(f"Length of weights ({len(weights)}) does not match number of available models ({len(available_models)}).")

            weights = np.array(weights, dtype=float)
            weights = weights / weights.sum()  # normalize weights to sum = 1

            # Compute weighted average
            all_importances["average"] = (all_importances[available_models] * weights).sum(axis=1)

            # Sort by average importance
            all_importances = all_importances.sort_values("average", ascending=False)

            return all_importances

        else:
            if model_name not in models:
                raise ValueError(f"Invalid model_name '{model_name}'. Choose from 'xgb', 'lgb', 'cat', or 'average'.")
            model = models[model_name]
            if model is None:
                raise ValueError(f"{model_name} model is not trained or assigned.")
            imp, names = self._extract_importance(model, model_name)
            imp_series = pd.Series(imp, index=names, name=f"{model_name}_importance").sort_values(ascending=False)

            if normalize or percentage:
                imp_series = imp_series / imp_series.sum()
            if percentage:
                imp_series = imp_series * 100

            return imp_series
    def save_model(self, save_dir: str = "models", prefix: str = "v1"):
        """
        Save trained models (XGBoost, LightGBM, CatBoost) and metadata.

        Parameters
        ----------
        save_dir : str, default="models"
            Directory to save the models.
        prefix : str, default="v1"
            Prefix for filenames.
        """
        os.makedirs(save_dir, exist_ok=True)

        # Save XGBoost
        if self.xgb_model is not None:
            self.xgb_model.save_model(os.path.join(save_dir, f"{prefix}_xgb.json"))

        # Save LightGBM
        if self.lgb_model is not None:
            self.lgb_model.save_model(os.path.join(save_dir, f"{prefix}_lgb.txt"))

        # Save CatBoost
        if self.cat_model is not None:
            self.cat_model.save_model(os.path.join(save_dir, f"{prefix}_cat.cbm"))

        # Save metadata (like which model is primary, cat_features)
        metadata = {
            "main_model": self.main_model,
            "cat_features": self.cat_features,
            "feature_order_list": self.feature_order_list
        }
        joblib.dump(metadata, os.path.join(save_dir, f"{prefix}_meta.pkl"))

        print(f"Models saved successfully in '{save_dir}'")

    def load_model(self, load_dir: str = None, prefix: str = "reclaim"):
        """
        Load trained models (XGBoost, LightGBM, CatBoost) and metadata.

        Parameters
        ----------
        load_dir : str, optional
            Directory where models are stored.
            If None, defaults to the installed package's `pretrained_model` folder.
        prefix : str, default="reclaim"
            Prefix for filenames.
        """
        if load_dir is None:
            # Default: look inside the package directory
            package_dir = os.path.dirname(__file__)  # folder of this file
            load_dir = os.path.join(package_dir, "pretrained_model")

        # Load XGBoost
        xgb_path = os.path.join(load_dir, f"{prefix}_xgb.pkl")
        if os.path.exists(xgb_path):
            import xgboost as xgb
            self.xgb_model = joblib.load(xgb_path)

        # Load LightGBM
        lgb_path = os.path.join(load_dir, f"{prefix}_lgb.pkl")
        if os.path.exists(lgb_path):
            import lightgbm as lgb
            self.lgb_model = joblib.load(lgb_path)

        # Load CatBoost
        cat_path = os.path.join(load_dir, f"{prefix}_cat.cbm")
        if os.path.exists(cat_path):
            from catboost import CatBoostRegressor
            self.cat_model = CatBoostRegressor()
            self.cat_model.load_model(cat_path)

        # Load metadata
        meta_path = os.path.join(load_dir, f"{prefix}_meta.pkl")
        if os.path.exists(meta_path):
            metadata = joblib.load(meta_path)
            self.main_model = metadata.get("main_model", "ensemble")
            self.cat_features = metadata.get("cat_features", None)
            self.feature_order_list = metadata.get("feature_order_list", None)

        print(f"Models loaded successfully from '{load_dir}'")