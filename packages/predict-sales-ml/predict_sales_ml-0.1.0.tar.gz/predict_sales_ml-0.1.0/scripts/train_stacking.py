"""
Скрипт для обучения stacking модели.

Использование:
    python scripts/train_stacking.py
    python scripts/train_stacking.py --run-name my_stacking_run
    python scripts/train_stacking.py --meta-model Ridge --meta-alpha 0.1
    python scripts/train_stacking.py --n-folds 10 --cv-type timeseries
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import mlflow

from sklearn.linear_model import LinearRegression, Ridge, ElasticNet
from scripts.models.stacking_model import StackingModel
from scripts.models.registry import create_model_from_registry
from scripts.training.pipeline import TrainingPipeline, setup_mlflow
from scripts.utils_validation import BaselineFeatureExtractor, TimeSeriesValidator
from scripts.modeling_config import (
    FILES,
    VALIDATION_CONFIG,
    SUBMISSION_CONFIG,
    STACKING_CONFIG,
    LIGHTGBM_PARAMS,
    XGBOOST_PARAMS,
)

# === logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Регистр мета-моделей
META_MODEL_REGISTRY = {
    "LinearRegression": LinearRegression,
    "Ridge": Ridge,
    "ElasticNet": ElasticNet,
}


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Обучает stacking модель (ансамбль базовых моделей)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Обучить stacking с дефолтной конфигурацией
  python scripts/train_stacking.py

  # Обучить с кастомным именем run
  python scripts/train_stacking.py --run-name stacking_experiment_1

  # Изменить мета-модель
  python scripts/train_stacking.py --meta-model Ridge --meta-alpha 0.1

  # Изменить количество фолдов и тип CV
  python scripts/train_stacking.py --n-folds 10 --cv-type timeseries

  # Добавить/убрать базовые модели
  python scripts/train_stacking.py --base-models xgboost lightgbm

  # Без OOF (не рекомендуется)
  python scripts/train_stacking.py --no-oof

  # Без submission
  python scripts/train_stacking.py --no-submission
        """,
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
        "--base-models",
        type=str,
        nargs="+",
        default=None,
        help="Список базовых моделей (например: xgboost lightgbm). "
        "Если не указано, используется конфигурация из STACKING_CONFIG",
    )

    parser.add_argument(
        "--meta-model",
        type=str,
        choices=list(META_MODEL_REGISTRY.keys()),
        default=None,
        help="Тип мета-модели (LinearRegression, Ridge, ElasticNet)",
    )

    parser.add_argument(
        "--meta-alpha",
        type=float,
        default=None,
        help="Alpha параметр для Ridge/ElasticNet мета-модели",
    )

    parser.add_argument(
        "--n-folds",
        type=int,
        default=None,
        help="Количество фолдов для OOF валидации",
    )

    parser.add_argument(
        "--cv-type",
        type=str,
        choices=["kfold", "timeseries"],
        default=None,
        help="Тип кросс-валидации (kfold или timeseries)",
    )

    parser.add_argument(
        "--no-oof",
        action="store_true",
        help="Не использовать out-of-fold predictions (не рекомендуется)",
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


def create_base_models(
    base_models_config: List[Dict[str, Any]],
) -> List[Any]:
    """
    Создает список базовых моделей из конфигурации.

    Args:
        base_models_config: Список конфигураций базовых моделей

    Returns:
        Список экземпляров базовых моделей
    """
    base_models = []

    for idx, model_config in enumerate(base_models_config):
        model_type = model_config["type"]
        model_name = model_config.get("name", f"{model_type}_{idx + 1}")
        model_params = model_config.get("params", {})

        # Создаем модель через регистр
        model = create_model_from_registry(
            model_type=model_type,
            model_name=model_name,
            custom_params=model_params,
        )

        base_models.append(model)
        logger.info(f"Создана базовая модель {idx + 1}: {model_name} ({model_type})")

    return base_models


def create_stacking_model(args) -> StackingModel:
    """
    Создает stacking модель на основе аргументов и конфигурации.

    Args:
        args: Парсированные аргументы командной строки

    Returns:
        Экземпляр StackingModel
    """
    # Определяем базовые модели
    if args.base_models:
        # Используем указанные модели
        base_models_config = []
        for idx, model_type in enumerate(args.base_models):
            if model_type == "xgboost":
                params = XGBOOST_PARAMS.copy()
                if idx > 0:
                    params["random_state"] = 42 + idx  # Разные seeds
            elif model_type == "lightgbm":
                params = LIGHTGBM_PARAMS.copy()
                if idx > 0:
                    params["random_state"] = 42 + idx
            else:
                raise ValueError(f"Неизвестный тип базовой модели: {model_type}")

            base_models_config.append(
                {
                    "type": model_type,
                    "name": f"{model_type}_{idx + 1}",
                    "params": params,
                }
            )
    else:
        # Используем конфигурацию из STACKING_CONFIG
        base_models_config = STACKING_CONFIG["base_models"]

    # Создаем базовые модели
    base_models = create_base_models(base_models_config)

    # Определяем мета-модель
    if args.meta_model:
        meta_model_class = META_MODEL_REGISTRY[args.meta_model]
        meta_model_params = {}
        if args.meta_alpha is not None:
            meta_model_params["alpha"] = args.meta_alpha
    else:
        # Используем конфигурацию из STACKING_CONFIG
        meta_model_name = STACKING_CONFIG["meta_model"]["class"]
        meta_model_class = META_MODEL_REGISTRY.get(
            meta_model_name,
            LinearRegression,  # Fallback
        )
        meta_model_params = STACKING_CONFIG["meta_model"].get("params", {})

    # Параметры stacking
    use_oof = not args.no_oof if args.no_oof else STACKING_CONFIG.get("use_oof", True)
    n_folds = args.n_folds or STACKING_CONFIG.get("n_folds", 5)
    cv_type = args.cv_type or STACKING_CONFIG.get("cv_type", "kfold")
    random_state = STACKING_CONFIG.get("random_state", 42)

    # Имя модели
    model_name = args.model_name or "stacking_model"

    logger.info("Создание stacking модели:")
    logger.info(f"  Базовых моделей: {len(base_models)}")
    logger.info(f"  Мета-модель: {meta_model_class.__name__}")
    logger.info(f"  OOF: {use_oof}, Фолдов: {n_folds}, CV тип: {cv_type}")

    return StackingModel(
        base_models=base_models,
        meta_model_class=meta_model_class,
        meta_model_params=meta_model_params,
        use_oof=use_oof,
        n_folds=n_folds,
        cv_type=cv_type,
        random_state=random_state,
        name=model_name,
    )


def main():
    """Главная функция."""
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
    print(f"\nКоличество фичей: {len(feature_list)}")

    # Создание stacking модели
    logger.info("Создание stacking модели...")
    stacking_model = create_stacking_model(args)

    # Генерация имени run, если не указано
    run_name = args.run_name
    if run_name is None:
        run_name = f"stacking_{stacking_model.name}"

    # Создание pipeline
    pipeline = TrainingPipeline(
        model=stacking_model,
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
        print("ИТОГОВЫЕ РЕЗУЛЬТАТЫ")

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

        # Вывод информации о вкладе базовых моделей
        if hasattr(stacking_model, "get_meta_model_coefficients"):
            coef_df = stacking_model.get_meta_model_coefficients()
            if coef_df is not None:
                print("\n" + "=" * 60)
                print("Вклад базовых моделей (коэффициенты мета-модели):")
                print("=" * 60)
                print(coef_df.to_string(index=False))

        logger.info("Stacking обучение завершено успешно!")

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
