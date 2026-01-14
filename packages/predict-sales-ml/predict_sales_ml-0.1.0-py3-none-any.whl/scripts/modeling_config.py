from pathlib import Path

DATA_PATH = Path("data/processed")

VALIDATION_CONFIG = {
    "train_months": (0, 30),
    "val_months": (31, 32),
    "test_month": 33,
    "production_month": 34,
}

FILES = {
    "train_encoded": DATA_PATH / "sales_monthly_with_features_encoded.parquet",
    "test_encoded": DATA_PATH / "test_enriched_encoded.parquet",
}

LIGHTGBM_PARAMS = {
    "n_estimators": 1850,
    "learning_rate": 0.01108487589254321,
    "num_leaves": 899,
    "min_child_samples": 70,
    "min_child_weight": 0.005763751814926363,
    "max_bin": 140,
    "cat_smooth": 11,
    "subsample_for_bin": 300000,
    "min_data_in_bin": 7,
    "colsample_bytree": 0.85,
    "subsample": 0.75,
    "subsample_freq": 9,
    "random_state": 42,
    "n_jobs": -1,
}

XGBOOST_PARAMS = {
    "n_estimators": 1000,
    "learning_rate": 0.01,
    "max_depth": 8,
    "min_child_weight": 3,
    "subsample": 0.8,
    "colsample_bytree": 0.8,
    "gamma": 0.1,
    "reg_alpha": 0.1,
    "reg_lambda": 1,
    "random_state": 42,
    "n_jobs": -1,
    "tree_method": "hist",
}

# Stacking конфигурация
STACKING_CONFIG = {
    "base_models": [
        {
            "type": "xgboost",
            "name": "xgb_1",
            "params": XGBOOST_PARAMS,
        },
        {
            "type": "xgboost",
            "name": "xgb_2",
            "params": {**XGBOOST_PARAMS, "random_state": 43},  # Другой seed
        },
        {
            "type": "lightgbm",
            "name": "lgbm_1",
            "params": LIGHTGBM_PARAMS,
        },
    ],
    "meta_model": {
        "class": "Ridge",  # или "LinearRegression", "ElasticNet"
        "params": {"alpha": 0.1},
    },
    "use_oof": True,
    "n_folds": 5,
    "cv_type": "timeseries",  # или "kfold"
    "random_state": 42,
}

SUBMISSION_CONFIG = {
    "clip_min": 0.0,
    "clip_max": 20.0,
    "output_dir": Path("submissions"),
}
