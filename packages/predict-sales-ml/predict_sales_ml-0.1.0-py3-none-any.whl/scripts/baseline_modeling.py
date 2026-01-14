import logging
import os

import mlflow
import mlflow.lightgbm
import pandas as pd

from dotenv import load_dotenv
from lightgbm import LGBMRegressor

from scripts.modeling_config import (
    FILES,
    VALIDATION_CONFIG,
    LIGHTGBM_PARAMS,
    SUBMISSION_CONFIG,
)
from scripts.utils_validation import (
    BaselineFeatureExtractor,
    TimeSeriesValidator,
    train_model,
    evaluate_model,
    create_submission,
)

# === logging ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()
if "MLFLOW_USER" not in os.environ:
    os.environ["MLFLOW_USER"] = "Eugene Malyukevich"

# === MLflow ===
mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
mlflow_experiment_name = os.getenv("MLFLOW_EXPERIMENT_NAME")

logger.info("MLFLOW_TRACKING_URI=%s", mlflow_tracking_uri)
logger.info("MLFLOW_EXPERIMENT_NAME=%s", mlflow_experiment_name)

mlflow.set_tracking_uri(mlflow_tracking_uri)
mlflow.set_experiment(mlflow_experiment_name)

# === Загрузка encoded train данных ===
logger.info("Чтение данных из %s", FILES["train_encoded"])
sales_encoded = pd.read_parquet(FILES["train_encoded"])
logger.info("Загружено %d строк, %d столбцов", *sales_encoded.shape)

# === Инициализация валидации и feature extractor ===
validator = TimeSeriesValidator(**VALIDATION_CONFIG)
feature_extractor = BaselineFeatureExtractor(features_df=sales_encoded)

print("\nКонфигурация валидации:")
print(f"Train: месяцы {validator.train_months[0]}-{validator.train_months[1]}")
print(f"Validation: месяцы {validator.val_months[0]}-{validator.val_months[1]}")
print(f"Test: месяц {validator.test_month}")
print(f"Production: месяц {validator.production_month}")

feature_list = feature_extractor.get_feature_list()
logger.info("Количество фичей: %d", len(feature_list))
print(f"\nФичи для модели: {feature_list}")

# === Подготовка train / val / test ===
datasets = feature_extractor.prepare_datasets(
    validator=validator,
    run_leak_checks=True,
)

X_train = datasets["X_train"]
y_train = datasets["y_train"]
X_val = datasets["X_val"]
y_val = datasets["y_val"]
X_test = datasets["X_test"]
y_test = datasets["y_test"]

print(f"\nВсего train данных: {len(X_train):,} записей")
print(f"Память X_train: {X_train.memory_usage(deep=True).sum() / 1024**2:.1f} MB")

# === Обучение и оценка модели ===
# Обёртываем весь процесс в один MLflow run, как в прошлой рабочей версии
with mlflow.start_run(run_name="baseline_LightGBM_encoded"):
    # Логируем конфигурацию валидации
    mlflow.log_param(
        "train_months", f"{validator.train_months[0]}-{validator.train_months[1]}"
    )
    mlflow.log_param(
        "val_months", f"{validator.val_months[0]}-{validator.val_months[1]}"
    )
    mlflow.log_param("test_month", int(validator.test_month))
    mlflow.log_param("production_month", int(validator.production_month))
    mlflow.log_param("n_features", int(len(feature_list)))
    mlflow.log_param("n_train_samples", int(len(X_train)))

    # === Обучение модели ===
    model_params = LIGHTGBM_PARAMS.copy()
    model_params.update(
        {
            "verbose": 100,
            "objective": "regression",
            "metric": "rmse",
        }
    )

    model = train_model(
        model_class=LGBMRegressor,
        model_params=model_params,
        X_train=X_train,
        y_train=y_train,
        X_val=X_val,
        y_val=y_val,
        run_name=None,  # Не создаём новый run, используем текущий
        validator=validator,
    )

    # === Оценка модели ===
    _ = evaluate_model(
        model=model,
        X_val=X_val,
        y_val=y_val,
        X_test=X_test,
        y_test=y_test,
        feature_names=feature_list,
        log_to_mlflow=True,
    )

    # === Сохранение модели в MLflow ===
    # При использовании remote tracking URI (http://localhost:5050) артефакты
    # сохраняются через HTTP на MLflow сервер. Сервер должен иметь доступ
    # к директории ./mlflow/mlruns для записи (через volume в Docker).
    try:
        logger.info("Сохранение модели в MLflow...")
        logger.info("Tracking URI: %s", mlflow.get_tracking_uri())
        logger.info(
            "Active run ID: %s",
            mlflow.active_run().info.run_id if mlflow.active_run() else "None",
        )

        # В новых версиях MLflow используется 'name' вместо 'artifact_path'
        # Но для обратной совместимости оставляем artifact_path
        mlflow.lightgbm.log_model(model, artifact_path="model")
        logger.info("Модель успешно сохранена в MLflow")
    except Exception as e:
        logger.error("Ошибка при сохранении модели: %s", e)
        logger.error("Тип ошибки: %s", type(e).__name__)
        import traceback

        logger.error("Traceback:\n%s", traceback.format_exc())
        # Как в прошлой рабочей версии - поднимаем исключение, чтобы увидеть проблему
        raise

# === Создание submission ===
submission = create_submission(
    model=model,
    feature_extractor=feature_extractor,
    test_encoded_path=FILES["test_encoded"],
    output_path=SUBMISSION_CONFIG["output_dir"],
    production_month=validator.production_month,
    clip_min=SUBMISSION_CONFIG["clip_min"],
    clip_max=SUBMISSION_CONFIG["clip_max"],
    submission_filename="baseline_lgbm_submission.csv",
)

print("\nBaseline modeling завершён успешно!")
