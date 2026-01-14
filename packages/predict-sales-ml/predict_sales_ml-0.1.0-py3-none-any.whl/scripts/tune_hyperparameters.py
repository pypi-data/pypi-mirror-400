"""
Скрипт для оптимизации гиперпараметров LightGBM с использованием Optuna.

Использование:
    python scripts/tune_hyperparameters.py --model lightgbm --n-trials 100
    python scripts/tune_hyperparameters.py --model lightgbm --n-trials 50 --timeout 3600
    python scripts/tune_hyperparameters.py --model lightgbm --study-name lgbm_optuna_v1
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import json

import pandas as pd
import numpy as np
import optuna
import mlflow
from optuna import Trial
from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_squared_error

from scripts.models.lightgbm_model import LightGBMModel
from scripts.training.pipeline import setup_mlflow
from scripts.utils_validation import BaselineFeatureExtractor, TimeSeriesValidator
from scripts.modeling_config import (
    FILES,
    VALIDATION_CONFIG,
    LIGHTGBM_PARAMS,
)

# === logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Настройка Optuna logging
optuna.logging.set_verbosity(optuna.logging.WARNING)


def objective(
    trial: Trial,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: Optional[pd.DataFrame],
    y_val: Optional[pd.Series],
    base_params: Dict[str, Any],
    n_folds: int = 5,
    use_cv: bool = True,
) -> float:
    """
    Objective функция для Optuna.

    Args:
        trial: Optuna trial объект
        X_train: Обучающие данные
        y_train: Целевая переменная
        X_val: Валидационные данные (если не используется CV)
        y_val: Целевая переменная для валидации
        base_params: Базовые параметры модели
        n_folds: Количество фолдов для CV
        use_cv: Использовать ли кросс-валидацию

    Returns:
        RMSE на валидации (минимизируем)
    """
    # Определяем пространство поиска гиперпараметров
    params = base_params.copy()

    # Основные гиперпараметры для оптимизации
    params["n_estimators"] = trial.suggest_int("n_estimators", 500, 2000, step=50)
    params["learning_rate"] = trial.suggest_float(
        "learning_rate", 0.005, 0.05, log=True
    )
    params["num_leaves"] = trial.suggest_int(
        "num_leaves", 31, 1023, step=31
    )  # Исправлено: 1023 вместо 1024
    params["min_child_samples"] = trial.suggest_int(
        "min_child_samples", 5, 95, step=5
    )  # Исправлено: 95 вместо 96 (кратно step=5)
    params["min_child_weight"] = trial.suggest_float(
        "min_child_weight", 0.001, 0.1, log=True
    )
    params["max_bin"] = trial.suggest_int("max_bin", 100, 300, step=10)
    params["cat_smooth"] = trial.suggest_int(
        "cat_smooth", 1, 96, step=5
    )  # Исправлено: 96 вместо 100 (кратно step=5)
    params["colsample_bytree"] = trial.suggest_float(
        "colsample_bytree", 0.6, 1.0, step=0.05
    )
    params["subsample"] = trial.suggest_float("subsample", 0.5, 1.0, step=0.05)
    params["subsample_freq"] = trial.suggest_int("subsample_freq", 1, 10, step=1)

    # Фиксированные параметры
    params["objective"] = "regression"
    params["metric"] = "rmse"
    params["verbose"] = -1
    params["random_state"] = 42

    if use_cv:
        # Используем TimeSeriesSplit для кросс-валидации
        tscv = TimeSeriesSplit(n_splits=n_folds)
        cv_scores = []

        for fold, (train_idx, val_idx) in enumerate(tscv.split(X_train)):
            # Разделяем данные на фолды
            X_train_fold = X_train.iloc[train_idx]
            y_train_fold = y_train.iloc[train_idx]
            X_val_fold = X_train.iloc[val_idx]
            y_val_fold = y_train.iloc[val_idx]

            # Создаем и обучаем модель
            model = LightGBMModel(
                params=params, name=f"lgbm_trial_{trial.number}_fold_{fold}"
            )
            model.fit(
                X_train_fold,
                y_train_fold,
                X_val=X_val_fold,
                y_val=y_val_fold,
                stopping_rounds=50,
                verbose=False,
            )

            # Предсказания и оценка
            y_pred = model.predict(X_val_fold)
            y_pred = np.clip(y_pred, 0.0, 20.0)  # Clip как в финальной модели

            rmse = np.sqrt(mean_squared_error(y_val_fold, y_pred))
            cv_scores.append(rmse)

        # Возвращаем средний RMSE по фолдам
        mean_rmse = np.mean(cv_scores)
        logger.info(
            f"Trial {trial.number}: CV RMSE = {mean_rmse:.6f} (folds: {[f'{s:.6f}' for s in cv_scores]})"
        )
        return mean_rmse
    else:
        # Используем фиксированную валидацию
        if X_val is None or y_val is None:
            raise ValueError("X_val и y_val должны быть указаны, если use_cv=False")

        model = LightGBMModel(params=params, name=f"lgbm_trial_{trial.number}")
        model.fit(
            X_train,
            y_train,
            X_val=X_val,
            y_val=y_val,
            stopping_rounds=50,
            verbose=False,
        )

        y_pred = model.predict(X_val)
        y_pred = np.clip(y_pred, 0.0, 20.0)

        rmse = np.sqrt(mean_squared_error(y_val, y_pred))
        logger.info(f"Trial {trial.number}: Validation RMSE = {rmse:.6f}")
        return rmse


def parse_args():
    """Парсит аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Оптимизация гиперпараметров модели с Optuna",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  # Базовый запуск с 100 trials
  python scripts/tune_hyperparameters.py --model lightgbm --n-trials 100

  # С таймаутом (1 час)
  python scripts/tune_hyperparameters.py --model lightgbm --n-trials 200 --timeout 3600

  # С кастомным именем study
  python scripts/tune_hyperparameters.py --model lightgbm --study-name lgbm_optuna_v1

  # Без кросс-валидации (использует фиксированную валидацию)
  python scripts/tune_hyperparameters.py --model lightgbm --no-cv

  # С меньшим количеством фолдов
  python scripts/tune_hyperparameters.py --model lightgbm --n-folds 3
        """,
    )

    parser.add_argument(
        "--model",
        type=str,
        choices=["lightgbm", "xgboost"],
        default="lightgbm",
        help="Тип модели для оптимизации (по умолчанию: lightgbm)",
    )

    parser.add_argument(
        "--n-trials",
        type=int,
        default=100,
        help="Количество trials для Optuna (по умолчанию: 100)",
    )

    parser.add_argument(
        "--timeout",
        type=int,
        default=None,
        help="Таймаут в секундах (по умолчанию: без ограничений)",
    )

    parser.add_argument(
        "--study-name",
        type=str,
        default=None,
        help="Имя Optuna study (по умолчанию: генерируется автоматически)",
    )

    parser.add_argument(
        "--n-folds",
        type=int,
        default=5,
        help="Количество фолдов для кросс-валидации (по умолчанию: 5)",
    )

    parser.add_argument(
        "--no-cv",
        action="store_true",
        help="Не использовать кросс-валидацию (использовать фиксированную валидацию)",
    )

    parser.add_argument(
        "--run-name",
        type=str,
        default=None,
        help="Имя MLflow run (по умолчанию: генерируется автоматически)",
    )

    parser.add_argument(
        "--train-encoded",
        type=Path,
        default=None,
        help=f"Путь к train данным (по умолчанию: {FILES['train_encoded']})",
    )

    return parser.parse_args()


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

    logger.info("Подготовка данных...")
    datasets = feature_extractor.prepare_datasets(
        validator=validator,
        run_leak_checks=False,
    )

    X_train = datasets["X_train"]
    y_train = datasets["y_train"]
    X_val = datasets["X_val"] if not args.no_cv else datasets["X_val"]
    y_val = datasets["y_val"] if not args.no_cv else datasets["y_val"]

    logger.info(f"Train: {len(X_train):,} записей")
    if X_val is not None:
        logger.info(f"Validation: {len(X_val):,} записей")

    # Базовые параметры модели
    if args.model == "lightgbm":
        base_params = LIGHTGBM_PARAMS.copy()
    else:
        logger.error(f"Оптимизация для {args.model} пока не реализована")
        sys.exit(1)

    # Создание Optuna study
    study_name = args.study_name or f"optuna_{args.model}_{args.n_trials}trials"
    study = optuna.create_study(
        direction="minimize",
        study_name=study_name,
    )

    # Имя MLflow run
    run_name = args.run_name or f"optuna_{args.model}_tuning"

    # Запуск оптимизации
    logger.info(f"Начало оптимизации: {args.n_trials} trials")
    logger.info(f"Study name: {study_name}")
    logger.info(f"CV: {'Да' if not args.no_cv else 'Нет'} ({args.n_folds} фолдов)")

    with mlflow.start_run(run_name=run_name):
        # Логируем конфигурацию
        mlflow.log_param("optimization_model", args.model)
        mlflow.log_param("n_trials", args.n_trials)
        mlflow.log_param("n_folds", args.n_folds if not args.no_cv else 0)
        mlflow.log_param("use_cv", not args.no_cv)
        mlflow.log_param("study_name", study_name)

        try:
            study.optimize(
                lambda trial: objective(
                    trial,
                    X_train,
                    y_train,
                    X_val,
                    y_val,
                    base_params,
                    n_folds=args.n_folds,
                    use_cv=not args.no_cv,
                ),
                n_trials=args.n_trials,
                timeout=args.timeout,
                show_progress_bar=True,
            )
        except KeyboardInterrupt:
            logger.warning("Оптимизация прервана пользователем")

        # Лучшие параметры
        best_params = study.best_params
        best_value = study.best_value

        logger.info(f"\n{'=' * 60}")
        logger.info("РЕЗУЛЬТАТЫ ОПТИМИЗАЦИИ")
        logger.info(f"{'=' * 60}")
        logger.info(f"Лучший RMSE (CV): {best_value:.6f}")
        logger.info(f"Количество завершенных trials: {len(study.trials)}")
        logger.info("\nЛучшие параметры:")
        for key, value in sorted(best_params.items()):
            logger.info(f"  {key}: {value}")

        # Логируем в MLflow
        mlflow.log_metric("best_cv_rmse", best_value)
        mlflow.log_metric("n_completed_trials", len(study.trials))

        for key, value in best_params.items():
            mlflow.log_param(f"best_{key}", value)

        # Сохраняем лучшие параметры в JSON
        best_params_full = base_params.copy()
        best_params_full.update(best_params)

        output_dir = Path("tuned_configs")
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"best_params_{args.model}_{study_name}.json"

        with open(output_file, "w") as f:
            json.dump(best_params_full, f, indent=2)

        logger.info(f"\nЛучшие параметры сохранены в: {output_file}")

        # Выводим команду для использования лучших параметров
        print(f"\nЛучшие параметры сохранены в: {output_file}")
        print("\nДля использования лучших параметров:")
        print(
            f"  python scripts/train_single.py --model {args.model} --run-name {args.model}_tuned"
        )
        print("\nИли обновите LIGHTGBM_PARAMS в scripts/modeling_config.py:")
        print(json.dumps(best_params_full, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
