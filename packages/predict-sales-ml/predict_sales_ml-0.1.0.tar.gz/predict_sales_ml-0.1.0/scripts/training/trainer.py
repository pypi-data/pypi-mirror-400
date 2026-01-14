import logging
import time
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
import mlflow
import mlflow.lightgbm
import mlflow.xgboost
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from tqdm import tqdm

from scripts.models.base import BaseModel
from scripts.utils_validation import TimeSeriesValidator

import pickle
import tempfile
import os
import traceback

logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Класс для обучения и оценки моделей с MLflow логированием.

    Инкапсулирует логику обучения, оценки и сохранения моделей,
    работая с моделями через интерфейс BaseModel.
    """

    def __init__(
        self,
        model: BaseModel,
        validator: Optional[TimeSeriesValidator] = None,
        clip_min: float = 0.0,
        clip_max: float = 20.0,
    ):
        """
        Инициализирует ModelTrainer.

        Args:
            model: Модель для обучения (наследник BaseModel)
            validator: Валидатор временных рядов (опционально)
            clip_min, clip_max: Границы для обрезки предсказаний
        """
        self.model = model
        self.validator = validator
        self.clip_min = clip_min
        self.clip_max = clip_max

    def train(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        **fit_kwargs,
    ) -> BaseModel:
        """
        Обучает модель на предоставленных данных.

        Args:
            X_train: Обучающие данные
            y_train: Целевая переменная
            X_val: Валидационные данные (опционально)
            y_val: Целевая переменная для валидации
            **fit_kwargs: Дополнительные параметры для fit()

        Returns:
            Обученная модель
        """
        logger.info(f"Начало обучения модели: {self.model.name}")

        start_time = time.time()

        # Обучаем модель
        self.model.fit(X_train, y_train, X_val=X_val, y_val=y_val, **fit_kwargs)

        elapsed_time = time.time() - start_time
        logger.info(f"Обучение завершено за {elapsed_time:.2f} секунд")

        # Логируем время обучения в MLflow (если есть активный run)
        try:
            mlflow.log_metric("training_time_seconds", float(elapsed_time))
        except Exception:
            pass

        return self.model

    def evaluate(
        self,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        X_test: Optional[pd.DataFrame] = None,
        y_test: Optional[pd.Series] = None,
        log_to_mlflow: bool = True,
    ) -> Dict[str, Any]:
        """
        Оценивает модель на validation и/или test данных.

        Args:
            X_val, y_val: Валидационные данные
            X_test, y_test: Тестовые данные
            log_to_mlflow: Логировать метрики в MLflow

        Returns:
            dict с метриками и feature importance
        """
        if not self.model.is_trained:
            raise ValueError("Модель не обучена. Вызовите train() перед evaluate()")

        results = {
            "metrics_val": None,
            "metrics_test": None,
            "feature_importance": None,
        }

        def calculate_rmse(y_true, y_pred):
            """Вычисляет RMSE."""
            mse = mean_squared_error(y_true, y_pred)
            return np.sqrt(mse)

        # Validation
        if X_val is not None and y_val is not None:
            logger.info("Оценка на validation данных...")

            with tqdm(total=1, desc="Predicting validation") as pbar:
                y_val_pred = self.model.predict(X_val)
                y_val_pred = np.clip(y_val_pred, self.clip_min, self.clip_max)
                pbar.update(1)

            rmse_val = calculate_rmse(y_val, y_val_pred)
            mae_val = mean_absolute_error(y_val, y_val_pred)
            r2_val = r2_score(y_val, y_val_pred)

            metrics_val = {
                "rmse": float(rmse_val),
                "mae": float(mae_val),
                "r2": float(r2_val),
                "y_pred_min": float(y_val_pred.min()),
                "y_pred_max": float(y_val_pred.max()),
                "y_true_min": float(y_val.min()),
                "y_true_max": float(y_val.max()),
            }
            results["metrics_val"] = metrics_val
            print(f"Validation RMSE: {rmse_val:.4f}")
            print(f"Validation MAE:  {mae_val:.4f}")
            print(f"Validation R²:   {r2_val:.4f}")

            # Логируем метрики валидации в MLflow
            if log_to_mlflow:
                try:
                    mlflow.log_metric("rmse_val", metrics_val["rmse"])
                    mlflow.log_metric("mae_val", metrics_val["mae"])
                    mlflow.log_metric("r2_val", metrics_val["r2"])
                except Exception as e:
                    logger.warning(
                        f"Не удалось залогировать validation метрики в MLflow: {e}"
                    )

        # Test
        if X_test is not None and y_test is not None:
            logger.info("Оценка на test данных...")

            with tqdm(total=1, desc="Predicting test") as pbar:
                y_test_pred = self.model.predict(X_test)
                y_test_pred = np.clip(y_test_pred, self.clip_min, self.clip_max)
                pbar.update(1)

            rmse_test = calculate_rmse(y_test, y_test_pred)
            mae_test = mean_absolute_error(y_test, y_test_pred)
            r2_test = r2_score(y_test, y_test_pred)

            metrics_test = {
                "rmse": float(rmse_test),
                "mae": float(mae_test),
                "r2": float(r2_test),
                "y_pred_min": float(y_test_pred.min()),
                "y_pred_max": float(y_test_pred.max()),
                "y_true_min": float(y_test.min()),
                "y_true_max": float(y_test.max()),
            }
            results["metrics_test"] = metrics_test
            print(f"Test RMSE: {rmse_test:.4f}")
            print(f"Test MAE:  {mae_test:.4f}")
            print(f"Test R²:   {r2_test:.4f}")

            if log_to_mlflow:
                try:
                    mlflow.log_metric("rmse_test", metrics_test["rmse"])
                    mlflow.log_metric("mae_test", metrics_test["mae"])
                    mlflow.log_metric("r2_test", metrics_test["r2"])
                except Exception as e:
                    logger.warning(f"Не удалось залогировать метрики в MLflow: {e}")

        # Feature importance
        feature_importance = self.model.get_feature_importance()
        if feature_importance is not None:
            results["feature_importance"] = feature_importance
            print("Топ-20 важных фичей:")
            print(feature_importance.head(20).to_string(index=False))

        return results

    def log_config_to_mlflow(
        self,
        X_train: pd.DataFrame,
        feature_names: Optional[List[str]] = None,
    ):
        """
        Логирует конфигурацию в MLflow.

        Args:
            X_train: Обучающие данные
            feature_names: Список названий фичей (опционально)
        """
        try:
            # Базовая информация о модели
            mlflow.log_param("model_name", self.model.name)
            mlflow.log_param("model_type", self.model.__class__.__name__)
            mlflow.log_param("n_train_samples", int(X_train.shape[0]))
            mlflow.log_param("n_features", int(X_train.shape[1]))

            # Логируем гиперпараметры модели
            for key, value in self.model.params.items():
                try:
                    mlflow.log_param(key, value)
                except Exception:
                    mlflow.log_param(key, str(value))

            # Логируем конфигурацию валидации
            if self.validator is not None:
                mlflow.log_param(
                    "train_months",
                    f"{self.validator.train_months[0]}-{self.validator.train_months[1]}",
                )
                mlflow.log_param(
                    "val_months",
                    f"{self.validator.val_months[0]}-{self.validator.val_months[1]}",
                )
                mlflow.log_param("test_month", int(self.validator.test_month))
                mlflow.log_param(
                    "production_month", int(self.validator.production_month)
                )

            # Логируем best iteration, если доступно
            best_iter = self.model.get_best_iteration()
            if best_iter is not None:
                mlflow.log_param("best_iteration", best_iter)

        except Exception as e:
            logger.warning(f"Не удалось залогировать конфигурацию в MLflow: {e}")

    def save_model_to_mlflow(self, artifact_path: str):
        """
        Сохраняет модель в MLflow.

        Args:
            name: Путь для сохранения модели в MLflow
        """
        if not self.model.is_trained:
            raise RuntimeError("Модель не обучена. Обучите модель перед сохранением.")

        logger.info(f"Сохранение модели {self.model.name} в MLflow...")
        logger.info(f"Tracking URI: {mlflow.get_tracking_uri()}")

        try:
            active_run = mlflow.active_run()
            if active_run:
                logger.info(f"Active run ID: {active_run.info.run_id}")
            else:
                logger.warning("Нет активного MLflow run")

            # Определяем тип модели и используем соответствующий logger
            model_type = self.model.__class__.__name__

            if "LightGBM" in model_type:
                # Для LightGBM моделей используем mlflow.lightgbm
                # Нужно получить sklearn-модель из обертки
                if hasattr(self.model, "model") and self.model.model is not None:
                    mlflow.lightgbm.log_model(
                        self.model.model, artifact_path=artifact_path
                    )
                else:
                    raise RuntimeError("LightGBM модель не инициализирована")

            elif "XGBoost" in model_type:
                # Для XGBoost моделей используем mlflow.xgboost
                if hasattr(self.model, "model") and self.model.model is not None:
                    mlflow.xgboost.log_model(
                        self.model.model, artifact_path=artifact_path
                    )
                else:
                    raise RuntimeError("XGBoost модель не инициализирована")

            elif "Stacking" in model_type:
                # Для stacking моделей сохраняем через pickle или pyfunc
                with tempfile.TemporaryDirectory() as tmpdir:
                    model_path = os.path.join(tmpdir, "model.pkl")
                    with open(model_path, "wb") as f:
                        pickle.dump(self.model, f)
                    mlflow.log_artifacts(tmpdir, artifact_path=artifact_path)

            else:
                # Для других моделей используем generic log_model
                if hasattr(self.model, "model") and self.model.model is not None:
                    mlflow.sklearn.log_model(
                        self.model.model, artifact_path=artifact_path
                    )
                else:
                    with tempfile.TemporaryDirectory() as tmpdir:
                        model_path = os.path.join(tmpdir, "model.pkl")
                        with open(model_path, "wb") as f:
                            pickle.dump(self.model, f)
                        mlflow.log_artifacts(tmpdir, artifact_path=artifact_path)

            logger.info(f"Модель успешно сохранена в MLflow: {artifact_path}")

        except Exception as e:
            logger.warning(f"Не удалось сохранить модель в MLflow: {e}")
            logger.warning(f"Тип ошибки: {type(e).__name__}")
            logger.warning(f"Traceback:\n{traceback.format_exc()}")
            # Не пробрасываем исключение, чтобы не ломать весь pipeline
            # Ошибка сохранения модели не критична для обучения и оценки
