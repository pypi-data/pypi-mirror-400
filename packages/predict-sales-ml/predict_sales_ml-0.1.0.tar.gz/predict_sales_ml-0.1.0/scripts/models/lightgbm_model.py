from typing import Optional
import pandas as pd
import numpy as np
import lightgbm as lgbm
from lightgbm import LGBMRegressor
from tqdm import tqdm

from scripts.models.base import BaseModel


class LightGBMModel(BaseModel):
    """
    LightGBM модель для регрессии.

    Обертка над LGBMRegressor, обеспечивающая единообразный интерфейс
    с другими моделями через BaseModel.

    Особенности:
    - Поддержка early stopping через callbacks
    - Автоматическое заполнение пропусков нулями
    - Логирование прогресса обучения
    - Поддержка feature importance
    """

    def build_model(self) -> LGBMRegressor:
        """
        Создает экземпляр LGBMRegressor с параметрами из self.params.
        Устанавливает стандартные параметры для регрессии, если они не указаны.

        Returns:
            Экземпляр LGBMRegressor
        """
        params = self.params.copy()

        # Устанавливаем стандартные параметры для регрессии, если не указаны
        params.setdefault("objective", "regression")
        params.setdefault("metric", "rmse")
        params.setdefault("verbose", -1)

        return LGBMRegressor(**params)

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        **kwargs,
    ):
        """
        Обучает LightGBM модель на предоставленных данных.

        Args:
            X_train: Обучающие данные (DataFrame с фичами)
            y_train: Целевая переменная для обучения
            X_val: Валидационные данные (опционально, используется для early stopping)
            y_val: Целевая переменная для валидации (опционально)
            **kwargs: Дополнительные параметры:
                - callbacks: список callbacks для LightGBM (например, early_stopping)
                - verbose: уровень детализации (по умолчанию True)
        """
        if self.is_trained:
            raise ValueError(
                f"Модель {self.name} уже обучена. "
                "Для переобучения создайте новый экземпляр модели."
            )

        # Сохраняем названия фичей
        self.feature_names = list(X_train.columns)

        # Создаем модель, если еще не создана
        if self.model is None:
            self.model = self.build_model()

        # Подготовка данных: заполняем пропуски нулями
        X_train_clean = X_train.fillna(0)

        # Настройка параметров обучения
        fit_kwargs = {}
        verbose = kwargs.get("verbose", True)

        # Настройка eval_set для валидации и early stopping
        if X_val is not None and y_val is not None:
            X_val_clean = X_val.fillna(0)
            eval_set = [(X_val_clean, y_val)]
            fit_kwargs["eval_set"] = eval_set

            # Early stopping через callbacks
            callbacks = kwargs.get("callbacks", [])
            if callbacks:
                fit_kwargs["callbacks"] = callbacks
            else:
                # Используем встроенный early stopping
                stopping_rounds = kwargs.get("stopping_rounds", 50)
                fit_kwargs["callbacks"] = [
                    lgbm.early_stopping(stopping_rounds=stopping_rounds)
                ]

            # Устанавливаем метрику для оценки (если не указана в params)
            if "eval_metric" not in fit_kwargs:
                fit_kwargs["eval_metric"] = "rmse"

        # Настройка verbose для LightGBM
        if verbose:
            # Временно переопределяем verbose в модели для вывода прогресса
            original_verbose = self.model.verbose
            self.model.verbose = 100
        else:
            original_verbose = self.model.verbose
            self.model.verbose = -1

        # Логирование прогресса
        desc = f"Обучение {self.name}"
        if X_val is not None:
            desc += " (с валидацией)"

        with tqdm(total=1, desc=desc) as pbar:
            self.model.fit(X_train_clean, y_train, **fit_kwargs)
            pbar.update(1)

        # Восстанавливаем оригинальный verbose
        self.model.verbose = original_verbose

        self.is_trained = True

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Делает предсказания на новых данных.
        Автоматически заполняет пропуски нулями перед предсказанием.

        Args:
            X: Данные для предсказания (DataFrame с фичами)

        Returns:
            Массив предсказаний
        """
        if not self.is_trained:
            raise ValueError(
                f"Модель {self.name} не обучена. Вызовите метод fit() перед predict()."
            )

        if self.model is None:
            raise ValueError(f"Модель {self.name} не инициализирована.")

        # Заполняем пропуски нулями (как при обучении)
        X_clean = X.fillna(0)

        return self.model.predict(X_clean)

    def get_best_iteration(self) -> Optional[int]:
        """
        Возвращает номер лучшей итерации (для LightGBM с early stopping).
        LightGBM сохраняет best_iteration в атрибуте best_iteration_.

        Returns:
            Номер лучшей итерации или None, если не применимо
        """
        if not self.is_trained or self.model is None:
            return None

        # LightGBM хранит best iteration в атрибуте best_iteration_
        if (
            hasattr(self.model, "best_iteration_")
            and self.model.best_iteration_ is not None
        ):
            return int(self.model.best_iteration_)

        return None
