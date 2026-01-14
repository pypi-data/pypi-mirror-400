"""
Регистр моделей для обучения.

Централизованное место для регистрации всех доступных моделей
и их конфигураций.
"""

from typing import Dict, Any, Type, Optional
from scripts.models.base import BaseModel
from scripts.models.lightgbm_model import LightGBMModel
from scripts.models.xgboost_model import XGBoostModel
from scripts.modeling_config import LIGHTGBM_PARAMS, XGBOOST_PARAMS

# Тип для записи в регистре
ModelRegistryEntry = Dict[str, Any]


def get_model_registry() -> Dict[str, ModelRegistryEntry]:
    """
    Возвращает регистр всех доступных моделей.

    Returns:
        dict с ключами - названиями моделей, значениями - конфигурацией модели
    """
    return {
        "lightgbm": {
            "class": LightGBMModel,
            "params": LIGHTGBM_PARAMS,
            "default_name": "lgbm_baseline",
            "description": "LightGBM gradient boosting model",
        },
        "lgbm": {
            "class": LightGBMModel,
            "params": LIGHTGBM_PARAMS,
            "default_name": "lgbm_baseline",
            "description": "LightGBM gradient boosting model (alias)",
        },
        "xgboost": {
            "class": XGBoostModel,
            "params": XGBOOST_PARAMS,
            "default_name": "xgb_baseline",
            "description": "XGBoost gradient boosting model",
        },
        "xgb": {
            "class": XGBoostModel,
            "params": XGBOOST_PARAMS,
            "default_name": "xgb_baseline",
            "description": "XGBoost gradient boosting model (alias)",
        },
    }


def create_model_from_registry(
    model_type: str,
    model_name: Optional[str] = None,
    custom_params: Optional[Dict[str, Any]] = None,
) -> BaseModel:
    """
    Создает экземпляр модели из регистра.

    Args:
        model_type: Тип модели (lightgbm, xgboost, etc.)
        model_name: Имя модели (если None, используется дефолтное)
        custom_params: Кастомные параметры (объединяются с дефолтными)

    Returns:
        Экземпляр модели

    Raises:
        ValueError: Если тип модели не найден в регистре
    """
    registry = get_model_registry()

    if model_type not in registry:
        available = ", ".join(registry.keys())
        raise ValueError(
            f"Неизвестный тип модели: {model_type}. Доступные типы: {available}"
        )

    model_info = registry[model_type]
    model_class: Type[BaseModel] = model_info["class"]
    model_params = model_info["params"].copy()

    # Объединяем с кастомными параметрами, если есть
    if custom_params:
        model_params.update(custom_params)

    if model_name is None:
        model_name = model_info["default_name"]

    return model_class(params=model_params, name=model_name)


def list_available_models() -> Dict[str, str]:
    """
    Возвращает список доступных моделей с их описаниями.

    Returns:
        dict с ключами - названиями моделей, значениями - описаниями
    """
    registry = get_model_registry()
    return {model_type: info["description"] for model_type, info in registry.items()}
