#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
from pathlib import Path

from scripts.utils_etl import (
    clean_sales_train,
    aggregate_to_monthly,
    fill_sparse_timeseries,
    enrich_items,
    enrich_categories,
    enrich_shops,
    join_with_references,
    create_basic_features,
    prepare_test_data,
    save_processed_data,
    validate_etl_results,
    encode_categorical_features,
)

import warnings

warnings.filterwarnings("ignore")


# In[2]:


raw_data_path = Path("data/raw/")
processed_data_path = Path("data/processed/")
processed_data_path.mkdir(parents=True, exist_ok=True)

sales_train = pd.read_csv(raw_data_path / "sales_train.csv")
test = pd.read_csv(raw_data_path / "test.csv")
items = pd.read_csv(raw_data_path / "items.csv")
shops = pd.read_csv(raw_data_path / "shops.csv")
item_categories = pd.read_csv(raw_data_path / "item_categories.csv")


# In[3]:


sales_train["date"] = pd.to_datetime(sales_train["date"], format="%d.%m.%Y")


# In[4]:


sales_train_clean = clean_sales_train(sales_train)

print(f"После очистки: {len(sales_train_clean):,} записей")
print(f"Удалено записей: {len(sales_train) - len(sales_train_clean):,}")

# Проверка новых столбцов
print("\nНовые столбцы:")
print(f"is_return: {sales_train_clean['is_return'].sum():,} возвратов")
print(
    f"item_cnt_day_abs: диапазон {sales_train_clean['item_cnt_day_abs'].min():.0f} - {sales_train_clean['item_cnt_day_abs'].max():.0f}"
)

print("\nЭтап 2 завершен.")


# In[5]:


print("Этап 3: Агрегация до месячного уровня")
print(f"Исходное количество записей: {len(sales_train_clean):,}")

# Применяем агрегацию
sales_monthly = aggregate_to_monthly(sales_train_clean)

print(f"После агрегации: {len(sales_monthly):,} записей")
print(f"Размерность: {sales_monthly.shape}")

# Проверка структуры
print(f"\nСтолбцы: {list(sales_monthly.columns)}")
print("\nПервые 5 строк:")
print(sales_monthly.head())

# Статистика по основным метрикам
print("\nСтатистика по item_cnt_month:")
print(sales_monthly["item_cnt_month"].describe())

print("\nЭтап 3 завершен.")


# In[6]:


# Этап 4: Обработка разреженных временных рядов

print("Этап 4: Обработка разреженных временных рядов")
print(f"Исходное количество записей: {len(sales_monthly):,}")

# Подсчет активных пар
active_pairs = sales_monthly[["shop_id", "item_id"]].drop_duplicates()
print(f"Активных пар (shop_id x item_id): {len(active_pairs):,}")

# Применяем заполнение
sales_monthly_filled = fill_sparse_timeseries(sales_monthly)

print(f"После заполнения: {len(sales_monthly_filled):,} записей")
print(f"Ожидаемое количество: {len(active_pairs) * 34:,} (пары x 34 месяца)")

# Проверка заполнения
print("\nПроверка заполнения:")
print(
    f"  Записей с item_cnt_month = 0: {(sales_monthly_filled['item_cnt_month'] == 0).sum():,}"
)
print(
    f"  Записей с item_cnt_month > 0: {(sales_monthly_filled['item_cnt_month'] > 0).sum():,}"
)

# Проверка пропусков
print("\nПроверка пропусков:")
print(sales_monthly_filled.isnull().sum())

# Пример: проверка одной пары
example_pair = sales_monthly_filled[
    (sales_monthly_filled["shop_id"] == 0) & (sales_monthly_filled["item_id"] == 30)
].head(10)
print("\nПример: shop_id=0, item_id=30 (первые 10 месяцев):")
print(example_pair[["date_block_num", "item_cnt_month", "item_price_median"]])

print("\nЭтап 4 завершен.")


# In[7]:


print("Этап 5: Обогащение справочниками")

# Обогащаем items
print("\n1. Обогащение items...")
items_enriched = enrich_items(items, item_categories, sales_train_clean)
print(
    f"Добавлены колонки: {[col for col in items_enriched.columns if col not in items.columns]}"
)
print("Пример:")
print(
    items_enriched[
        ["item_id", "item_name", "main_category", "sub_category", "has_sales_history"]
    ].head()
)

# Обогащаем shops
print("\n2. Обогащение shops...")
shops_enriched = enrich_shops(shops)
print(
    f"Добавлены колонки: {[col for col in shops_enriched.columns if col not in shops.columns]}"
)
print("Пример:")
print(
    shops_enriched[
        ["shop_id", "shop_name", "city", "shop_type", "is_online", "is_franchise"]
    ].head()
)

# Обогащаем item_categories
print("\n3. Обогащение item_categories...")
item_categories_enriched = enrich_categories(item_categories)
print(
    f"Добавлены колонки: {[col for col in item_categories_enriched.columns if col not in item_categories.columns]}"
)
print("Пример:")
print(item_categories_enriched.head())

print("\nЭтап 5 завершен.")


# In[8]:


print("Этап 6: Джойн данных")
print(f"Исходное количество записей: {len(sales_monthly_filled):,}")

# Применяем джойн
sales_monthly_enriched = join_with_references(
    sales_monthly_filled, items_enriched, shops_enriched
)

print(f"После джойна: {len(sales_monthly_enriched):,} записей")
print(f"Размерность: {sales_monthly_enriched.shape}")

# Проверка структуры
print(f"\nСтолбцы ({len(sales_monthly_enriched.columns)}):")
print(list(sales_monthly_enriched.columns))

# Проверка пропусков
print("\nПроверка пропусков:")
missing = sales_monthly_enriched.isnull().sum()
print(missing[missing > 0])

# Пример данных
print("\nПример данных (первые 3 строки):")
print(sales_monthly_enriched.head(3))

print("\nЭтап 6 завершен.")


# In[9]:


print("Этап 7: Создание базовых фичей")
print(f"Исходное количество записей: {len(sales_monthly_enriched):,}")

sales_monthly_with_features = create_basic_features(sales_monthly_enriched)

print(f"После создания фичей: {len(sales_monthly_with_features):,} записей")
print(f"Размерность: {sales_monthly_with_features.shape}")

# Проверка созданных фичей
print("\nСозданные фичи:")
new_features = [
    "month",
    "year",
    "is_holiday_season",
    "lag_1",
    "lag_2",
    "lag_3",
    "lag_6",
    "lag_12",
    "mean_3m",
    "mean_6m",
    "mean_12m",
    "item_total_sales",
    "item_avg_price",
    "shop_total_sales",
]
print(
    f"  Временные: {[f for f in new_features if f in ['month', 'year', 'is_holiday_season']]}"
)
print(f"  Лаги: {[f for f in new_features if f.startswith('lag_')]}")
print(f"  Скользящие средние: {[f for f in new_features if f.startswith('mean_')]}")
print(f"  Агрегаты по товару: {[f for f in new_features if f.startswith('item_')]}")
print(f"  Агрегаты по магазину: {[f for f in new_features if f.startswith('shop_')]}")

# Проверка пропусков в новых фичах
print("\nПроверка пропусков в фичах:")
missing = sales_monthly_with_features[new_features].isnull().sum()
print(missing[missing > 0])

# Пример данных
print("\nПример данных (shop_id=0, item_id=30, первые 5 месяцев):")
example = sales_monthly_with_features[
    (sales_monthly_with_features["shop_id"] == 0)
    & (sales_monthly_with_features["item_id"] == 30)
].head(5)
print(
    example[
        [
            "date_block_num",
            "month",
            "year",
            "item_cnt_month",
            "lag_1",
            "lag_2",
            "mean_3m",
        ]
    ]
)

print("\nЭтап 7 завершен.")

print("\nЭтап 7.5: Кодирование категориальных признаков")
print(f"Исходное количество записей: {len(sales_monthly_with_features):,}")

sales_monthly_with_features_encoded, label_encoders = encode_categorical_features(
    sales_monthly_with_features
)

print(f"После кодирования: {len(sales_monthly_with_features_encoded):,} записей")
print(f"Размерность: {sales_monthly_with_features_encoded.shape}")
print("Новые колонки после кодирования:")
new_cols = [
    col
    for col in sales_monthly_with_features_encoded.columns
    if col not in sales_monthly_with_features.columns
]
print(f"  Добавлено колонок: {len(new_cols)}")
print(f"  Примеры: {new_cols[:10]}")

print("\nЭтап 7.5 завершен.")
# In[10]:


print("Этап 8: Подготовка тестовых данных")
print(f"Исходное количество записей в test: {len(test):,}")

# Применяем подготовку тестовых данных
test_enriched = prepare_test_data(
    test, sales_monthly_with_features, items_enriched, shops_enriched
)

print(f"После подготовки: {len(test_enriched):,} записей")
print(f"Размерность: {test_enriched.shape}")

# Проверка структуры
print(f"\nСтолбцы ({len(test_enriched.columns)}):")
print(list(test_enriched.columns))

# Проверка флагов истории
print("\nПроверка флагов истории:")
print(f"  Товаров с историей: {test_enriched['has_sales_history'].sum():,}")
print(f"  Новых товаров: {(~test_enriched['has_sales_history']).sum():,}")
print(f"  Пар с историей: {test_enriched['has_pair_history'].sum():,}")
print(f"  Новых пар: {(~test_enriched['has_pair_history']).sum():,}")

# Проверка пропусков
print("\nПроверка пропусков:")
missing = test_enriched.isnull().sum()
print(missing[missing > 0])

# Пример данных
print("\nПример данных (первые 3 строки):")
print(test_enriched.head(3))

# Пример новых пар
print("\nПример новых пар (без истории):")
new_pairs = test_enriched[~test_enriched["has_pair_history"]].head(3)
print(
    new_pairs[
        [
            "ID",
            "shop_id",
            "item_id",
            "has_sales_history",
            "has_pair_history",
            "main_category",
            "city",
            "shop_type",
        ]
    ]
)

print("\nЭтап 8 завершен.")

print("\nЭтап 8.5: Кодирование категориальных признаков в test")
print(f"Исходное количество записей: {len(test_enriched):,}")

test_enriched_encoded, _ = encode_categorical_features(
    test_enriched, label_encoders=label_encoders
)

print(f"После кодирования: {len(test_enriched_encoded):,} записей")
print(f"Размерность: {test_enriched_encoded.shape}")
print("Новые колонки после кодирования:")
new_cols_test = [
    col for col in test_enriched_encoded.columns if col not in test_enriched.columns
]
print(f"  Добавлено колонок: {len(new_cols_test)}")
print(f"  Примеры: {new_cols_test[:10]}")

print("\nЭтап 8.5 завершен.")
# In[11]:


print("Этап 9: Валидация и отчетность")

validation_results = validate_etl_results(
    sales_train_original=sales_train,
    sales_train_clean=sales_train_clean,
    sales_monthly=sales_monthly,
    sales_monthly_with_features=sales_monthly_with_features,
    test_enriched=test_enriched,
    items_enriched=items_enriched,
    shops_enriched=shops_enriched,
    item_categories_enriched=item_categories_enriched,
    sales_monthly_with_features_encoded=sales_monthly_with_features_encoded,
    test_enriched_encoded=test_enriched_encoded,
)

print("\nЭтап 9 завершен.")


# In[12]:


print("Этап 10: Сохранение обработанных данных")

save_processed_data(
    sales_monthly=sales_monthly,
    sales_monthly_with_features=sales_monthly_with_features,
    test_enriched=test_enriched,
    items_enriched=items_enriched,
    shops_enriched=shops_enriched,
    item_categories_enriched=item_categories_enriched,
    output_path=processed_data_path,
    sales_monthly_with_features_encoded=sales_monthly_with_features_encoded,
    test_enriched_encoded=test_enriched_encoded,
)

print("\nЭтап 10 завершен.")
