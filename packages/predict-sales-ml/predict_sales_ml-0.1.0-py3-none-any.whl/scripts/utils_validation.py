import pandas as pd
import numpy as np
import time
import mlflow
import lightgbm as lgbm
from contextlib import nullcontext

from tqdm import tqdm
from typing import List, Optional
from pathlib import Path

from sklearn.model_selection import TimeSeriesSplit
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class TimeSeriesValidator:
    """
    Валидация для временных рядов с разбиением по месяцам (date_block_num).

    Базовые правила:
    - Для прогноза месяца N (target_month = N) мы можем использовать
      только информацию из месяцев 0..N-1 включительно.
    - Train / validation / test / production диапазоны по месяцам
      не пересекаются и упорядочены по времени:

        train_months = (train_start, train_end)
        val_months   = (val_start,  val_end)   где val_start > train_end
        test_month   > val_end
        production_month > test_month

    Класс отвечает только за выбор индексов по date_block_num.
    Логика построения фичей (и контроль leakage внутри них) реализована
    в BaselineFeatureExtractor.
    """

    def __init__(
        self,
        train_months=(0, 30),
        val_months=(31, 32),
        test_month=33,
        production_month=34,
    ):
        self.train_months = train_months
        self.val_months = val_months
        self.test_month = test_month
        self.production_month = production_month

    def split_data(self, df: pd.DataFrame, date_column: str = "date_block_num"):
        """
        Простое разбиение по месяцам. Возвращает индексы для train/val/test.
        """
        train_mask = (df[date_column] >= self.train_months[0]) & (
            df[date_column] <= self.train_months[1]
        )
        val_mask = (df[date_column] >= self.val_months[0]) & (
            df[date_column] <= self.val_months[1]
        )
        test_mask = df[date_column] == self.test_month

        train_idx = df[train_mask].index.values
        val_idx = df[val_mask].index.values
        test_idx = df[test_mask].index.values

        return train_idx, val_idx, test_idx

    def cross_validate(
        self,
        df: pd.DataFrame,
        date_column: str = "date_block_num",
        n_splits: int = 5,
        max_train_size=None,
    ):
        """
        Time-series cross-validation используя sklearn TimeSeriesSplit.
        Но адаптированный под наши месяцы.
        """
        train_data = df[
            (df[date_column] >= self.train_months[0])
            & (df[date_column] <= self.train_months[1])
        ].copy()
        train_data = train_data.sort_values(date_column)

        tscv = TimeSeriesSplit(n_splits=n_splits, max_train_size=max_train_size)
        X = train_data[[date_column]]

        folds = []
        for train_idx, val_idx in tscv.split(X):
            train_global_idx = train_data.iloc[train_idx].index.values
            val_global_idx = train_data.iloc[val_idx].index.values
            folds.append((train_global_idx, val_global_idx))

        return folds

    def get_geature_extraction_window(
        self, target_month: int, date_column: str = "date_block_num"
    ):
        """
        Возвращает валидный диапазон месяцев для извлечения фичей.
        Для предсказания месяца target_month можно использовать данные
        только до (target_month - 1) включительно.

        Args:
            target_month: Месяц, для которого делаем предсказание
            date_column: Название колонки с номером месяца

        Returns:
            tuple: (min_month, max_month) - валидный диапазон для извлечения фичей
        """
        max_month = target_month - 1
        min_month = 0

        return (min_month, max_month)


class BaselineFeatureExtractor:
    """
    Извлечение базовых фичей из готового датасета sales_monthly_with_features.

    Идея:
    - В features_df каждая строка соответствует (shop_id, item_id, date_block_num),
      где date_block_num — МЕСЯЦ, ЗА КОТОРЫЙ посчитаны лаги, скользящие средние
      и агрегаты на основании данных до этого месяца.
    - Для прогноза месяца target_month = N мы используем фичи из source_month = N-1:
      берем все (shop_id, item_id) с date_block_num == N-1 и переносим их в
      target_month = N (обновляя только временную фичу "month").
    - Таким образом, для каждого примера (shop_id, item_id, target_month=N)
      все фичи построены только из истории до N-1 и leakage исключён.
    """

    def __init__(
        self,
        features_df: Optional[pd.DataFrame] = None,
        features_path: Optional[Path] = None,
        date_column: str = "date_block_num",
        target_column: str = "item_cnt_month",
    ):
        """
        Args:
            features_df: Датафрейм с фичами (если уже загружен)
            features_path: Путь к parquet файлу с фичами
            date_column: Название колонки с номером месяца
            target_column: Название колонки с таргетом (по умолчанию item_cnt_month)

        Логика выбора фичей:
        - Берём все колонки из features_df,
        - исключаем:
            * идентификаторы: shop_id, item_id, ID (если есть),
            * колонку с месяцом date_column,
            * колонку таргета target_column.
        - Всё остальное считаем фичами и передаём в модель.

        Таким образом, baseline теперь использует максимум доступных признаков
        из подготовленного encode-датасета.
        """
        self.date_column = date_column
        self.target_column = target_column
        self.feature_list: List[str] = []

        # Загружаем датафрейм с фичами
        if features_df is not None:
            self.features_df = features_df.copy()
        elif features_path is not None:
            self.features_df = pd.read_parquet(features_path)
        else:
            raise ValueError("Нужно указать либо features_df, либо features_path")

        all_columns = list(self.features_df.columns)
        exclude_cols = {
            "shop_id",
            "item_id",
            "ID",
            self.date_column,
            self.target_column,
        }
        self.feature_list = [col for col in all_columns if col not in exclude_cols]

    def extract_features(
        self,
        target_month: int,
        pairs_df: Optional[pd.DataFrame] = None,
        shop_id_col: str = "shop_id",
        item_id_col: str = "item_id",
    ) -> pd.DataFrame:
        """
        Извлекает фичи для конкретного месяца target_month из готового датасета.
        Важно: для предсказания месяца N используем фичи из месяца N-1,
        чтобы избежать leakage (кроме временных фичей, которые вычисляются для target_month).

        Args:
            target_month: Месяц, для которого извлекаем фичи
            pairs_df: Датафрейм с парами shop_id x item_id (если None, берем все из features_df)
            shop_id_col: Название колонки с shop_id
            item_id_col: Название колонки с item_id

        Returns:
            Датафрейм с фичами для target_month
        """
        source_month = target_month - 1

        if source_month < 0:
            raise ValueError(
                f"Нельзя извлечь фичи для месяца {target_month}: нет данных до него"
            )

        # Берем фичи из предыдущего месяца
        source_data = self.features_df[
            self.features_df[self.date_column] == source_month
        ].copy()

        if len(source_data) == 0:
            raise ValueError(f"Нет данных для месяца {source_month}")

        # Если указаны конкретные пары, фильтруем по ним
        if pairs_df is not None:
            # Объединяем с парами, чтобы получить только нужные
            result = pairs_df.copy()
            result[self.date_column] = target_month

            # Мержим фичи из предыдущего месяца
            feature_cols = [shop_id_col, item_id_col] + self.feature_list
            available_cols = [col for col in feature_cols if col in source_data.columns]

            result = result.merge(
                source_data[available_cols], on=[shop_id_col, item_id_col], how="left"
            )
        else:
            # Берем все пары из предыдущего месяца
            result = source_data[[shop_id_col, item_id_col] + self.feature_list].copy()
            result[self.date_column] = target_month

        # Обновляем временную фичу month так, чтобы она соответствовала
        # ЦЕЛЕВОМУ месяцу (target_month), а не месяцу-источнику (source_month).
        # Все остальные фичи (лаги, средние, агрегаты) уже отражают историю до
        # source_month и не содержат информацию из будущего.
        # Здесь target_month — скаляр int, поэтому приводим к int без astype.
        result["month"] = int(target_month % 12 + 1)

        # Заполняем пропуски нулями (для новых пар, которых не было в предыдущем месяце)
        for col in self.feature_list:
            if col != "month" and col in result.columns:
                result[col] = result[col].fillna(0)

        return result

    def get_feature_list(self) -> List[str]:
        """
        Возвращает список названий фичей.

        Returns:
            Список названий фичей
        """
        return self.feature_list.copy()

    def validate_no_leakage(self, df: pd.DataFrame, target_month: int) -> dict:
        """
        Простая проверка на отсутствие leakage.

        Args:
            df: Датафрейм с фичами
            target_month: Месяц, для которого извлекались фичи

        Returns:
            dict с результатами проверки
        """
        if self.date_column not in df.columns:
            return {
                "has_leakage": False,
                "message": "Колонка date_column не найдена в данных",
            }

        # Проверяем, что date_column = target_month (фичи должны быть для этого месяца)
        wrong_month = df[df[self.date_column] != target_month]

        if len(wrong_month) > 0:
            return {
                "has_leakage": True,
                "message": f"Найдены данные для месяцев != {target_month}",
                "wrong_months": sorted(wrong_month[self.date_column].unique().tolist()),
            }

        return {"has_leakage": False, "message": "Leakage не обнаружен"}

    def build_feature_matrix(
        self,
        validator: TimeSeriesValidator,
        mode: str,
        target_column: str = "item_cnt_month",
        run_leak_checks: bool = False,
    ):
        """
        Строит матрицы X, y для train/val/test/prod в соответствии с TimeSeriesValidator
        и логикой BaselineFeatureExtractor (N ← N-1).

        Использует self.features_df (загруженный при инициализации) для извлечения фичей
        и таргетов по месяцам, определённым в validator.

        Args:
            validator: Объект TimeSeriesValidator с заданными диапазонами месяцев.
            mode: Один из ["train", "val", "test", "prod"].
            target_column: Название таргета. По умолчанию "item_cnt_month".
            run_leak_checks: Если True, дополнительно запускает validate_no_leakage
                для каждого target_month и падает при обнаружении leakage.

        Returns:
            X: pd.DataFrame с фичами (объединённый по всем выбранным месяцам).
            y: pd.Series с таргетом.
            meta: dict с метаинформацией:
                - mode: str - режим работы
                - target_months: List[int] - список месяцев, для которых извлечены данные
                - n_samples: int - количество примеров
                - n_features: int - количество фичей
        """
        mode = mode.lower()
        if mode not in {"train", "val", "test", "prod"}:
            raise ValueError(
                f"Неожиданный режим='{mode}', ожидался один из: ['train', 'val', 'test', 'prod']."
            )

        # Определяем, какие target_months входят в данный mode
        if mode == "train":
            min_m, max_m = validator.train_months
            target_months = sorted(
                m
                for m in self.features_df[self.date_column].unique()
                if min_m <= m <= max_m and m > 0
            )
        elif mode == "val":
            min_m, max_m = validator.val_months
            target_months = sorted(
                m
                for m in self.features_df[self.date_column].unique()
                if min_m <= m <= max_m
            )
        elif mode == "test":
            target_months = [validator.test_month]
        else:  # mode == "prod"
            target_months = [validator.production_month]

        if not target_months:
            raise ValueError(f"Для mode='{mode}' не найдено ни одного target_month.")

        feature_frames = []
        target_frames = []

        # Для каждого target_month извлекаем фичи и таргеты
        for month in target_months:
            # Фичи для месяца N из source_month = N-1
            month_features = self.extract_features(target_month=month)

            if run_leak_checks:
                check = self.validate_no_leakage(month_features, target_month=month)
                if check.get("has_leakage", False):
                    raise RuntimeError(f"Leakage detected for month={month}: {check}")

            # Таргет: реальные продажи за месяц N
            month_data = self.features_df[self.features_df[self.date_column] == month]

            if target_column not in month_data.columns:
                raise KeyError(
                    f"Колонка таргета '{target_column}' не найдена в features_df "
                    f"для month={month}."
                )

            month_with_target = month_features.merge(
                month_data[["shop_id", "item_id", target_column]],
                on=["shop_id", "item_id"],
                how="inner",
            )

            if len(month_with_target) == 0:
                raise RuntimeError(
                    f"После merge для месяца {month} не осталось записей "
                    f"(проверь соответствие пар shop_id x item_id)."
                )

            feature_frames.append(month_with_target[self.get_feature_list()])
            target_frames.append(month_with_target[target_column])

        X = pd.concat(feature_frames, ignore_index=True)
        y = pd.concat(target_frames, ignore_index=True)

        meta = {
            "mode": mode,
            "target_months": target_months,
            "n_samples": int(X.shape[0]),
            "n_features": int(X.shape[1]),
        }

        return X, y, meta

    def prepare_datasets(
        self,
        validator: TimeSeriesValidator,
        run_leak_checks: bool = True,
        target_column: str = "item_cnt_month",
    ) -> dict:
        """
        Подготавливает train/val/test датасеты используя build_feature_matrix.

        Args:
            validator: Объект TimeSeriesValidator с заданными диапазонами месяцев.
            run_leak_checks: Если True, запускает validate_no_leakage для каждого месяца.
            target_column: Название таргета. По умолчанию "item_cnt_month".

        Returns:
            dict с ключами:
                - X_train, y_train, meta_train
                - X_val, y_val, meta_val (или None, None, None если нет val данных)
                - X_test, y_test, meta_test (или None, None, None если нет test данных)
        """
        results = {}

        # Train
        print("Подготовка train данных...")
        X_train, y_train, meta_train = self.build_feature_matrix(
            validator=validator,
            mode="train",
            target_column=target_column,
            run_leak_checks=run_leak_checks,
        )
        results["X_train"] = X_train
        results["y_train"] = y_train
        results["meta_train"] = meta_train
        print(
            f"Train: {meta_train['n_samples']:,} записей, {meta_train['n_features']} фичей"
        )

        # Validation
        print("\nПодготовка validation данных...")
        try:
            X_val, y_val, meta_val = self.build_feature_matrix(
                validator=validator,
                mode="val",
                target_column=target_column,
                run_leak_checks=run_leak_checks,
            )
            results["X_val"] = X_val
            results["y_val"] = y_val
            results["meta_val"] = meta_val
            print(
                f"Validation: {meta_val['n_samples']:,} записей, {meta_val['n_features']} фичей"
            )
        except (ValueError, RuntimeError) as e:
            print(f"Не удалось подготовить validation данные: {e}")
            results["X_val"] = None
            results["y_val"] = None
            results["meta_val"] = None

        # Test
        print("\nПодготовка test данных...")
        try:
            X_test, y_test, meta_test = self.build_feature_matrix(
                validator=validator,
                mode="test",
                target_column=target_column,
                run_leak_checks=run_leak_checks,
            )
            results["X_test"] = X_test
            results["y_test"] = y_test
            results["meta_test"] = meta_test
            print(
                f"Test: {meta_test['n_samples']:,} записей, {meta_test['n_features']} фичей"
            )
        except (ValueError, RuntimeError) as e:
            print(f"Не удалось подготовить test данные: {e}")
            results["X_test"] = None
            results["y_test"] = None
            results["meta_test"] = None

        return results


def train_model(
    model_class,
    model_params: dict,
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: Optional[pd.DataFrame] = None,
    y_val: Optional[pd.Series] = None,
    run_name: Optional[str] = "baseline_model",
    validator: Optional["TimeSeriesValidator"] = None,
):
    """
    Обучает модель с MLflow-логированием.

    Args:
        model_class: класс модели (например, LGBMRegressor, XGBRegressor, RandomForestRegressor).
        model_params: dict с гиперпараметрами для инициализации модели.
        X_train, y_train: обучающие данные.
        X_val, y_val: валидационные данные (можно None).
        run_name: имя MLflow run. Если None, использует активный run (не создаёт новый).
        validator: опционально, объект TimeSeriesValidator для логирования конфигурации сплитов.

    Returns:
        Обученная модель.
    """
    # Если run_name=None, используем активный run (не создаём новый)
    # Это позволяет обернуть весь процесс в один run в вызывающем коде
    if run_name is None:
        # Проверяем, есть ли активный run
        active_run = mlflow.active_run()
        if active_run is None:
            raise RuntimeError(
                "run_name=None, но нет активного MLflow run. Создайте run перед вызовом train_model."
            )
        # Просто логируем в активный run, без создания нового контекста
        # (весь код выполняется внутри внешнего with mlflow.start_run())
        # Используем nullcontext, чтобы код работал одинаково в обоих случаях
        run_wrapper = nullcontext()
    else:
        # Создаём новый run
        run_wrapper = mlflow.start_run(run_name=run_name)

    with run_wrapper:
        model = model_class(**model_params)

        # Базовая информация о данных
        mlflow.log_param("model_type", model.__class__.__name__)
        mlflow.log_param("n_train_samples", int(X_train.shape[0]))
        mlflow.log_param("n_features", int(X_train.shape[1]))

        # Логируем гиперпараметры модели
        for key, value in model_params.items():
            try:
                mlflow.log_param(key, value)
            except Exception:
                # На случай, если значение не сериализуемо в строку
                mlflow.log_param(key, str(value))

        # Логируем информацию о временных сплитах, если есть валидатор
        # (но только если run_name не None, чтобы не дублировать логирование)
        if validator is not None and run_name is not None:
            mlflow.log_param(
                "train_months",
                f"{validator.train_months[0]}-{validator.train_months[1]}",
            )
            mlflow.log_param(
                "val_months",
                f"{validator.val_months[0]}-{validator.val_months[1]}",
            )
            mlflow.log_param("test_month", int(validator.test_month))
            mlflow.log_param("production_month", int(validator.production_month))

        start_time = time.time()

        eval_set = None
        fit_kwargs = {}
        if X_val is not None and hasattr(model, "fit"):
            # Не заполняем NaN здесь, чтобы пользователь мог контролировать стратегию
            eval_set = [(X_val.fillna(0), y_val)]
            fit_kwargs["eval_set"] = eval_set

            # Для LightGBM добавляем метрику и раннюю остановку
            if model.__class__.__name__.startswith("LGBM"):
                fit_kwargs["eval_metric"] = "rmse"
                fit_kwargs["callbacks"] = [lgbm.early_stopping(stopping_rounds=50)]

        with tqdm(total=1, desc=f"Обучение модели {model.__class__.__name__}") as pbar:
            model.fit(X_train.fillna(0), y_train, **fit_kwargs)
            pbar.update(1)

        elapsed_time = time.time() - start_time
        mlflow.log_metric("training_time_seconds", float(elapsed_time))

        if hasattr(model, "best_iteration_") and model.best_iteration_ is not None:
            mlflow.log_param("best_iteration", int(model.best_iteration_))

        return model


def evaluate_model(
    model,
    X_val=None,
    y_val=None,
    X_test=None,
    y_test=None,
    clip_min=0.0,
    clip_max=20.0,
    feature_names=None,
    log_to_mlflow=True,
):
    """
    Оценивает модель на validation и/или test данных.

    Args:
        model: Обученная модель с методом predict().
        X_val, y_val: Валидационные данные (опционально).
        X_test, y_test: Тестовые данные (опционально).
        clip_min, clip_max: Границы для обрезки предсказаний (по умолчанию [0, 20] для Kaggle).
        feature_names: Список названий фичей (для важности фичей, опционально).
        log_to_mlflow: Если True, логирует метрики в MLflow (если есть активный run).

    Returns:
        dict с метриками:
            - metrics_val: dict с метриками validation (или None)
            - metrics_test: dict с метриками test (или None)
            - feature_importance: pd.DataFrame с важностью фичей (если доступно)
    """

    def calculate_rmse(y_true, y_pred):
        """Вычисляет RMSE (метрика соревнования)."""
        mse = mean_squared_error(y_true, y_pred)
        return np.sqrt(mse)

    results = {
        "metrics_val": None,
        "metrics_test": None,
        "feature_importance": None,
    }

    # Validation
    if X_val is not None and y_val is not None:
        X_val_clean = X_val.fillna(0)

        print("\nПредсказание на validation...")
        with tqdm(total=1, desc="Оценка validation") as pbar:
            y_val_pred = model.predict(X_val_clean)
            pbar.update(1)

        y_val_pred = np.clip(y_val_pred, clip_min, clip_max)

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

        print("\nValidation метрики:")
        print(f"RMSE: {rmse_val:.4f}")
        print(f"MAE: {mae_val:.4f}")
        print(f"R²: {r2_val:.4f}")
        print(f"Min pred: {y_val_pred.min():.2f}, Max pred: {y_val_pred.max():.2f}")
        print(f"Min true: {y_val.min():.2f}, Max true: {y_val.max():.2f}")

        # Логируем в MLflow только итоговые (test) метрики, чтобы не захламлять run.
        # Поэтому validation-метрики только печатаем, без log_metric.

    # Test
    if X_test is not None and y_test is not None:
        X_test_clean = X_test.fillna(0)

        print("\nПредсказание на test...")
        with tqdm(total=1, desc="Predicting test") as pbar:
            y_test_pred = model.predict(X_test_clean)
            pbar.update(1)

        y_test_pred = np.clip(y_test_pred, clip_min, clip_max)

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

        print("\nTest метрики:")
        print(f"RMSE: {rmse_test:.4f}")
        print(f"MAE: {mae_test:.4f}")
        print(f"R²: {r2_test:.4f}")
        print(f"Min pred: {y_test_pred.min():.2f}, Max pred: {y_test_pred.max():.2f}")
        print(f"Min true: {y_test.min():.2f}, Max true: {y_test.max():.2f}")

        if log_to_mlflow:
            try:
                mlflow.log_metric("rmse_test", metrics_test["rmse"])
                mlflow.log_metric("mae_test", metrics_test["mae"])
                mlflow.log_metric("r2_test", metrics_test["r2"])
            except Exception as e:
                print(f"Не удалось залогировать метрики в MLflow: {e}")

    # Важность фичей (если доступна)
    if hasattr(model, "feature_importances_"):
        if feature_names is None:
            # Пытаемся получить названия из X_train, если он был передан
            # Или создаем generic названия
            try:
                if X_val is not None:
                    feature_names = list(X_val.columns)
                elif X_test is not None:
                    feature_names = list(X_test.columns)
                else:
                    feature_names = [
                        f"feature_{i}" for i in range(len(model.feature_importances_))
                    ]
            except Exception:
                feature_names = [
                    f"feature_{i}" for i in range(len(model.feature_importances_))
                ]

        feature_importance = pd.DataFrame(
            {
                "feature": feature_names,
                "importance": model.feature_importances_,
            }
        ).sort_values("importance", ascending=False)

        results["feature_importance"] = feature_importance

        print("\nТоп-20 важных фичей:")
        print(feature_importance.head(20).to_string(index=False))

    return results


def create_submission(
    model,
    feature_extractor: BaselineFeatureExtractor,
    test_encoded_path: Path,
    output_path: Path,
    production_month: int = 34,
    clip_min: float = 0.0,
    clip_max: float = 20.0,
    submission_filename: str = "submission.csv",
):
    """
    Создает Kaggle submission файл из test_enriched_encoded.

    Args:
        model: Обученная модель с методом predict().
        feature_extractor: Экземпляр BaselineFeatureExtractor, работающий
            поверх train данных (sales_monthly_with_features_encoded).
        test_encoded_path: Путь к test_enriched_encoded.parquet.
        output_path: Директория для сохранения submission файла.
        production_month: Месяц для предсказания (по умолчанию 34).
        clip_min, clip_max: Границы для обрезки предсказаний.
        submission_filename: Имя файла для submission.

    Returns:
        pd.DataFrame с submission (ID, item_cnt_month).
    """
    print(f"\nЗагрузка test данных из {test_encoded_path}...")
    test_encoded = pd.read_parquet(test_encoded_path)
    print(f"Загружено {len(test_encoded):,} записей")

    # Проверяем наличие обязательных колонок
    required_cols = ["ID", "shop_id", "item_id"]
    missing_cols = [col for col in required_cols if col not in test_encoded.columns]
    if missing_cols:
        raise ValueError(f"В test_encoded отсутствуют колонки: {missing_cols}")

    # Проверяем, что date_block_num = production_month
    if "date_block_num" in test_encoded.columns:
        unique_months = test_encoded["date_block_num"].unique()
        if len(unique_months) > 1 or (
            len(unique_months) == 1 and unique_months[0] != production_month
        ):
            print(
                f"Предупреждение: test_encoded содержит date_block_num={unique_months}, ожидался {production_month}"
            )

    # Извлекаем пары shop_id x item_id из test
    test_pairs = test_encoded[["shop_id", "item_id"]].drop_duplicates()
    print(f"Уникальных пар (shop_id, item_id) в test: {len(test_pairs):,}")

    # Извлекаем фичи для production месяца
    print(f"\nИзвлечение фичей для месяца {production_month}...")
    production_features = feature_extractor.extract_features(
        target_month=production_month,
        pairs_df=test_pairs,
    )
    print(f"Извлечено фичей для {len(production_features):,} пар")

    # Мержим с test, чтобы сохранить ID
    test_with_features = test_encoded[["ID", "shop_id", "item_id"]].merge(
        production_features[
            ["shop_id", "item_id"] + feature_extractor.get_feature_list()
        ],
        on=["shop_id", "item_id"],
        how="left",
    )

    # Проверяем, что все ID сохранены
    if len(test_with_features) != len(test_encoded):
        raise RuntimeError(
            f"После merge потеряны записи: было {len(test_encoded):,}, стало {len(test_with_features):,}"
        )

    # Проверяем пропуски в фичах
    feature_list = feature_extractor.get_feature_list()
    missing_features = test_with_features[feature_list].isnull().sum()
    if missing_features.sum() > 0:
        print("\nПредупреждение: найдены пропуски в фичах:")
        print(missing_features[missing_features > 0])
        # Заполняем пропуски нулями
        test_with_features[feature_list] = test_with_features[feature_list].fillna(0)

    # Предсказания
    print("\nГенерация предсказаний...")
    X_prod = test_with_features[feature_list].fillna(0)

    with tqdm(total=1, desc="Predicting production") as pbar:
        y_pred = model.predict(X_prod)
        pbar.update(1)

    # Обрезаем предсказания
    y_pred = np.clip(y_pred, clip_min, clip_max)

    # Создаем submission DataFrame
    submission = pd.DataFrame(
        {
            "ID": test_with_features["ID"],
            "item_cnt_month": y_pred,
        }
    )

    # Проверяем, что все ID на месте
    if len(submission) != len(test_encoded):
        raise RuntimeError(
            f"Количество записей в submission ({len(submission):,}) "
            f"не совпадает с test ({len(test_encoded):,})"
        )

    # Проверяем, что ID отсортированы (как в оригинальном test)
    if not submission["ID"].equals(test_encoded["ID"]):
        # Сортируем по ID, чтобы соответствовать оригинальному порядку
        submission = submission.sort_values("ID").reset_index(drop=True)
        print("Предупреждение: submission отсортирован по ID")

    # Сохраняем
    output_path.mkdir(parents=True, exist_ok=True)
    submission_file = output_path / submission_filename
    submission.to_csv(submission_file, index=False)
    print(f"\nSubmission сохранен: {submission_file}")
    print(f"Размер: {len(submission):,} записей")
    print(f"Диапазон предсказаний: [{y_pred.min():.2f}, {y_pred.max():.2f}]")
    print(f"Среднее предсказание: {y_pred.mean():.2f}")

    return submission
