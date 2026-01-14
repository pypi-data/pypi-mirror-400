#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt

from scripts.utils_eda import (
    check_missing_values,
    print_numeric_stats,
    check_anomalies,
    check_id_uniqueness,
    check_datasets_overlap,
    create_histogram,
    create_boxplot,
    print_top_n,
)

import warnings

warnings.filterwarnings("ignore")


# In[2]:


# Путь к данным
data_path = "data/raw/"

# Загрузка всех CSV файлов
sales_train = pd.read_csv(data_path + "sales_train.csv")
test = pd.read_csv(data_path + "test.csv")
items = pd.read_csv(data_path + "items.csv")
shops = pd.read_csv(data_path + "shops.csv")
item_categories = pd.read_csv(data_path + "item_categories.csv")
sample_submission = pd.read_csv(data_path + "sample_submission.csv")


# In[3]:


def print_dataset_info(name, df):
    print(f"{name.upper()}")
    print(f"Размерность (shape): {df.shape}")
    print(f"\nСтолбцы: {list(df.columns)}")
    print("\nПервые 5 строк:")
    print(df.head())
    print("\nИнформация о данных:")
    df.info()


# ### sales_train.csv
# Основной файл с историческими продажами. Содержит:
# - `date` - дата продажи
# - `date_block_num` - номер месяца (0-33)
# - `shop_id` - идентификатор магазина
# - `item_id` - идентификатор товара
# - `item_price` - цена товара
# - `item_cnt_day` - количество проданных товаров за день

# In[4]:


# Временной анализ
sales_train["date"] = pd.to_datetime(sales_train["date"], format="%d.%m.%Y")
print(f"Минимальная дата: {sales_train['date'].min()}")
print(f"Максимальная дата: {sales_train['date'].max()}")
print(
    f"Количество дней: {(sales_train['date'].max() - sales_train['date'].min()).days}"
)
print(
    f"\nУникальные месяцы (date_block_num): {sorted(sales_train['date_block_num'].unique())}"
)
print(f"Количество месяцев: {sales_train['date_block_num'].nunique()}")
print(
    f"Диапазон date_block_num: {sales_train['date_block_num'].min()} - {sales_train['date_block_num'].max()}"
)

# Распределение транзакций по месяцам
transactions_per_month = sales_train.groupby("date_block_num").size()
print("\nКоличество транзакций по месяцам:")
print(transactions_per_month.head(10))
print(f"\nСреднее количество транзакций в месяц: {transactions_per_month.mean():.0f}")
print(f"Медианное количество транзакций в месяц: {transactions_per_month.median():.0f}")


# In[5]:


# Уникальные магазины и товары
print(f"Уникальных магазинов: {sales_train['shop_id'].nunique()}")
print(f"Уникальных товаров: {sales_train['item_id'].nunique()}")
print(
    f"Уникальных комбинаций shop_id + item_id: {sales_train.groupby(['shop_id', 'item_id']).size().shape[0]:,}"
)

# Топ магазинов по количеству транзакций
top_shops = sales_train["shop_id"].value_counts()
print_top_n(top_shops, n=10, name="Магазинов по количеству транзакций")

# Топ товаров по количеству транзакций
top_items = sales_train["item_id"].value_counts()
print_top_n(top_items, n=10, name="Товаров по количеству транзакций")


# In[ ]:


# Анализ распределения цен
print_numeric_stats(sales_train["item_price"], name="Цена (item_price)", decimals=2)

# Проверка на аномалии в ценах
check_anomalies(
    sales_train["item_price"], name="Цена", thresholds={"<= 0": 0, "> 100000": 100000}
)


# In[ ]:


# Анализ количества продаж
print_numeric_stats(
    sales_train["item_cnt_day"], name="Количество продаж (item_cnt_day)", decimals=2
)

# Проверка на возвраты и аномалии
_ = check_anomalies(
    sales_train["item_cnt_day"],
    name="Количество продаж",
    thresholds={"<= -1": -1, "== 0": 0, "> 1000": 1000},
)


# In[8]:


plt.style.use("seaborn-v0_8-darkgrid")
fig, ax = plt.subplots(2, 2, figsize=(15, 12))

price_data = sales_train[sales_train["item_price"] > 0]["item_price"]
price_data_clean = price_data[price_data <= price_data.quantile(0.95)]

# 1. Распределение цен
create_histogram(
    ax[0, 0],
    price_data_clean,
    bins=100,
    title="Распределение цен",
    xlabel="Цена (item price)",
    xlim=(0, sales_train["item_price"].quantile(0.99)),
)

# 2. Распределение цен (логарифмическая шкала)
create_histogram(
    ax[0, 1],
    price_data,
    bins=100,
    title="Распределение цен (логарифмическая шкала)",
    xlabel="log(Цена + 1)",
    log_scale=True,
)

# 3. Распределение количества продаж
create_histogram(
    ax[1, 0],
    sales_train["item_cnt_day"],
    bins=100,
    title="Распределение количества продаж",
    xlabel="Количество продаж (item cnt day)",
    xlim=(0, sales_train["item_cnt_day"].quantile(0.99)),
)

# 4. Boxplot для цен
create_boxplot(
    ax[1, 1],
    price_data_clean,
    title="Boxplot цен (99% перцентиль)",
    ylabel="Цена",
    show_fliers=False,
)

plt.tight_layout()
plt.show()


# ## Итоговый анализ sales_train.csv
#
# ### Основные характеристики данных
#
# **Временной период:**
# - Данные охватывают 34 месяца (date_block_num: 0–33)
# - Период: с января 2013 по октябрь 2015 года
# - Этого достаточно для анализа трендов и сезонности
#
# **Масштаб данных:**
# - ~2.9 млн транзакций
# - 60 уникальных магазинов
# - 21,807 уникальных товаров
# - Очень разреженная матрица: большинство пар `shop_id × item_id` никогда не встречались
#
# ### Критические проблемы и аномалии
#
# #### 1. **Экстремальные выбросы в ценах**
# - **Одна запись с ценой -1** (явная ошибка данных)
# - **Одна запись с ценой 307,980** (экстремальный выброс, в 300+ раз больше медианы)
# - Медианная цена: 399, средняя: 890.85
# - Стандартное отклонение: 1,729.80 (очень высокое, указывает на сильную вариативность)
# - **99% перцентиль: 5,999** - это означает, что 1% цен выше этого значения
#
# **Вывод:** Распределение цен сильно скошено вправо с экстремальными выбросами. Необходимо решить, как обрабатывать эти выбросы в ETL.
#
# #### 2. **Экстремальные выбросы в количестве продаж**
# - **Максимальное значение: 2,169** (при медиане 1.0!)
# - **Минимальное значение: -22** (возврат товара)
# - **Одна запись с количеством > 1,000**
# - 99% перцентиль: всего 5, но есть единичные экстремальные значения
#
# **Вывод:** Большинство продаж - это 1-2 единицы товара, но есть редкие массовые продажи и возвраты. Необходимо определить стратегию обработки.
#
# #### 3. **Отрицательные значения (возвраты)**
# - **7,356 записей (0.25%)** с отрицательным количеством
# - Это возвраты товаров, что является нормальной бизнес-практикой
# - **Вопрос:** Как учитывать возвраты?
#
# ### Потенциальные проблемы
#
# #### 4. **Сильная асимметрия распределений**
# - **Цены:** Распределение сильно скошено вправо (длинный правый хвост)
# - **Количество продаж:** Также скошено вправо, но большинство значений = 1
# - Логарифмическая шкала для цен показывает более нормальное распределение
#
# #### 5. **Разреженность данных**
# - Огромное количество возможных комбинаций shop_id × item_id
# - Большинство комбинаций отсутствуют в данных
# - Это создаст проблемы при создании признаков для моделирования
#
# #### 6. **Неравномерное распределение транзакций**
# - Топ-10 магазинов составляют значительную долю всех транзакций
# - Топ-10 товаров также имеют очень высокую частоту продаж
# - Может указывать на доминирование определенных магазинов/товаров
#
# #### Наблюдения и особенности
#
# #### 7. **Временная структура**
# - 34 месяца данных - достаточно для анализа сезонности
# - Необходимо проверить непрерывность временных рядов
# - Возможны пропуски в данных для некоторых магазинов/товаров
#
# #### 8. **Статистика по квантилям**
# - **Цены:** 25% перцентиль = 249, медиана = 399, 75% = 999
# - **Количество:** 25%, 50%, 75% перцентили все равны 1.0!
# - Это указывает на то, что большинство транзакций - это продажа 1 единицы товара
#
# ### Выводы
#
# Данные sales_train.csv содержат богатую информацию о продажах за 34 месяца, но требуют тщательной обработки из-за:
# - Экстремальных выбросов в ценах и количестве
# - Сильной асимметрии распределений
# - Разреженности данных
# - Наличия возвратов (отрицательных значений)

# In[9]:


print_dataset_info("TEST", test)


# In[ ]:


# Проверка уникальности ID в test
_ = check_id_uniqueness(test, "ID", name="test")
_ = check_id_uniqueness(test, "shop_id", name="test")
_ = check_id_uniqueness(test, "item_id", name="test")

# Уникальные магазины в тесте
unique_shops_test = test["shop_id"].nunique()
print(f"\nУникальных магазинов в test: {unique_shops_test}")

# Уникальные товары в тесте
unique_items_test = test["item_id"].nunique()
print(f"Уникальных товаров в test: {unique_items_test}")

unique_combinations = test.groupby(["shop_id", "item_id"]).size().shape[0]
print(f"Уникальных комбинаций shop_id x item_id: {unique_combinations:,}")

# Проверка соответствия магазинов между train и test
shops_overlap_result = check_datasets_overlap(
    sales_train, "shop_id", test, "shop_id", name1="sales_train", name2="test"
)
shops_in_train = shops_overlap_result["ids1"]
shops_in_test = shops_overlap_result["ids2"]
shops_only_in_test = shops_overlap_result["only_in_2"]

# Проверка соответствия товаров между train и test
items_overlap_result = check_datasets_overlap(
    sales_train, "item_id", test, "item_id", name1="sales_train", name2="test"
)
items_in_train = items_overlap_result["ids1"]
items_in_test = items_overlap_result["ids2"]
items_only_in_test = items_overlap_result["only_in_2"]


# In[11]:


train_combinations = set(
    sales_train.groupby(["shop_id", "item_id"]).size().index.tolist()
)

test_combinations = set(test[["shop_id", "item_id"]].apply(tuple, axis=1).tolist())

print(f"Комбинаций в train: {len(train_combinations):,}")
print(f"Комбинаций в test: {len(test_combinations):,}")

new_combinations = test_combinations - train_combinations
print(f"\nНовых комбинаций (не было в train): {len(new_combinations):,}")
print(
    f"Процент новых комбинаций: {len(new_combinations) / len(test_combinations) * 100:.2f}%"
)

existing_combinations = test_combinations & train_combinations
print(f"\nСуществующих комбинаций (были в train): {len(existing_combinations):,}")
print(
    f"Процент существующих: {len(existing_combinations) / len(test_combinations) * 100:.2f}%"
)


# In[12]:


fig, ax = plt.subplots(1, 2, figsize=(14, 5))

# 1. Соответствие магазинов
shops_overlap = len(shops_in_test & shops_in_train)
shops_only_test = len(shops_only_in_test)
shops_only_train = len(shops_in_train - shops_in_test)

ax[0].bar(
    ["В train и test", "Только в test", "Только в train"],
    [shops_overlap, shops_only_test, shops_only_train],
    color=["green", "red", "blue"],
    alpha=0.7,
)
ax[0].set_title("Соответствие магазинов между train и test")
ax[0].set_ylabel("Количество магазинов")
ax[0].grid(True, alpha=0.3)

for i, v in enumerate([shops_overlap, shops_only_test, shops_only_train]):
    ax[0].text(i, v + 0.5, str(v), ha="center", va="bottom")

# 2. Соответствие товаров
items_overlap = len(items_in_test & items_in_train)
items_only_test = len(items_only_in_test)
items_only_train = len(items_in_train - items_in_test)

ax[1].bar(
    ["В train и test", "Только в test", "Только в train"],
    [items_overlap, items_only_test, items_only_train],
    color=["green", "red", "blue"],
    alpha=0.7,
)
ax[1].set_title("Соответствие товаров между train и test")
ax[1].set_ylabel("Количество товаров")
ax[1].grid(True, alpha=0.3)

for i, v in enumerate([items_overlap, items_only_test, items_only_train]):
    ax[1].text(i, v + 100, f"{v:,}", ha="center", va="bottom")

plt.tight_layout()
plt.show()


# ## Итоговый анализ test.csv
#
# ### Структура и масштаб
#
# - `test.csv` содержит **214,200 строк** и **3 столбца**: `ID`, `shop_id`, `item_id`.
# - Это **список комбинаций магазин–товар**, для которых нужно предсказать `item_cnt_month` (через `sample_submission.csv`).
# - Нет ни дат, ни цен, ни количества — только идентификаторы. Вся информация о поведении берётся из `sales_train.csv` и справочников (`items`, `shops`, `item_categories`).
#
# ### Уникальные значения
#
# - Уникальных магазинов в test: **42** (в train: 60)
# - Уникальных товаров в test: **5,100** (в train: 21,807)
# - Уникальных комбинаций `shop_id x item_id` в test: **214,200** (каждый ID — уникальная пара)
#
# **Вывод:** тест покрывает не все магазины и не все товары.
#
# ### Соответствие с train
#
# **Магазины (`shop_id`):**
# - Все 42 магазина из test присутствуют в train.
# - В train есть **18 магазинов**, которых нет в test.
#
# **Товары (`item_id`):**
# - В train: **21,807** товаров.
# - В test: **5,100** товаров.
# - Товаров, которые есть в test, но **ни разу не встречались в train**: **363**.
#
# **Проблема:** для этих 363 товаров у модели **нет исторических данных**. Придётся смотреть на информацию о категории, среднем поведении похожих товаров, магазина и т.п.
#
# ### Комбинации shop_id x item_id
#
# - Комбинаций в train: **424,124**.
# - Комбинаций в test: **214,200**.
# - **Новых комбинаций** (есть в test, но не было в train): **102,796** (~**48%**).
# - **Существующих комбинаций** (были в train): **111,404** (~**52%**).
#
# **Ключевое наблюдение:**
# - Около **половины** тестовых пар магазин–товар **никогда не встречались в истории продаж**.
# - Для них нет прямого таргета в train — модель будет опираться только на агрегаты по магазину/товару/категории и на общие паттерны.
# - Для второй половины (52%) есть исторические данные, и прогноз по ним будет более надёжным.
#
# ### Риски и узкие места
#
# 1. **Новые товары (363 item_id):**
#    - Нет истории продаж → высокая неопределённость.
#    - Нужно использовать информацию о категориях (`item_category_id`) и статистики по похожим товарам.
#
# 2. **Новые комбинации shop×item (~48%):**
#    - Даже если товар и магазин по отдельности были в train, конкретная пара могла ни разу не продаваться.
#    - Нужны агрегированные признаки по магазину и по товару (средние продажи, сезонность и т.д.).
#
# **Итого:** `test.csv` — примерно половина комбинаций не имеет прямых исторических аналогов в `sales_train.csv`.

# In[13]:


print_dataset_info("items", items)


# In[ ]:


_ = check_missing_values(items, name="items")


# In[ ]:


# Проверка уникальности ID в items
_ = check_id_uniqueness(items, "item_id", name="items")

total_items = len(items)
print(f"Всего записей в справочнике: {total_items:,}")

unique_categories = items["item_category_id"].nunique()
print(f"\nУникальных категорий: {unique_categories}")

avg_items_per_category = total_items / unique_categories
print(f"Среднее количество товаров на категорию: {avg_items_per_category:.1f}")


# In[16]:


items_per_category = items["item_category_id"].value_counts().sort_index()
print_numeric_stats(
    items_per_category, name="Количество товаров в категории", decimals=1
)


# In[17]:


Q1 = items_per_category.quantile(0.25)
Q3 = items_per_category.quantile(0.75)
IQR = Q3 - Q1

outlier_threshold = Q3 + 1.5 * IQR
outlier_categories = items_per_category[items_per_category > outlier_threshold]
if len(outlier_categories) > 0:
    print(
        f"Категории с аномально большим количеством товаров (> {outlier_threshold:.0f}):"
    )
    for cat_id, count in outlier_categories.items():
        print(f"Категория {cat_id}: {count:,} товаров")
else:
    print("Нет категорий с аномально большим количеством товаров")


# In[18]:


# Проверка соответствия товаров между items и sales_train
check_datasets_overlap(
    items,
    "item_id",
    sales_train,
    "item_id",
    name1="items (справочник)",
    name2="sales_train (продажи)",
    return_sets=False,
)


# In[19]:


fig, ax = plt.subplots(2, 2, figsize=(16, 12))

# 1. Гистограмма распределения количества товаров по категориям
create_histogram(
    ax[0, 0],
    items_per_category,
    bins=30,
    title="Распределение количества товаров по категориям",
    xlabel="Количество товаров в категории",
    ylabel="Количество категорий",
    show_mean=True,
    show_median=True,
)

# 2. Топ-20 категорий по количеству товаров (столбчатая диаграмма)
top_categories = items_per_category.nlargest(20)

ax[0, 1].bar(range(len(top_categories)), top_categories.values, align="center")
ax[0, 1].set_xticks(range(len(top_categories)))
ax[0, 1].set_xticklabels(top_categories.index)
ax[0, 1].set_ylabel("Количество товаров")
ax[0, 1].set_xlabel("ID категории")
ax[0, 1].set_title("Топ-20 категорий по количеству товаров")
ax[0, 1].grid(True, alpha=0.3, axis="y")

# 3. Boxplot распределения
create_boxplot(
    ax[1, 0],
    items_per_category,
    title="Boxplot распределения товаров по категориям",
    ylabel="Количество товаров в категории",
    show_fliers=False,
)

# 4. Круговая диаграмма для топ-10 категорий
top_10 = items_per_category.nlargest(10)

other_count = items_per_category.tail(len(items_per_category) - 10).sum()
plot_data = list(top_10.values) + [other_count]
plot_labels = [f"Кат. {cat_id}" for cat_id in top_10.index] + ["Остальные"]

ax[1, 1].pie(plot_data, labels=plot_labels, autopct="%1.1f%%", startangle=90)
ax[1, 1].set_title("Распределение товаров: Топ-10 категорий vs Остальные")

plt.tight_layout()
plt.show()


# ## Итоговый анализ items.csv
#
# ### Основные характеристики
#
# **Структура справочника:**
# - **22,170 товаров** в справочнике
# - **3 столбца**: `item_id` (уникальный идентификатор), `item_name` (название), `item_category_id` (категория)
# - Все `item_id` уникальны — дубликатов нет
# - Пропущенных значений нет — все товары имеют названия и категории
#
# **Категоризация:**
# - **84 уникальные категории** (item_category_id)
# - Среднее количество товаров на категорию: ~**264 товара**
# - Распределение по категориям **неравномерное** — есть категории с очень большим и очень малым количеством товаров
#
# ### Распределение по категориям
#
# **Статистика распределения:**
# - Минимум товаров в категории: 1
# - Максимум товаров в категории: 5035
# - Медианное количество: 43.5
# - Стандартное отклонение: 642.8
#
# **Ключевые наблюдения:**
# - **Топ-10 категорий** содержат значительную долю всех товаров
# - Есть категории с **аномально большим** количеством товаров
# - Есть категории с **очень малым** количеством товаров
#
# **Вывод:** Категории сильно различаются по размеру. При создании признаков — категории с малым количеством товаров могут иметь менее надёжные статистики.
#
# ### Связь с продажами (sales_train.csv)
#
# **Согласованность данных:**
# - **Все товары из продаж есть в справочнике** (0 товаров в продажах, но отсутствующих в items.csv)
# - **Полная согласованность** - нет проблем с отсутствующими товарами
#
# **Товары без продаж:**
# - **363 товара** (1.64%) есть в справочнике, но **никогда не продавались**
# - Это может быть нормально:
#   - Новые товары, не продаются и тд..
#
# **Вывод:** Небольшой процент товаров без продаж — это нормально и не является проблемой качества данных.
#
# ### Потенциальные проблемы
#
# **1. Неравномерное распределение по категориям:**
# - Категории сильно различаются по размеру
# - Категории с малым количеством товаров могут иметь ненадёжные статистики
#
# **2. Возможные выбросы в категориях:**
# - Если есть категории с аномально большим количеством товаров, возможно, их стоит разбить на подкатегории
#
# **3. Названия товаров:**
# - Длина названий может сильно варьироваться
# - Возможны дубликаты названий (разные товары с одинаковыми названиями)
#
# ### Выводы
#
# `items.csv` — **качественный справочник товаров** с хорошей согласованностью с данными продаж:
# - Нет проблем с пропусками в продажах
# - Все товары имеют категории и названия
# - Неравномерное распределение по категориям требует внимания при создании признаков
# - Небольшой процент товаров без продаж
#

# In[20]:


print_dataset_info("item_categories", item_categories)


# In[ ]:


# Проверка уникальности ID и названий в item_categories
_ = check_id_uniqueness(item_categories, "item_category_id", name="item_categories")

unique_names = item_categories["item_category_name"].nunique()
total_categories = len(item_categories)
print(f"Уникальных названий: {unique_names}")
if unique_names == total_categories:
    print("Все названия категорий уникальны")
else:
    print(f"Есть дубликаты названий: {total_categories - unique_names} дубликатов")

categories_analysis = item_categories.copy()

separators = {
    " - ": "Дефис с пробелами",
    "-": "Дефис без пробелов",
    "/": "Слэш (возможная подкатегория)",
    " -": "Дефис с пробелом слева",
    "- ": "Дефис с пробелом справа",
}

for sep, description in separators.items():
    count = (
        categories_analysis["item_category_name"]
        .str.contains(sep, regex=False, na=False)
        .sum()
    )
    if count > 0:
        print(
            f"'{sep}': {count} категорий ({count / len(categories_analysis) * 100:.1f}%) - {description}"
        )

categories_analysis["main_category"] = (
    categories_analysis["item_category_name"].str.split(" - ").str[0]
)
categories_analysis["sub_category"] = (
    categories_analysis["item_category_name"].str.split(" - ").str[1:].str.join(" - ")
)

print(
    f"\nУникальных основных категорий: {categories_analysis['main_category'].nunique()}"
)
print(
    f"Уникальных субкатегорий категорий: {categories_analysis['sub_category'].nunique()}"
)


# In[22]:


main_cat_counts = categories_analysis["main_category"].value_counts()
print("\nТоп-5 основных категорий:")
print(main_cat_counts.head(5))


# ## Итоговый анализ item_categories.csv
#
# ### Основные характеристики
#
# **Структура справочника:**
# - **84 категории** товаров
# - **2 столбца**: `item_category_id` (уникальный идентификатор), `item_category_name` (название)
# - Все ID и названия уникальны — дубликатов нет
# - Пропущенных значений нет
#
# ### Иерархия категорий
#
# **Структура названий:**
# - **91.7% категорий** (77 из 84) имеют структуру с разделителем " - "
# - Это указывает на **двухуровневую иерархию**: "Основная категория - Подкатегория"
#
# **Уровни иерархии:**
# - **20 основных категорий** (первый уровень)
# - **61 подкатегория** (второй уровень, после разделителя " - ")
# - **7 категорий** без явной подкатегории (без разделителя)
#
# **Примеры основных категорий:**
# - "Аксессуары" — подкатегории: PS2, PS3, PS4, PSP, PSVita, XBOX 360, XBOX ONE
# - "Игровые консоли" — подкатегории: PS2, PS3, PS4, PSP, PSVita, XBOX 360, XBOX ONE, Прочие
# - "Игры" — подкатегории: PS2, PS3, PS4, PSP, PSVita, XBOX 360, XBOX ONE, Аксессуары для игр
# - "Игры PC" — подкатегории: Дополнительные издания, Коллекционные издания, Стандартные издания
# - И другие
#
# **Вывод:** Категории имеют чёткую иерархическую структуру, что можно использовать для создания признаков (основная категория и подкатегория).
#
# ### Наблюдения
#
# **Паттерны в названиях:**
# - Много категорий связаны с игровыми платформами (PS2, PS3, PS4, PSP, PSVita, XBOX 360, XBOX ONE)
# - Есть категории для цифровых товаров ("Цифра" в названии)
# - Есть категории для физических товаров (консоли, аксессуары)
# - Есть служебные категории ("Доставка товара", "Билеты")
#
# **Распределение:**
# - Основные категории сильно различаются по количеству подкатегорий
# - Некоторые основные категории имеют много подкатегорий (например, "Игры", "Аксессуары")
#
# ### Связь с другими данными
#
# **С items.csv:**
# - Все категории из items.csv должны присутствовать в item_categories.csv
# - Это будет проверено в DQC
#
# ### Выводы
#
# `item_categories.csv` — **структурированный справочник** с явной иерархией:
# - Двухуровневая структура (основная категория - подкатегория)
# - Все категории имеют уникальные ID и названия
# - Нет пропущенных значений
# - Иерархия может быть полезна для создания признаков
#

# In[23]:


print_dataset_info("shops", shops)


# In[ ]:


# Проверка уникальности ID в shops
_ = check_id_uniqueness(shops, "shop_id", name="shops")

shops_analysis = shops.copy()
shops_analysis["name_length"] = shops_analysis["shop_name"].str.len()
shops_analysis["city"] = shops_analysis["shop_name"].str.split().str[0].str.strip('!,"')

print(f"\nСредняя длина: {shops_analysis['name_length'].mean():.1f} символов")
print(f"Медианная длина: {shops_analysis['name_length'].median():.1f} символов")
print(f"Минимальная длина: {shops_analysis['name_length'].min()} символов")
print(f"Максимальная длина: {shops_analysis['name_length'].max()} символов")


# In[25]:


city_counts = shops_analysis["city"].value_counts()

print(f"Уникальных городов (приблизительно): {len(city_counts)}")
print_top_n(city_counts, n=10, name="городов по количеству магазинов")


# In[26]:


keywords = {
    "ТЦ": "Торговый центр",
    "ТРЦ": "Торгово-развлекательный центр",
    "ТРК": "Торгово-развлекательный комплекс",
    "ТК": "Торговый комплекс",
    "МТРЦ": "Многофункциональный торгово-развлекательный центр",
    "Интернет": "Интернет-магазин",
    "Выездная": "Выездная торговля",
    "фран": "Франшиза",
}

for keyword, description in keywords.items():
    count = (
        shops_analysis["shop_name"].str.contains(keyword, case=False, na=False).sum()
    )
    if count > 0:
        print(f"'{keyword}' ({description}): {count} магазин(ов)")


# In[27]:


# Визуализация анализа shops.csv
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

# 1. Распределение длины названий
create_histogram(
    axes[0, 0],
    shops_analysis["name_length"],
    bins=15,
    title="Распределение длины названий магазинов",
    xlabel="Длина названия (символов)",
    ylabel="Количество магазинов",
    show_mean=True,
)

# 2. Топ-10 городов по количеству магазинов
top_cities = city_counts.head(10)
axes[0, 1].barh(range(len(top_cities)), top_cities.values, alpha=0.7)
axes[0, 1].set_yticks(range(len(top_cities)))
axes[0, 1].set_yticklabels(top_cities.index)
axes[0, 1].set_xlabel("Количество магазинов")
axes[0, 1].set_title("Топ-10 городов по количеству магазинов")
axes[0, 1].grid(True, alpha=0.3, axis="x")
axes[0, 1].invert_yaxis()

# 3. Распределение по типам магазинов
type_counts = {}
for keyword, description in keywords.items():
    count = (
        shops_analysis["shop_name"].str.contains(keyword, case=False, na=False).sum()
    )
    if count > 0:
        type_counts[description] = count

if type_counts:
    axes[1, 0].bar(
        range(len(type_counts)), list(type_counts.values()), color="purple", alpha=0.7
    )
    axes[1, 0].set_xticks(range(len(type_counts)))
    axes[1, 0].set_xticklabels(list(type_counts.keys()), rotation=45, ha="right")
    axes[1, 0].set_ylabel("Количество магазинов")
    axes[1, 0].set_title("Распределение по типам магазинов")
    axes[1, 0].grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.show()


# ## Итоговый анализ shops.csv
#
# ### Основные характеристики
#
# **Структура справочника:**
# - **60 магазинов** в справочнике
# - **2 столбца**: `shop_id` (уникальный идентификатор), `shop_name` (название)
# - Все ID уникальны — дубликатов нет
# - Пропущенных значений нет
#
# ### Географическое распределение
#
# **Города:**
# - Магазины расположены в разных городах России
# - Названия магазинов обычно начинаются с названия города
# - Москва имеет наибольшее количество магазинов
# - Есть магазины в крупных городах (Казань, Красноярск, Воронеж и др.)
#
# **Типы магазинов:**
# - **Торговые центры (ТЦ)** — большинство магазинов
# - **Торгово-развлекательные центры (ТРЦ, ТРК, МТРЦ)**
# - **Торговые комплексы (ТК)**
# - **Интернет-магазины** — есть онлайн-магазины
# - **Выездная торговля**
# - **Франшизы** — некоторые магазины являются франшизами
#
# ### Особенности названий
#
# **Паттерны:**
# - Названия содержат географическую информацию (город)
# - Названия содержат тип торговой точки (ТЦ, ТРЦ и т.д.)
# - Некоторые названия содержат дополнительную информацию (адрес, павильон)
# - Есть специальные символы в начале некоторых названий ("!")
#
# **Длина названий:**
# - Названия различаются по длине
# - Средняя длина: 23.6 символов
# - Медианная длина: 22.0 символов
#
# ### Потенциал для feature engineering
#
# **Географические признаки:**
# - Можно создать признаки на основе города
# - Можно группировать города по регионам
# - Можно выделить столичные vs региональные магазины
#
# **Типы магазинов:**
# - Можно создать признаки типа магазина (ТЦ, ТРЦ, интернет и т.д.)
# - Можно выделить онлайн vs офлайн магазины
# - Можно выделить франшизы vs собственные магазины
#
# ### Выводы
#
# `shops.csv` — **структурированный справочник** с богатой информацией:
# - Все магазины имеют уникальные ID и названия
# - Названия содержат полезную информацию (город, тип)
# - Географическая информация и типы магазинов могут быть полезны для создания признаков

# In[28]:


print_dataset_info("sample_submission", sample_submission)


# In[ ]:


# Проверка уникальности ID в sample_submission
_ = check_id_uniqueness(sample_submission, "ID", name="sample_submission")

unique_values = sample_submission["item_cnt_month"].unique()
print(f"\nКоличество уникальных значений: {len(unique_values)}")
print(f"Уникальные значения: {unique_values}")


# In[30]:


if "test" in globals():
    print(f"Строк в test.csv: {test.shape[0]:,}")
    print(f"Строк в sample_submission.csv: {sample_submission.shape[0]:,}")

    if test.shape[0] == sample_submission.shape[0]:
        print("Количество строк совпадает")
    else:
        print("Количество строк не совпадает!")

    # Проверка ID
    test_ids = set(test["ID"].unique())
    submission_ids = set(sample_submission["ID"].unique())

    if test_ids == submission_ids:
        print("Все ID из test.csv присутствуют в sample_submission.csv")
    else:
        missing_in_submission = test_ids - submission_ids
        missing_in_test = submission_ids - test_ids
        if missing_in_submission:
            print(f"ID в test, но нет в submission: {len(missing_in_submission)}")
        if missing_in_test:
            print(f"ID в submission, но нет в test: {len(missing_in_test)}")
else:
    print("test.csv не загружен")


# ## Итоговый анализ sample_submission.csv
#
# ### Основные характеристики
#
# **Структура файла:**
# - **214,200 строк** (совпадает с test.csv)
# - **2 столбца**: `ID` (идентификатор записи), `item_cnt_month` (предсказанное количество продаж за месяц)
# - Все ID уникальны и соответствуют test.csv
# - Пропущенных значений нет
#
# ### Формат предсказаний
#
# **Значения item_cnt_month:**
# - Все предсказания равны **0.5** (baseline)
#
# ### Соответствие с test.csv
#
# **Структурное соответствие:**
# - Количество строк совпадает с test.csv (214,200)
# - Все ID из test.csv присутствуют в sample_submission.csv
# - Порядок ID соответствует test.csv
#
# **Формат:**
# - Каждая строка в sample_submission.csv соответствует строке в test.csv
# - ID связывает предсказание с конкретной комбинацией shop_id x item_id из test.csv
#
# ### Выводы
#
# `sample_submission.csv` — **шаблон файла для отправки результатов**:
# - Правильный формат и структура
# - Полное соответствие с test.csv
# - Все значения 0.5 — это просто placeholder
# - В ETL нужно будет создать аналогичный файл с реальными предсказаниями модели
