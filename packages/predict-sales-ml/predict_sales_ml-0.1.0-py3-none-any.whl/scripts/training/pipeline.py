import logging
import os
from typing import Optional, Dict, Any
import pandas as pd
import mlflow

from dotenv import load_dotenv

from scripts.models.base import BaseModel
from scripts.utils_validation import (
    BaselineFeatureExtractor,
    TimeSeriesValidator,
    create_submission,
)

from scripts.training.trainer import ModelTrainer
from scripts.modeling_config import FILES, SUBMISSION_CONFIG

logger = logging.getLogger(__name__)


class TrainingPipeline:
    """
    Pipeline для обучения моделей: подготовка данных, обучение, оценка, submission.

    Инкапсулирует весь процесс обучения модели от загрузки данных
    до создания submission файла.
    """

    def __init__(
        self,
        model: BaseModel,
        validator: TimeSeriesValidator,
        feature_extractor: BaselineFeatureExtractor,
        mlflow_run_name: Optional[str] = None,
        clip_min: float = 0.0,
        clip_max: float = 20.0,
    ):
        """
        Инициализирует TrainingPipeline.

        Args:
            model: Модель для обучения (наследник BaseModel)
            validator: Валидатор временных рядов
            feature_extractor: Экстрактор фичей
            mlflow_run_name: Имя MLflow run (если None, используется имя модели)
            clip_min, clip_max: Границы для обрезки предсказаний
        """
        self.model = model
        self.validator = validator
        self.feature_extractor = feature_extractor
        self.mlflow_run_name = mlflow_run_name or f"train_{model.name}"
        self.clip_min = clip_min
        self.clip_max = clip_max

        self.datasets: Optional[Dict[str, pd.DataFrame]] = None
        self.trainer: Optional[ModelTrainer] = None
        self.evaluation_results: Optional[Dict[str, Any]] = None

    def prepare_data(self, run_leak_checks: bool = True) -> Dict[str, pd.DataFrame]:
        """
        Подготавливает train/val/test датасеты.

        Args:
            run_leak_checks: Запускать проверки на data leakage

        Returns:
            dict с ключами: X_train, y_train, X_val, y_val, X_test, y_test
        """
        logger.info("Подготовка данных...")
        datasets = self.feature_extractor.prepare_datasets(
            validator=self.validator,
            run_leak_checks=run_leak_checks,
        )
        self.datasets = datasets

        logger.info(f"Train: {len(datasets['X_train']):,} записей")
        if datasets["X_val"] is not None:
            logger.info(f"Validation: {len(datasets['X_val']):,} записей")
        if datasets["X_test"] is not None:
            logger.info(f"Test: {len(datasets['X_test']):,} записей")

        return datasets

    def train_and_evaluate(
        self, log_to_mlflow: bool = True, save_model: bool = True, **fit_kwargs
    ) -> Dict[str, Any]:
        """
        Обучает модель и оценивает её.

        Args:
            log_to_mlflow: Логировать в MLflow
            save_model: Сохранять модель в MLflow
            **fit_kwargs: Дополнительные параметры для fit()

        Returns:
            dict с результатами оценки
        """
        if self.datasets is None:
            raise RuntimeError("Данные не подготовлены. Вызовите prepare_data()")

        # Создаем trainer
        self.trainer = ModelTrainer(
            model=self.model,
            validator=self.validator,
            clip_min=self.clip_min,
            clip_max=self.clip_max,
        )

        # Начинаем MLflow run
        if log_to_mlflow:
            mlflow.start_run(run_name=self.mlflow_run_name)

        error_occurred = False
        try:
            # Логируем конфигурацию
            if log_to_mlflow:
                self.trainer.log_config_to_mlflow(
                    X_train=self.datasets["X_train"],
                    feature_names=self.feature_extractor.get_feature_list(),
                )

            # Обучаем модель
            self.trainer.train(
                X_train=self.datasets["X_train"],
                y_train=self.datasets["y_train"],
                X_val=self.datasets["X_val"],
                y_val=self.datasets["y_val"],
                **fit_kwargs,
            )

            # Оцениваем модель
            self.evaluation_results = self.trainer.evaluate(
                X_val=self.datasets["X_val"],
                y_val=self.datasets["y_val"],
                X_test=self.datasets["X_test"],
                y_test=self.datasets["y_test"],
                log_to_mlflow=log_to_mlflow,
            )

            # Сохраняем модель
            if save_model and log_to_mlflow:
                self.trainer.save_model_to_mlflow(artifact_path="model")

        except Exception as e:
            error_occurred = True
            # Логируем ошибку в MLflow
            if log_to_mlflow:
                try:
                    mlflow.log_param("error", str(e))
                    mlflow.log_param("error_type", type(e).__name__)
                    import traceback

                    mlflow.log_text(traceback.format_exc(), "error_traceback.txt")
                    # Помечаем run как failed
                    mlflow.set_tag("mlflow.runStatus", "Failed")
                except Exception:
                    pass  # Если не удалось залогировать, продолжаем

            logger.error(f"Ошибка при обучении модели: {e}", exc_info=True)
            # Пробрасываем исключение дальше
            raise

        finally:
            if log_to_mlflow:
                # Если была ошибка, помечаем run как failed
                if error_occurred:
                    try:
                        mlflow.end_run(status="FAILED")
                    except Exception:
                        # Если end_run не поддерживает status, просто вызываем его
                        mlflow.end_run()
                else:
                    mlflow.end_run()

        return self.evaluation_results

    def create_submission(
        self,
        submission_filename: Optional[str] = None,
        test_encoded_path: Optional[str] = None,
    ) -> pd.DataFrame:
        """
        Создает Kaggle submission файл.

        Args:
            submission_filename: Имя файла для submission
            test_encoded_path: Путь к test данным (если None, берется из конфига)

        Returns:
            DataFrame с submission
        """
        if not self.model.is_trained:
            raise RuntimeError("Модель не обучена. Вызовите train_and_evaluate()")

        if submission_filename is None:
            submission_filename = f"{self.model.name}_submission.csv"

        if test_encoded_path is None:
            test_encoded_path = FILES["test_encoded"]

        model_for_prediction = self.model
        if hasattr(self.model, "model") and self.model.model is not None:
            model_for_prediction = self.model.model

        submission = create_submission(
            model=model_for_prediction,
            feature_extractor=self.feature_extractor,
            test_encoded_path=test_encoded_path,
            output_path=SUBMISSION_CONFIG["output_dir"],
            production_month=self.validator.production_month,
            clip_min=self.clip_min,
            clip_max=self.clip_max,
            submission_filename=submission_filename,
        )

        logger.info(f"Submission файл создан: {submission_filename}")
        return submission

    def run_full_pipeline(
        self,
        run_leak_checks: bool = True,
        create_submission: bool = True,
        submission_filename: Optional[str] = None,
        **fit_kwargs,
    ) -> Dict[str, Any]:
        """
        Запускает полный pipeline: подготовка данных → обучение → оценка → submission.

        Args:
            run_leak_checks: Запускать проверки на data leakage
            create_submission: Создавать submission файл
            submission_filename: Имя файла для submission
            **fit_kwargs: Дополнительные параметры для fit()

        Returns:
            dict с результатами оценки
        """
        logger.info(f"Запуск полного pipeline для модели: {self.model.name}")

        # 1. Подготовка данных
        self.prepare_data(run_leak_checks=run_leak_checks)

        # 2. Обучение и оценка
        results = self.train_and_evaluate(**fit_kwargs)

        # 3. Создание submission
        if create_submission:
            self.create_submission(submission_filename=submission_filename)

        logger.info("Pipeline завершен успешно!")

        return results


def setup_mlflow(
    tracking_uri: Optional[str] = None,
    experiment_name: Optional[str] = None,
):
    """
    Настраивает MLflow.

    Args:
        tracking_uri: URI для MLflow tracking (если None, берется из .env)
        experiment_name: Имя эксперимента (если None, берется из .env)
    """
    load_dotenv()

    if "MLFLOW_USER" not in os.environ:
        os.environ["MLFLOW_USER"] = "Eugene Malyukevich"

    if tracking_uri is None:
        tracking_uri = os.environ.get("MLFLOW_TRACKING_URI")

    if experiment_name is None:
        experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME")

    logger.info(f"MLFLOW_TRACKING_URI={tracking_uri}")
    logger.info(f"MLFLOW_EXPERIMENT_NAME={experiment_name}")

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)
