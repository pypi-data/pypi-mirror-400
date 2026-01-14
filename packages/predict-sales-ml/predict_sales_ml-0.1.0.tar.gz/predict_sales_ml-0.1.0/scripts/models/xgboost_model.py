from typing import Optional
import pandas as pd
import numpy as np
from xgboost import XGBRegressor
from tqdm import tqdm

from scripts.models.base import BaseModel


class XGBoostModel(BaseModel):
    """
    XGBoost модель для регрессии.
    Обертка над XGBRegressor, обеспечивающая единообразный интерфейс
    с другими моделями через BaseModel.

    Особенности:
    - Поддержка early stopping через eval_set
    - Автоматическое заполнение пропусков нулями
    - Логирование прогресса обучения
    - Поддержка feature importance
    """

    def build_model(self) -> XGBRegressor:
        """
        Создает экземпляр XGBRegressor с параметрами из self.params.
        Устанавливает стандартные параметры для регрессии, если они не указаны.

        Returns:
            Экземпляр XGBRegressor
        """
        params = self.params.copy()

        params.setdefault("objective", "reg:squarederror")
        params.setdefault("eval_metric", "rmse")
        params.setdefault("verbosity", 1)
        params.setdefault("tree_method", "hist")

        # Если не указан, устанавливаем значение по умолчанию
        if "early_stopping_rounds" not in params:
            params["early_stopping_rounds"] = 50

        return XGBRegressor(**params)

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        **kwargs,
    ):
        """
        Обучает XGBoost модель на предоставленных данных.

        Args:
            X_train: Обучающие данные (DataFrame с фичами)
            y_train: Целевая переменная для обучения
            X_val: Валидационные данные (опционально, используется для early stopping)
            y_val: Целевая переменная для валидации (опционально)
            **kwargs: Дополнительные параметры:
                - verbose: уровень детализации (по умолчанию True)
                - stopping_rounds: количество раундов для early stopping (если не указано в params)

        Note:
            Early stopping настраивается через параметр модели early_stopping_rounds,
            который передается при создании модели (build_model).
        """
        if self.is_trained:
            raise ValueError(
                f"Модель {self.name} уже обучена. "
                "Для переобучения создайте новый экземпляр модели."
            )

        self.feature_names = list(X_train.columns)

        if self.model is None:
            self.model = self.build_model()

        X_train_clean = X_train.fillna(0)

        fit_kwargs = {}
        verbose = kwargs.get("verbose", True)

        # Настройка eval_set для валидации и early stopping
        if X_val is not None and y_val is not None:
            X_val_clean = X_val.fillna(0)
            eval_set = [(X_val_clean, y_val)]
            fit_kwargs["eval_set"] = eval_set

            # Early stopping уже настроен в параметрах модели (early_stopping_rounds)
            # Не нужно передавать callbacks в fit() для XGBoost

        # Логирование прогресса
        if verbose:
            desc = f"Обучение {self.name}"
            if X_val is not None:
                desc += " (с валидацией)"

            with tqdm(total=1, desc=desc) as pbar:
                self.model.fit(X_train_clean, y_train, verbose=verbose, **fit_kwargs)
                pbar.update(1)
        else:
            self.model.fit(X_train_clean, y_train, verbose=0, **fit_kwargs)

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
        Возвращает номер лучшей итерации (для XGBoost с early stopping).
        XGBoost сохраняет best_iteration в атрибуте best_ntree_limit (старые версии)
        или best_iteration (новые версии).

        Returns:
            Номер лучшей итерации или None, если не применимо
        """
        if not self.is_trained or self.model is None:
            return None

        if (
            hasattr(self.model, "best_iteration")
            and self.model.best_iteration is not None
        ):
            return int(self.model.best_iteration)

        if (
            hasattr(self.model, "best_ntree_limit")
            and self.model.best_ntree_limit is not None
        ):
            return int(self.model.best_ntree_limit)

        return None
