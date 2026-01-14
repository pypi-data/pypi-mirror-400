from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import pandas as pd
import numpy as np


class BaseModel(ABC):
    """
    Базовый абстрактный класс для всех моделей машинного обучения.

    Этот класс определяет общий интерфейс для обучения и предсказания,
    обеспечивая единообразие работы с разными типами моделей (LightGBM, XGBoost, etc.).

    Attributes:
        params: Словарь с гиперпараметрами модели
        name: Имя модели (для логирования и идентификации)
        model: Обученная модель (sklearn-подобный объект)
        is_trained: Флаг, указывающий, обучена ли модель
        feature_names: Список названий фичей (заполняется при обучении)
    """

    def __init__(self, params: Dict[str, Any], name: Optional[str] = None):
        """
        Инициализирует базовую модель.

        Args:
            params: Словарь с гиперпараметрами для модели
            name: Имя модели. Если не указано, используется имя класса
        """
        self.params = params
        self.name = name or self.__class__.__name__
        self.model = None
        self.is_trained = False
        self.feature_names: Optional[List[str]] = None

    @abstractmethod
    def build_model(self):
        """
        Создает и возвращает экземпляр модели.

        Этот метод должен быть реализован в подклассах для создания
        конкретного типа модели (LightGBM, XGBoost, etc.).

        Returns:
            Экземпляр модели (sklearn-подобный объект)
        """
        pass

    @abstractmethod
    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        X_val: Optional[pd.DataFrame] = None,
        y_val: Optional[pd.Series] = None,
        **kwargs,
    ):
        """
        Обучает модель на предоставленных данных.

        Args:
            X_train: Обучающие данные (DataFrame с фичами)
            y_train: Целевая переменная для обучения
            X_val: Валидационные данные (опционально)
            y_val: Целевая переменная для валидации (опционально)
            **kwargs: Дополнительные параметры для обучения
                     (например, callbacks для LightGBM/XGBoost)

        Raises:
            ValueError: Если модель уже обучена и требуется переобучение
        """
        pass

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Делает предсказания на новых данных.

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

        return self.model.predict(X)

    def get_feature_importance(self) -> Optional[pd.DataFrame]:
        """
        Возвращает важность фичей, если модель поддерживает эту функциональность.

        Returns:
            DataFrame с колонками, отсортированный по убыванию важности.
            None, если модель не поддерживает feature importance.
        """
        if not self.is_trained or self.model is None:
            return None

        if not hasattr(self.model, "feature_importances_"):
            return None

        if self.feature_names is None:
            if hasattr(self.model, "feature_name_"):
                self.feature_names = self.model.feature_name_
            else:
                n_features = len(self.model.feature_importances_)
                self.feature_names = [f"feature_{i}" for i in range(n_features)]

        return pd.DataFrame(
            {
                "feature": self.feature_names,
                "importance": self.model.feature_importances_,
            }
        ).sort_values(by="importance", ascending=False)

    def get_best_iteration(self) -> Optional[int]:
        """
        Возвращает номер лучшей итерации (для моделей с early stopping).

        Returns:
            Номер лучшей итерации или None, если не применимо
        """
        if not self.is_trained or self.model is None:
            return None

        if (
            hasattr(self.model, "best_iteration_")
            and self.model.best_iteration_ is not None
        ):
            return int(self.model.best_iteration_)

        return None

    def __repr__(self) -> str:
        """Строковое представление модели."""
        status = "trained" if self.is_trained else "not trained"
        return f"{self.__class__.__name__}(name='{self.name}', status='{status}')"
