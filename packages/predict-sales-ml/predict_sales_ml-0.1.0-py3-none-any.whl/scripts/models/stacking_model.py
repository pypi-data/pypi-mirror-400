from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np
from sklearn.model_selection import KFold, TimeSeriesSplit
from tqdm import tqdm

from scripts.models.base import BaseModel
from scripts.models.lightgbm_model import LightGBMModel
from scripts.models.xgboost_model import XGBoostModel


class StackingModel(BaseModel):
    """
    Stacking модель (ансамбль базовых моделей с мета-моделью).

    Принцип работы:
    1. Обучает несколько базовых моделей (base models)
    2. Получает их предсказания на train данных через out-of-fold (OOF) валидацию
    3. Обучает мета-модель (meta-learner) на OOF предсказаниях
    4. Использует мета-модель для финальных предсказаний

    Особенности:
    - Out-of-fold predictions для избежания overfitting
    - Поддержка временных рядов через TimeSeriesSplit
    - Гибкая настройка мета-модели
    - Сохранение всех базовых моделей для inference
    """

    def __init__(
        self,
        base_models: List[BaseModel],
        meta_model_class: Any,
        meta_model_params: Optional[Dict[str, Any]] = None,
        use_oof: bool = True,
        n_folds: int = 5,
        cv_type: str = "timeseries",
        random_state: int = 42,
        name: Optional[str] = None,
    ):
        """
        Инициализирует stacking модель.

        Args:
            base_models: Список базовых моделей (наследники BaseModel)
            meta_model_class: Класс мета-модели (по умолчанию LinearRegression)
            meta_model_params: Параметры для мета-модели
            use_oof: Использовать out-of-fold predictions (рекомендуется True)
            n_folds: Количество фолдов для OOF валидации
            cv_type: Тип кросс-валидации ("kfold" или "timeseries")
            random_state: Random state для воспроизводимости
            name: Имя модели
        """
        super().__init__(params={}, name=name or "StackingModel")

        if not base_models:
            raise ValueError("Необходимо указать хотя бы одну базовую модель")

        self.base_models = base_models
        self.meta_model_class = meta_model_class
        self.meta_model_params = meta_model_params or {}
        self.use_oof = use_oof
        self.n_folds = n_folds
        self.cv_type = cv_type
        self.random_state = random_state

        # Будет заполнено при обучении
        self.trained_base_models: List[BaseModel] = []
        self.oof_predictions: Optional[np.ndarray] = None
        self.meta_model = None

    def build_model(self) -> Any:
        """
        Создает мета-модель.

        Returns:
            Экземпляр мета-модели
        """
        return self.meta_model_class(**self.meta_model_params)

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        **kwargs,
    ):
        """
        Обучает stacking модель.

        Процесс:
        1. Для каждой базовой модели:
           - Если use_oof=True: обучает на фолдах и получает OOF предсказания
           - Если use_oof=False: обучает на всех данных и использует их предсказания
        2. Обучает мета-модель на OOF предсказаниях
        3. Переобучает базовые модели на всех train данных для финальных предсказаний

        Args:
            X_train: Обучающие данные
            y_train: Целевая переменная
            X_val: Валидационные данные (опционально, используется для early stopping базовых моделей)
            y_val: Целевая переменная для валидации
            **kwargs: Дополнительные параметры (передаются в базовые модели)
        """
        if self.is_trained:
            raise ValueError(
                f"Модель {self.name} уже обучена. "
                "Для переобучения создайте новый экземпляр модели."
            )

        self.feature_names = list(X_train.columns)
        n_samples = len(X_train)
        n_base_models = len(self.base_models)

        # Обучение
        oof_predictions = np.zeros((n_samples, n_base_models))
        val_predictions = None
        if X_val is not None:
            val_predictions = np.zeros((len(X_val), n_base_models))

        # Обучаем каждую базовую модель
        for idx, base_model in enumerate(self.base_models):
            print(
                f"\n--- Базовая модель {idx + 1}/{n_base_models}: {base_model.name} ---"
            )

            if self.use_oof:
                print(f"Получение OOF предсказаний ({self.n_folds} фолдов)...")

                # Выбираем тип кросс-валидации
                if self.cv_type == "timeseries":
                    cv = TimeSeriesSplit(n_splits=self.n_folds)
                elif self.cv_type == "kfold":
                    cv = KFold(
                        n_splits=self.n_folds,
                        shuffle=True,
                        random_state=self.random_state,
                    )

                # OOF предсказания
                for fold, (train_idx, val_idx) in enumerate(cv.split(X_train)):
                    print(f"    Fold {fold + 1}/{self.n_folds}...", end=" ")

                    # Разделяем данные на фолды
                    X_train_fold = X_train.iloc[train_idx]
                    y_train_fold = y_train.iloc[train_idx]
                    X_val_fold = X_train.iloc[val_idx]

                    # Создаем копию модели для фолда
                    fold_model = self._create_model_copy(base_model)

                    fold_model.fit(
                        X_train_fold,
                        y_train_fold,
                        X_val=X_val,
                        y_val=y_val,
                        verbose=False,
                        **kwargs,
                    )

                    oof_predictions[val_idx, idx] = fold_model.predict(X_val_fold)

                # Обучаем финальную модель на всех данных
                print("Обучение финальной модели на всех данных...")
                final_model = self._create_model_copy(base_model)
                final_model.fit(
                    X_train,
                    y_train,
                    X_val=X_val,
                    y_val=y_val,
                    verbose=kwargs.get("verbose", True),
                    **{k: v for k, v in kwargs.items() if k != "verbose"},
                )
                self.trained_base_models.append(final_model)
            else:
                print("Обучение на всех данных...")
                base_model.fit(
                    X_train,
                    y_train,
                    X_val=X_val,
                    y_val=y_val,
                    verbose=kwargs.get("verbose", True),
                    **{k: v for k, v in kwargs.items() if k != "verbose"},
                )
                # Используем предсказания на train для мета-модели
                oof_predictions[:, idx] = base_model.predict(X_train)
                self.trained_base_models.append(base_model)

            # Предсказания на валидации (если есть)
            if X_val is not None:
                val_predictions[:, idx] = self.trained_base_models[-1].predict(X_val)

            print(f"Модель {base_model.name} обучена")

        self.oof_predictions = oof_predictions

        # Обучаем мета-модель на OOF предсказаниях
        print(f"\n--- Обучение мета-модели ({self.meta_model_class.__name__}) ---")
        self.meta_model = self.build_model()

        with tqdm(total=1, desc="Обучение мета-модели") as pbar:
            self.meta_model.fit(oof_predictions, y_train)
            pbar.update(1)
        print("Мета-модель обучена")

        self.is_trained = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Делает предсказания на новых данных.

        Процесс:
        1. Получает предсказания от всех базовых моделей
        2. Использует мета-модель для финального предсказания

        Args:
            X: Данные для предсказания

        Returns:
            Массив предсказаний
        """
        if not self.is_trained:
            raise ValueError(
                f"Модель {self.name} не обучена. Вызовите метод fit() перед predict()."
            )

        if not self.trained_base_models:
            raise ValueError("Базовые модели не обучены")

        if self.meta_model is None:
            raise ValueError("Мета-модель не обучена")

        # Получаем предсказания от всех базовых моделей
        base_predictions = np.zeros((len(X), len(self.trained_base_models)))

        for idx, model in enumerate(self.trained_base_models):
            base_predictions[:, idx] = model.predict(X)

        # Используем мета-модель для финального предсказания
        return self.meta_model.predict(base_predictions)

    def get_base_model_predictions(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Возвращает предсказания от всех базовых моделей отдельно.
        Полезно для анализа вклада каждой модели.

        Args:
            X: Данные для предсказания

        Returns:
            DataFrame с предсказаниями от каждой базовой модели
        """
        if not self.is_trained:
            raise ValueError("Модель не обучена")

        predictions = {}
        for idx, model in enumerate(self.trained_base_models):
            predictions[f"{model.name}_pred"] = model.predict(X)

        return pd.DataFrame(predictions)

    def get_meta_model_coefficients(self) -> Optional[pd.DataFrame]:
        """
        Возвращает коэффициенты мета-модели (если доступно).
        Полезно для понимания вклада каждой базовой модели.

        Returns:
            DataFrame с коэффициентами или None
        """
        if not self.is_trained or self.meta_model is None:
            return None

        if not hasattr(self.meta_model, "coef_"):
            return None

        coef = self.meta_model.coef_
        intercept = (
            self.meta_model.intercept_ if hasattr(self.meta_model, "intercept_") else 0
        )

        result = pd.DataFrame(
            {
                "model": [model.name for model in self.trained_base_models],
                "coefficient": coef,
            }
        )

        if intercept != 0:
            result = pd.concat(
                [
                    pd.DataFrame({"model": ["intercept"], "coefficient": [intercept]}),
                    result,
                ],
                ignore_index=True,
            )

        return result

    def _create_model_copy(self, model: BaseModel) -> BaseModel:
        """
        Создает копию модели для использования в фолдах.

        Args:
            model: Исходная модель

        Returns:
            Новая копия модели с теми же параметрами
        """
        # Определяем тип модели и создаем копию
        if isinstance(model, LightGBMModel):
            return LightGBMModel(params=model.params.copy(), name=model.name)
        elif isinstance(model, XGBoostModel):
            return XGBoostModel(params=model.params.copy(), name=model.name)
        else:
            # Для других типов моделей пытаемся создать через класс
            model_class = model.__class__
            return model_class(params=model.params.copy(), name=model.name)

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Возвращает важность базовых моделей через коэффициенты мета-модели.

        Returns:
            DataFrame с важностью моделей
        """
        coef_df = self.get_meta_model_coefficients()
        if coef_df is None:
            return None

        # Убираем intercept, если есть
        coef_df = coef_df[coef_df["model"] != "intercept"].copy()
        coef_df = coef_df.sort_values("coefficient", key=abs, ascending=False)

        return coef_df.rename(columns={"coefficient": "importance"})
