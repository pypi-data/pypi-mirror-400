#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np

from scripts.utils_dqc import (
    check_completeness,
    check_accuracy,
    check_consistency,
    check_validity,
    check_uniqueness,
    check_integrity,
    check_timeliness,
    check_poor_dynamic,
)

import warnings

warnings.filterwarnings("ignore")


# In[2]:


data_path = "data/raw/"

sales_train = pd.read_csv(data_path + "sales_train.csv")
test = pd.read_csv(data_path + "test.csv")
items = pd.read_csv(data_path + "items.csv")
shops = pd.read_csv(data_path + "shops.csv")
item_categories = pd.read_csv(data_path + "item_categories.csv")
sample_submission = pd.read_csv(data_path + "sample_submission.csv")


# In[3]:


# Проверка полноты данных: sales_train.csv
sales_train_completeness = check_completeness(
    sales_train, threshold=0.95, name="sales_train"
)


# In[4]:


# Проверка полноты данных: test.csv
test_completeness = check_completeness(test, threshold=1.0, name="test")


# In[5]:

# Проверка полноты данных: items.csv
items_completeness = check_completeness(items, threshold=1.0, name="items")


# In[6]:

# Проверка полноты данных: shops.csv
shops_completeness = check_completeness(shops, threshold=1.0, name="shops")


# In[7]:


# Проверка полноты данных: item_categories.csv
item_categories_completeness = check_completeness(
    item_categories, threshold=1.0, name="item_categories"
)


# In[8]:


# Проверка полноты данных: sample_submission.csv
sample_submission_completeness = check_completeness(
    sample_submission, threshold=1.0, name="sample_submission"
)


# In[9]:


# Сводная таблица результатов проверки completeness
completeness_summary = pd.DataFrame(
    {
        "Dataset": [
            "sales_train",
            "test",
            "items",
            "shops",
            "item_categories",
            "sample_submission",
        ],
        "Overall Completeness": [
            sales_train_completeness["overall_completeness"],
            test_completeness["overall_completeness"],
            items_completeness["overall_completeness"],
            shops_completeness["overall_completeness"],
            item_categories_completeness["overall_completeness"],
            sample_submission_completeness["overall_completeness"],
        ],
        "Passed": [
            sales_train_completeness["passed"],
            test_completeness["passed"],
            items_completeness["passed"],
            shops_completeness["passed"],
            item_categories_completeness["passed"],
            sample_submission_completeness["passed"],
        ],
    }
)

print("\n" + "=" * 60)
print("Сводная таблица: Проверка полноты данных (Completeness)")
print("=" * 60)
print(completeness_summary.to_string(index=False))
print()

# Подсчет проблемных датасетов
failed_datasets = completeness_summary[~completeness_summary["Passed"]]
if len(failed_datasets) > 0:
    print(f"ВНИМАНИЕ: {len(failed_datasets)} датасет(ов) не прошли проверку:")
    for _, row in failed_datasets.iterrows():
        print(f"- {row['Dataset']}: полнота {row['Overall Completeness'] * 100:.2f}%")
else:
    print("Все датасеты прошли проверку на полноту!")


# In[10]:


valid_item_ids = set(items["item_id"])
valid_shop_ids = set(shops["shop_id"])

sales_accuracy_rules = {
    # 1. date_block_num: только 0–33
    "date_block_num": lambda s: s.between(0, 33),
    # 2. item_price:
    #   - строго положительная
    #   - не превышает порог
    "item_price": lambda s: (s > 0) & (s <= 100_000),
    # 3. item_cnt_day:
    #   - допускаем возвраты (s >= -22), но
    #   - ограничиваем верх по аномалиям (<= 1000, как в EDA)
    "item_cnt_day": lambda s: (s >= -22) & (s <= 1000),
    # 4. item_id и shop_id должны быть в справочниках
    "item_id": lambda s: s.isin(valid_item_ids),
    "shop_id": lambda s: s.isin(valid_shop_ids),
}

sales_accuracy = check_accuracy(sales_train, sales_accuracy_rules, name="sales_train")


# In[11]:


valid_category_ids = set(item_categories["item_category_id"])

items_accuracy_rules = {
    "item_id": lambda s: s >= 0,
    "item_category_id": lambda s: s.isin(valid_category_ids),
    "item_name": lambda s: s.str.len().between(3, 255),
}

items_accuracy = check_accuracy(items, items_accuracy_rules, name="items")


# In[12]:


item_categories_accuracy_rules = {
    "item_category_id": lambda s: s >= 0,
    "item_category_name": lambda s: s.str.len().between(3, 255),
}

item_categories_accuracy_result = check_accuracy(
    item_categories, item_categories_accuracy_rules, name="item_categories"
)


# In[13]:


shops_accuracy_rules = {
    "shop_id": lambda s: s >= 0,
    "shop_name": lambda s: s.str.len().between(3, 100),
}

shops_accuracy_result = check_accuracy(shops, shops_accuracy_rules, name="shops")


# In[14]:


test_accuracy_rules = {
    "ID": lambda s: (s >= 0) & (s < len(test)),
    "shop_id": lambda s: s.isin(valid_shop_ids),
    "item_id": lambda s: s.isin(valid_item_ids),
}

test_accuracy_result = check_accuracy(test, test_accuracy_rules, name="test")


# In[15]:


valid_submission_ids = set(test["ID"])

sample_submission_accuracy_rules = {"ID": lambda s: s.isin(valid_submission_ids)}

sample_submission_accuracy_result = check_accuracy(
    sample_submission, sample_submission_accuracy_rules, name="sample_submission"
)


# In[16]:


# проверка соответствия date и date_block_num
def rule_date_matches_block(df: pd.DataFrame) -> pd.Series:
    dates = pd.to_datetime(df["date"], format="%d.%m.%Y", errors="coerce")
    month_index = (dates.dt.year - 2013) * 12 + (dates.dt.month - 1)
    return dates.notna() & (month_index == df["date_block_num"])


# проверка соответствия shop_id со справочником shops
def rule_train_shops_in_reference(df: pd.DataFrame) -> bool:
    train_shops = set(df["shop_id"].unique())
    return train_shops.issubset(valid_shop_ids)


# проверка соответствия item_id со справочником items
def rule_train_items_in_reference(df: pd.DataFrame) -> bool:
    train_items = set(df["item_id"].unique())
    return train_items.issubset(valid_item_ids)


sales_train_consistency_rules = [
    rule_date_matches_block,
    rule_train_shops_in_reference,
    rule_train_items_in_reference,
]

sales_consistency_result = check_consistency(
    sales_train, sales_train_consistency_rules, name="sales_train"
)


# In[17]:


# проверка соответствия shop_id со справочником shops
def rule_test_shops_in_reference(df: pd.DataFrame) -> bool:
    return set(df["shop_id"].unique()).issubset(valid_shop_ids)


# проверка соответствия item_id со справочником items
def rule_test_items_in_reference(df: pd.DataFrame) -> bool:
    return set(df["item_id"].unique()).issubset(valid_item_ids)


# проверка что все магазины из test есть в train
def rule_test_shops_in_train(df: pd.DataFrame) -> bool:
    return set(df["shop_id"].unique()).issubset(set(sales_train["shop_id"].unique()))


# проверка какие товары из test есть в train
def rule_test_items_in_train(df: pd.DataFrame) -> pd.Series:
    train_items = set(sales_train["item_id"].unique())
    return df["item_id"].isin(train_items)


# проверка какие пары shop_id×item_id из test есть в train
def rule_test_pairs_in_train(df: pd.DataFrame) -> pd.Series:
    train_pairs = set(zip(sales_train["shop_id"], sales_train["item_id"]))
    test_pairs = list(zip(df["shop_id"], df["item_id"]))
    return pd.Series([p in train_pairs for p in test_pairs], index=df.index)


test_consistency_rules = [
    rule_test_shops_in_reference,
    rule_test_items_in_reference,
    rule_test_shops_in_train,
    rule_test_items_in_train,
    rule_test_pairs_in_train,
]

test_consistency = check_consistency(test, test_consistency_rules, name="test")


# In[18]:


# проверка использования магазинов в данных
def rule_shops_used_in_data(df: pd.DataFrame) -> pd.Series:
    used_shops = set(sales_train["shop_id"].unique()) | set(test["shop_id"].unique())
    return df["shop_id"].isin(used_shops)


shops_consistency_rules = [rule_shops_used_in_data]

shops_consistency = check_consistency(shops, shops_consistency_rules, name="shops")


# In[19]:


# проверка соответствия item_category_id со справочником item_categories
def rule_items_categories_in_reference(df: pd.DataFrame) -> bool:
    items_cats = set(df["item_category_id"].unique())
    return items_cats.issubset(valid_category_ids)


# проверка использования товаров в данных
def rule_items_used_in_data(df: pd.DataFrame) -> pd.Series:
    used_items = set(sales_train["item_id"].unique()) | set(test["item_id"].unique())
    return df["item_id"].isin(used_items)


items_consistency_rules = [
    rule_items_categories_in_reference,
    rule_items_used_in_data,
]

items_consistency = check_consistency(items, items_consistency_rules, name="items")


# In[20]:


# проверка использования категорий в items
def rule_categories_used_in_items(df: pd.DataFrame) -> pd.Series:
    return df["item_category_id"].isin(set(items["item_category_id"].unique()))


item_categories_consistency_rules = [rule_categories_used_in_items]

item_categories_consistency = check_consistency(
    item_categories, item_categories_consistency_rules, name="item_categories"
)


# In[21]:


# проверка соответствия ID с test
def rule_submission_ids_match_test(df: pd.DataFrame) -> bool:
    return set(df["ID"].unique()) == set(test["ID"].unique())


# проверка порядка ID с test
def rule_submission_order_matches_test(df: pd.DataFrame) -> bool:
    return (df["ID"].values == test["ID"].values).all()


sample_submission_consistency_rules = [
    rule_submission_ids_match_test,
    rule_submission_order_matches_test,
]

sample_submission_consistency = check_consistency(
    sample_submission, sample_submission_consistency_rules, name="sample_submission"
)


# In[22]:


# проверка формата даты
sales_train_validity_rules = {
    "date": lambda s: pd.to_datetime(s, format="%d.%m.%Y", errors="coerce").notna(),
    "date_block_num": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "shop_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "item_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "item_price": lambda s: pd.api.types.is_numeric_dtype(s),
    "item_cnt_day": lambda s: pd.api.types.is_numeric_dtype(s),
}

sales_train_validity = check_validity(
    sales_train, sales_train_validity_rules, name="sales_train"
)


# In[23]:


test_validity_rules = {
    "ID": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "shop_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "item_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
}

test_validity = check_validity(test, test_validity_rules, name="test")


# In[24]:


items_validity_rules = {
    "item_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "item_name": lambda s: s.apply(lambda x: isinstance(x, str)),
    "item_category_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
}

items_validity = check_validity(items, items_validity_rules, name="items")


# In[25]:


shops_validity_rules = {
    "shop_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "shop_name": lambda s: s.apply(lambda x: isinstance(x, str)),
}

shops_validity = check_validity(shops, shops_validity_rules, name="shops")


# In[26]:


item_categories_validity_rules = {
    "item_category_id": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "item_category_name": lambda s: s.apply(lambda x: isinstance(x, str)),
}

item_categories_validity = check_validity(
    item_categories, item_categories_validity_rules, name="item_categories"
)


# In[27]:


sample_submission_validity_rules = {
    "ID": lambda s: s.apply(lambda x: isinstance(x, (int, np.integer))),
    "item_cnt_month": lambda s: pd.api.types.is_numeric_dtype(s),
}

sample_submission_validity = check_validity(
    sample_submission, sample_submission_validity_rules, name="sample_submission"
)


# In[28]:


# ========== UNIQUENESS: sales_train.csv ==========
sales_train_uniqueness = check_uniqueness(
    sales_train,
    ["date", "shop_id", "item_id", "item_price", "item_cnt_day"],
    name="sales_train",
)


# In[ ]:


# ========== UNIQUENESS: test.csv ==========
test_uniqueness = check_uniqueness(test, ["ID", "shop_id", "item_id"], name="test")


# In[30]:


# ========== UNIQUENESS: items.csv ==========
items_uniqueness = check_uniqueness(items, ["item_id", "item_name"], name="items")


# In[31]:


# ========== UNIQUENESS: shops.csv ==========
shops_uniqueness = check_uniqueness(shops, ["shop_id", "shop_name"], name="shops")


# In[32]:


# ========== UNIQUENESS: item_categories.csv ==========
item_categories_uniqueness = check_uniqueness(
    item_categories, ["item_category_id", "item_category_name"], name="item_categories"
)


# In[33]:


# ========== UNIQUENESS: sample_submission.csv ==========
sample_submission_uniqueness = check_uniqueness(
    sample_submission, "ID", name="sample_submission"
)


# In[ ]:


# ========== INTEGRITY: sales_train.csv ==========
# проверка целостности shop_id относительно shops
sales_train_integrity_shops = check_integrity(
    sales_train,
    shops,
    {"shop_id": "shop_id"},
    name="sales_train",
    reference_name="shops",
)

# проверка целостности item_id относительно items
sales_train_integrity_items = check_integrity(
    sales_train,
    items,
    {"item_id": "item_id"},
    name="sales_train",
    reference_name="items",
)


# In[35]:


# ========== INTEGRITY: test.csv ==========
# проверка целостности shop_id относительно shops
test_integrity_shops = check_integrity(
    test, shops, {"shop_id": "shop_id"}, name="test", reference_name="shops"
)

# проверка целостности item_id относительно items
test_integrity_items = check_integrity(
    test, items, {"item_id": "item_id"}, name="test", reference_name="items"
)


# In[36]:


# ========== INTEGRITY: test.csv ==========
# проверка целостности shop_id относительно shops
test_integrity_shops = check_integrity(
    test, shops, {"shop_id": "shop_id"}, name="test", reference_name="shops"
)

# проверка целостности item_id относительно items
test_integrity_items = check_integrity(
    test, items, {"item_id": "item_id"}, name="test", reference_name="items"
)


# In[37]:


# ========== INTEGRITY: items.csv ==========
# проверка целостности item_category_id относительно item_categories
items_integrity_categories = check_integrity(
    items,
    item_categories,
    {"item_category_id": "item_category_id"},
    name="items",
    reference_name="item_categories",
)


# In[38]:


# ========== INTEGRITY: sample_submission.csv ==========
# проверка целостности ID относительно test
sample_submission_integrity = check_integrity(
    sample_submission,
    test,
    {"ID": "ID"},
    name="sample_submission",
    reference_name="test",
)


# In[39]:


# ========== TIMELINESS ==========
# Проверка непрерывности по месяцам для каждой пары shop_id × item_id
sales_timeliness_shop_item = check_timeliness(
    df=sales_train,
    date_column="date",
    period_column="date_block_num",
    group_columns=["shop_id", "item_id"],
    expected_periods=list(range(34)),  # месяцы 0–33
    name="sales_train (shop_id, item_id)",
)


# In[40]:


# ========== POOR DYNAMIC ==========
sales_poor_dynamic_shop_item = check_poor_dynamic(
    df=sales_train,
    date_column="date",
    period_column="date_block_num",
    value_column="item_cnt_day",
    group_columns=["shop_id", "item_id"],
    name="sales_train (shop_id, item_id)",
)

sales_poor_dynamic_shop = check_poor_dynamic(
    df=sales_train,
    date_column="date",
    period_column="date_block_num",
    value_column="item_cnt_day",
    group_columns=["shop_id"],
    name="sales_train (shop_id)",
)


# ## Data Quality Check (DQC) Layer — Итоговый отчет и связь с ETL
#
# Этот ноутбук `02_DQC.ipynb` реализует полноценный **Data Quality Check (DQC) layer** для всех исходных датасетов соревнования:
#
# - `sales_train.csv`
# - `test.csv`
# - `items.csv`
# - `shops.csv`
# - `item_categories.csv`
# - `sample_submission.csv`
#
# Цель DQC: **явно зафиксировать качество данных** и получить входные сигналы для **ETL-слоя**, который будет:
#
# - очищать/нормализовать данные,
# - помечать проблемные записи,
# - выбирать разные стратегии обработки для разных типов наблюдений (особенно в `test.csv`).
#
# Ниже — сводка по каждому измерению качества и его роли в ETL.
#
# ---
#
# ### 1. Completeness (Полнота)
#
# **Что проверяем**
#
# С помощью `check_completeness` по всем датасетам:
#
# - `sales_train`: `date`, `date_block_num`, `shop_id`, `item_id`, `item_price`, `item_cnt_day`
# - `test`: `ID`, `shop_id`, `item_id`
# - `items`: `item_name`, `item_id`, `item_category_id`
# - `shops`: `shop_id`, `shop_name`
# - `item_categories`: `item_category_id`, `item_category_name`
# - `sample_submission`: `ID`, `item_cnt_month`
#
# **Выводы DQC**
#
# - Пропусков в ключевых столбцах нет.
# - Все датасеты проходят пороги completeness (0.95–1.0).
#
# **Что делает ETL на основе этого**
#
# - Не требуется сложный глобальный imputing пропусков.
# - ETL может считать, что:
#   - все ключи (`ID`, `shop_id`, `item_id`, `item_category_id`) всегда заданы,
#   - все записи имеют дату, цену и количество.
# - Любая работа с отсутствием информации будет относиться скорее к **отсутствию истории** (например, новые товары/пары), а не к техническим NaN.
#
# ---
#
# ### 2. Accuracy (Точность значений)
#
# **Инструмент**: `check_accuracy`
# **Идея**: задать **разумные допустимые диапазоны и правила** для числовых полей и ID.
#
# #### 2.1. `sales_train.csv`
#
# **Правила:**
#
# - `date_block_num`: `0 ≤ value ≤ 33`.
# - `item_price`:
#   - `item_price > 0` — отбрасываем очевидные ошибки (`-1`).
#   - `item_price ≤ 100_000` — отсекаем экстремальный выброс `307980`.
# - `item_cnt_day`:
#   - допускаем возвраты: `item_cnt_day ≥ -22`,
#   - ограничиваем экстремальные значения сверху: `item_cnt_day ≤ 1000`.
# - `item_id` и `shop_id`:
#   - проверка на **вхождение в справочники** `items` и `shops`.
#
# **Наблюдения:**
#
# - Технически все поля проходят правила с единичными нарушениями:
#   - 1 запись с `item_price <= 0`,
#   - 1 запись с `item_price >> разумного диапазона`,
#   - 1 запись с `item_cnt_day > 1000`.
#
# **Решения для ETL:**
#
# - **Цены (`item_price`)**:
#   - ETL может:
#     - либо **удалить** записи с `item_price <= 0` и `item_price > X` (например, `X = 100_000`),
#     - либо **обрезать** по верху (например, на 99-м перцентиле или фиксированном пороге).
# - **Количество (`item_cnt_day`)**:
#   - `item_cnt_day > 1000`:
#     - рассматривать как явный выброс - удалить/обрезать.
#   - `item_cnt_day < 0`:
#     - **не ошибка**, а **возвраты** - важный бизнес-сигнал:
#       - в ETL можно:
#         - хранить их отдельно,
#         - использовать как фичу, а не удалять.
#
# #### 2.2. Остальные таблицы
#
# - Проверки типов, диапазонов и принадлежности:
#   - `items`: `item_id ≥ 0`, `item_category_id` в справочнике, разумная длина `item_name`.
#   - `shops`: `shop_id ≥ 0`, разумная длина `shop_name`.
#   - `item_categories`: `item_category_id ≥ 0`, разумная длина `item_category_name`.
#   - `test`, `sample_submission`: корректный диапазон/тип `ID`, принадлежность ID нужным наборам.
#
# **Решения для ETL:**
#
# - Можно **считать типы и диапазоны валидными** и не добавлять дополнительные фильтры по типам/диапазонам в ETL, кроме обработки крайних аномалий в `sales_train`.
#
# ---
#
# ### 3. Consistency (Согласованность)
#
# **Инструмент**: `check_consistency`
# **Идея**: проверить согласованность **внутри таблиц** и **между таблицами**.
#
# #### 3.1. Внутри `sales_train.csv`
#
# - `date` - `date_block_num`:
#   - `rule_date_matches_block` проверяет, что:
#     - дата парсится по формату `%d.%m.%Y`,
#     - номер месяца (`date_block_num`) соответствует периоду от января 2013 до октября 2015.
#   - Согласованность 100%.
#
# - Связь с `shops`:
#   - все `shop_id` из `sales_train` есть в `shops`.
#
# - Связь с `items`:
#   - все `item_id` из `sales_train` есть в `items`.
#
# **Решения для ETL:**
#
# - Можно без опасений использовать:
#   - `date_block_num` как основную временную ось (для агрегаций и фичей),
#   - джойны по `shop_id` и `item_id` — **без потерь**.
#
# #### 3.2. `test.csv` - `sales_train.csv` и справочники
#
# - Магазины (`shop_id`):
#   - все `shop_id` из `test`:
#     - есть в `shops`,
#     - есть в `sales_train`.
#   - В `sales_train` есть магазины, которых **нет** в `test` (18 штук) — это нормально.
#
# - Товары (`item_id`):
#   - все `item_id` из `test` есть в `items`.
#   - ~**7.12%** `item_id` из `test` (363 товара) **никогда не встречались** в `sales_train`.
#
# - Комбинации `shop_id x item_id`:
#   - **52.01%** пар `shop x item` из `test` уже были в `train`.
#   - **47.99%** — **новые пары**, которых не было в `sales_train`.
#
# **Решения для ETL:**
#
# - В ETL-слое имеет смысл **ввести флаги** для строк `test`:
#   - `has_item_history` — товар есть в `sales_train`,
#   - `has_pair_history` — пара `shop x item` есть в `sales_train`,
#   - `is_new_item` — товар в `test`, но отсутствует в `sales_train`.
#
# - На эти флаги можно завязать:
#   - **разные стратегии генерации признаков**:
#     - для наблюдений с историей пары — использовать детальные лаги и статистики,
#     - для новых пар — использовать агрегаты по магазину, товару, категории,
#     - для новых товаров — преимущественно признаки категории/магазина/глобальные тренды.
#   - **разные стратегии обработки прогноза** (например, иные значения для новых комбинаций).
#
# #### 3.3. `items`, `item_categories`, `shops`
#
# - `items` - `item_categories`:
#   - все `item_category_id` в `items` есть в `item_categories`.
#   - все категории из `item_categories` используются.
#
# - `shops`:
#   - все магазины из справочника присутствуют в данных (train/test).
#
# **Решения для ETL:**
#
# - Джойны:
#   - `sales_train` -> `items` -> `item_categories`,
#   - `sales_train` -> `shops`,
#   - `test` -> те же справочники,
#   — можно делать **без фильтрации по “потерянным” ключам**.
#
# ---
#
# ### 4. Validity (Валидность)
#
# **Инструмент**: `check_validity`
# **Идея**: убедиться, что значения соответствуют ожидаемым **типам и форматам**.
#
# Проверки:
#
# - `sales_train`:
#   - `date` — корректно парсится как дата,
#   - `date_block_num`, `shop_id`, `item_id` — целые,
#   - `item_price`, `item_cnt_day` — числовые.
#
# - `test`, `items`, `shops`, `item_categories`, `sample_submission`:
#   - ID — целые,
#   - текстовые поля — строки,
#   - значения-таргеты (`item_cnt_month`) — числовые.
#
# **Решения для ETL:**
#
# - ETL может:
#   - не делать дополнительных кастов типов (кроме, возможно, приведения к нужному формату в хранилище),
#   - считать, что нарушения валидности — либо отсутствуют, либо находятся на уровне единичных строк и могут быть **просто отфильтрованы**.
#
# ---
#
# ### 5. Uniqueness (Уникальность)
#
# **Инструмент**: `check_uniqueness`
# **Идея**: проверить, где у нас **уникальные ключи**, а где — **многократные наблюдения**.
#
# Основные результаты:
#
# - `test`:
#   - `ID` — 100% уникален -> можно использовать как **основной ключ** для предсказаний.
#   - `shop_id`, `item_id` — не уникальны.
#
# - `items`:
#   - `item_id` и `item_name` — 100% уникальны.
#
# - `shops`:
#   - `shop_id` и `shop_name` — 100% уникальны.
#
# - `item_categories`:
#   - `item_category_id` и `item_category_name` — 100% уникальны.
#
# - `sample_submission`:
#   - `ID` — 100% уникален.
#
# - `sales_train`:
#   - поля по отдельности (`date`, `shop_id`, `item_id`, `item_price`, `item_cnt_day`) не уникальны (ожидаемо — это транзакции).
#
# **Решения для ETL:**
#
# - **Ключи:**
#   - `items`: `item_id` как PK.
#   - `shops`: `shop_id` как PK.
#   - `item_categories`: `item_category_id` как PK.
#   - `test` и `sample_submission`: `ID` как PK (и линк между ними).
# - **sales_train**:
#   - нужно агрегировать (например, до уровня месячных продаж `item_cnt_month` по `shop_id x item_id x date_block_num`) в ETL.
#
# ---
#
# ### 6. Integrity (Целостность внешних ключей)
#
# **Инструмент**: `check_integrity`
# **Проверки:**
#
# - `sales_train`:
#   - `shop_id` -> `shops.shop_id`
#   - `item_id` -> `items.item_id`
#
# - `test`:
#   - `shop_id` -> `shops.shop_id`
#   - `item_id` -> `items.item_id`
#
# - `items`:
#   - `item_category_id` -> `item_categories.item_category_id`
#
# - `sample_submission`:
#   - `ID` -> `test.ID`
#
# **Результаты:**
#
# - Все проверки целостности проходят на 100%, примеры невалидных значений отсутствуют.
#
# **Решения для ETL:**
#
# - Можно использовать внешние ключи
#
# ---
#
# ### 7. Timeliness (Актуальность, непрерывность временных рядов)
#
# **Инструмент**: `check_timeliness`
# **Что проверяется:**
#
# - Непрерывность по месяцам для каждой пары `shop_id x item_id` в `sales_train` (периоды 0–33).
#
# **Результаты:**
#
# - Всего групп (пар `shop_id x item_id`): **424,124**.
# - Групп с пропусками месяцев: **424,022** (~99.98%).
# - Среднее количество пропусков на группу: **≈ 30.21** месяцев из 34.
# - Топ-группы с максимальным количеством пропусков — пары, которые были активны только в 1–2 месяцах.
#
# **Интерпретация:**
#
# - Это **разреженные временные ряды**, что ожидаемо:
#   - большинство комбинаций `shop x item` продаются только в несколько месяцев из всех 34-х.
# - Это не обязательно ошибка качества, а **характеристика бизнес-процесса**.
#
# **Решения для ETL:**
#
# - При построении фичей:
#   - важно **явно учитывать нули и пропуски**:
#     - нули продаж могут означать “нет продаж в этом месяце” (не ошибка),
#     - отсутствие записи → в ETL можно интерпретировать как “0 продаж” при агрегации.
#   - стоит аккуратно генерировать временные фичи (лаги, скользящие средние):
#     - заполнять пропущенные месяцы нулями,
#     - не трактовать разреженность как техническую ошибку.
#
# ---
#
# ### 8. Poor Dynamic (Плохая динамика продаж)
#
# **Инструмент**: `check_poor_dynamic`
# **Что проверяется:**
#
# - Для агрегированных временных рядов:
#   - `shop_id x item_id`,
#   - отдельно по `shop_id`.
# - Анализируется:
#   - количество периодов с нулевыми продажами,
#   - резкие падения (drop ≥ 80%),
#   - резкий рост (growth ≥ 5 раз).
#
# **Результаты (пример по `sales_train`):**
#
# - По `shop_id x item_id`:
#   - всего групп: **424,124**,
#   - групп с нулевыми продажами: **2,543** (~0.60%),
#   - групп с резкими падениями: **14,625** (~3.45%),
#   - групп с резким ростом: **6,704** (~1.58%).
#
# - По `shop_id` (агрегация по магазину):
#   - всего магазинов: **60**,
#   - групп с нулевыми продажами: 0,
#   - магазинов с резкими падениями: 4,
#   - магазинов с резким ростом: 3.
#
# **Интерпретация:**
#
# - На уровне пар `shop x item`:
#   - много серий с редкими продажами -> нормально.
#   - резкие скачки/падения:
#     - могут быть как реальными акциями/поставками, так и выбросами.
# - На уровне магазинов:
#   - большинство магазинов ведут себя плавно,
#   - несколько магазинов имеют подозрительные изменения динамики.
#
# **Решения для ETL:**
#
# - Для **ETL и последующего моделирования**:
#   - можно метить группы (магазины/пары) флагами:
#     - `has_sudden_drop`,
#     - `has_sudden_growth`,
#     - `has_many_zero_periods`.
#   - использовать эти флаги:
#     - для отбора данных (например, исключать экстремально нестабильные пары),
#     - как фичи (модели могут учитывать нестабильность),
#     - для дополнительного анализа на уровне бизнеса (по магазинам с “аномальной” динамикой).
#
# ---
#
# ## Итог: как DQC используется в ETL
#
# **DQC layer** в этом ноутбуке даёт **структурированный набор сигналов** для ETL:
#
# - **Что можно считать “чистым” по умолчанию**:
#   - полнота (нет NaN в ключевых полях),
#   - типы и форматы (Validity),
#   - целостность внешних ключей (Integrity),
#   - согласованность справочников и продаж (Consistency).
#
# - **Где нужны трансформации/решения в ETL**:
#   - обработка выбросов в `item_price` и `item_cnt_day`,
#   - явное разделение продаж и возвратов,
#   - особая обработка:
#     - новых товаров,
#     - новых пар `shop x item`,
#   - генерация временных рядов с заполнением пропусков нулями,
#   - маркировка нестабильных временных рядов (Poor Dynamic).
#
# - **Что использовать как фичи/флаги**:
#   - наличие/отсутствие истории по товару и паре,
#   - показатели нестабильности (резкие скачки/падения),
#   - информация о разреженности временных рядов.
