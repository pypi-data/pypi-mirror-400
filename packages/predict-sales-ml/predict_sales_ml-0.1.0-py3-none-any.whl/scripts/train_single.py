"""
Скрипт для обучения одной модели (LightGBM или XGBoost).

Использование:
    python scripts/train_single.py --model lightgbm
    python scripts/train_single.py --model xgboost --run-name my_xgb_run
    python scripts/train_single.py --model lightgbm --no-submission
"""

import argparse
import logging
import sys
from pathlib import Path

import pandas as pd
import mlflow

from scripts.models.registry import create_model_from_registry, list_available_models
from scripts.training.pipeline import TrainingPipeline, setup_mlflow
from scripts.utils_validation import BaselineFeatureExtractor, TimeSeriesValidator
from scripts.modeling_config import (
    FILES,
    VALIDATION_CONFIG,
    SUBMISSION_CONFIG,
)

# === logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


def parse_args():
    """Парсит аргументы командной строки."""
    available_models = list_available_models()
    models_help = "\n".join([f"  {k}: {v}" for k, v in available_models.items()])

    parser = argparse.ArgumentParser(
        description="Обучает одну модель (LightGBM или XGBoost)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Доступные модели:
{models_help}

Примеры использования:
  # Обучить LightGBM с дефолтными параметрами
  python scripts/train_single.py --model lightgbm

  # Обучить XGBoost с кастомным именем run
  python scripts/train_single.py --model xgboost --run-name my_xgb_experiment

  # Обучить без создания submission файла
  python scripts/train_single.py --model lightgbm --no-submission

  # Обучить без timestamp в имени submission файла
  python scripts/train_single.py --model lightgbm --no-timestamp

  # Обучить без score в имени submission файла
  python scripts/train_single.py --model lightgbm --no-score
        """,
    )

    parser.add_argument(
        "--model",
        type=str,
        choices=list(available_models.keys()),
        required=True,
        help="Тип модели для обучения",
    )

    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Имя MLflow run (если не указано, генерируется автоматически)",
    )

    parser.add_argument(
        "--model-name",
        type=str,
        default=None,
        help="Имя модели (если не указано, используется дефолтное)",
    )

    parser.add_argument(
        "--submission-filename",
        type=str,
        default=None,
        help="Имя файла для submission (если не указано, генерируется автоматически)",
    )

    parser.add_argument(
        "--no-submission",
        action="store_true",
        help="Не создавать submission файл",
    )

    parser.add_argument(
        "--no-timestamp",
        action="store_true",
        help="Не добавлять timestamp в имя submission файла",
    )

    parser.add_argument(
        "--no-score",
        action="store_true",
        help="Не добавлять score в имя submission файла",
    )

    parser.add_argument(
        "--skip-leak-checks",
        action="store_true",
        help="Пропустить проверки на data leakage",
    )

    parser.add_argument(
        "--train-encoded",
        type=Path,
        default=None,
        help=f"Путь к train данным (по умолчанию: {FILES['train_encoded']})",
    )

    parser.add_argument(
        "--test-encoded",
        type=Path,
        default=None,
        help=f"Путь к test данным (по умолчанию: {FILES['test_encoded']})",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Настройка MLflow
    logger.info("Настройка MLflow...")
    setup_mlflow()

    # Загрузка данных
    train_path = args.train_encoded or FILES["train_encoded"]
    logger.info(f"Загрузка train данных из {train_path}...")

    if not train_path.exists():
        logger.error(f"Файл не найден: {train_path}")
        sys.exit(1)

    sales_encoded = pd.read_parquet(train_path)
    logger.info(
        f"Загружено {len(sales_encoded):,} строк, {len(sales_encoded.columns)} столбцов"
    )

    # Инициализация компонентов
    logger.info("Инициализация компонентов...")
    validator = TimeSeriesValidator(**VALIDATION_CONFIG)
    feature_extractor = BaselineFeatureExtractor(features_df=sales_encoded)

    feature_list = feature_extractor.get_feature_list()
    logger.info(f"Количество фичей: {len(feature_list)}")

    # Создание модели через регистр
    logger.info(f"Создание модели: {args.model}")
    model = create_model_from_registry(
        model_type=args.model,
        model_name=args.model_name,
    )

    # Генерация имени run, если не указано
    run_name = args.run_name
    if run_name is None:
        run_name = f"train_{model.name}"

    # Создание pipeline
    pipeline = TrainingPipeline(
        model=model,
        validator=validator,
        feature_extractor=feature_extractor,
        mlflow_run_name=run_name,
        clip_min=SUBMISSION_CONFIG["clip_min"],
        clip_max=SUBMISSION_CONFIG["clip_max"],
    )

    # Запуск pipeline
    try:
        results = pipeline.run_full_pipeline(
            run_leak_checks=not args.skip_leak_checks,
            create_submission=not args.no_submission,
            submission_filename=args.submission_filename,
            include_timestamp=not args.no_timestamp,
            include_score=not args.no_score,
        )

        # Вывод итоговых результатов
        if results.get("metrics_test") is not None:
            test_rmse = results["metrics_test"]["rmse"]
            test_mae = results["metrics_test"]["mae"]
            test_r2 = results["metrics_test"]["r2"]

            print(f"\nTest RMSE: {test_rmse:.4f}")
            print(f"Test MAE:  {test_mae:.4f}")
            print(f"Test R²:   {test_r2:.4f}")

        if results.get("metrics_val") is not None:
            val_rmse = results["metrics_val"]["rmse"]
            print(f"\nValidation RMSE: {val_rmse:.4f}")

        logger.info("Обучение завершено успешно!")

        # Вывод ссылки на MLflow
        try:
            tracking_uri = mlflow.get_tracking_uri()
            if tracking_uri and tracking_uri.startswith("http"):
                print(f"\n📊 MLflow UI: {tracking_uri}")
        except Exception:
            pass

        return 0

    except Exception as e:
        logger.error(f"Ошибка при выполнении pipeline: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
