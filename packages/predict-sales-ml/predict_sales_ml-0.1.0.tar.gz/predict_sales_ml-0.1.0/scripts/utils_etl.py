import pandas as pd
import numpy as np
from pathlib import Path


def clean_sales_train(sales_train: pd.DataFrame) -> pd.DataFrame:
    """
    Очистка данных sales_train согласно плану.

    Обработка выбросов (удаление):
    - Удалить записи с item_price <= 0 (1 запись с -1)
    - Удалить записи с item_price > 100_000 (1 запись с 307980)
    - Удалить записи с item_cnt_day > 1000 (1 запись)

    Обработка возвратов:
    - Создать флаг is_return (True если item_cnt_day < 0)
    - Создать столбец item_cnt_day_abs (абсолютное значение)
    - Включить возвраты в агрегацию (суммировать с продажами)

    Args:
        sales_train: Исходный датафрейм sales_train

    Returns:
        Очищенный sales_train_clean с дополнительными столбцами is_return, item_cnt_day_abs
    """

    sales_train_clean = sales_train.copy()
    sales_train_clean = sales_train_clean[
        (sales_train_clean["item_price"] > 0)
        & (sales_train_clean["item_price"] < 100_000)
        & (sales_train_clean["item_cnt_day"] < 1000)
    ]

    sales_train_clean["is_return"] = sales_train_clean["item_cnt_day"] < 0
    sales_train_clean["item_cnt_day_abs"] = sales_train_clean["item_cnt_day"].abs()

    return sales_train_clean


def aggregate_to_monthly(sales_train_clean: pd.DataFrame) -> pd.DataFrame:
    """
    Агрегация данных до месячного уровня.

    Группировка по shop_id, item_id, date_block_num.
    Вычисляет агрегаты для предсказания item_cnt_month и создания фичей.

    Args:
        sales_train_clean: Очищенный датафрейм sales_train с колонками is_return и item_cnt_day_abs

    Returns:
        sales_monthly DataFrame с агрегированными данными по месяцам
    """
    grouped = sales_train_clean.groupby(["shop_id", "item_id", "date_block_num"])
    sales_monthly = pd.DataFrame(
        {
            # Основной таргет
            "item_cnt_month": grouped["item_cnt_day_abs"].sum(),
            # Статистики по ценам
            "item_price_mean": grouped["item_price"].mean(),
            "item_price_median": grouped["item_price"].median(),
            "item_price_min": grouped["item_price"].min(),
            "item_price_max": grouped["item_price"].max(),
            # Количество транзакций
            "transactions_count": grouped.size(),
            # Статистики по возвратам
            "returns_count": grouped["is_return"].sum(),
            "returns_sum": grouped["item_cnt_day"].apply(
                lambda x: x[x < 0].sum() if (x < 0).any() else 0
            ),
        }
    )

    sales_monthly = sales_monthly.reset_index()
    return sales_monthly


def fill_sparse_timeseries(sales_monthly: pd.DataFrame) -> pd.DataFrame:
    """
    Обработка разреженных временных рядов.

    Для каждой пары shop_id x item_id, которая была активна хотя бы в одном месяце:
    - Создает полный временной ряд для месяцев 0-33
    - Заполняет пропущенные месяцы нулями (item_cnt_month = 0)
    - Для цен: заполняет пропуски медианной ценой по паре

    Args:
        sales_monthly: Агрегированный датафрейм с колонками shop_id, item_id, date_block_num

    Returns:
        sales_monthly_filled с полными временными рядами для активных пар
    """
    # Находим все уникальные пары
    active_pairs = sales_monthly[["shop_id", "item_id"]].drop_duplicates()

    all_months = pd.DataFrame({"date_block_num": np.arange(34)})

    # Декартово произведение: каждая пара x каждый месяц
    full_index = active_pairs.merge(all_months, how="cross")

    sales_monthly_filled = full_index.merge(
        sales_monthly, on=["shop_id", "item_id", "date_block_num"], how="left"
    )

    # Вычисляем медианные цены по каждой паре (shop_id, item_id) для заполнения пропусков
    price_medians = (
        sales_monthly.groupby(["shop_id", "item_id"])[
            ["item_price_mean", "item_price_median", "item_price_min", "item_price_max"]
        ]
        .median()
        .reset_index()
    )

    # Заполняем пропуски в количестве продаж нулями
    sales_monthly_filled["item_cnt_month"] = sales_monthly_filled[
        "item_cnt_month"
    ].fillna(0)

    # Заполняем пропуски в ценах медианными значениями по паре
    for price_col in [
        "item_price_mean",
        "item_price_median",
        "item_price_min",
        "item_price_max",
    ]:
        sales_monthly_filled = sales_monthly_filled.merge(
            price_medians[["shop_id", "item_id", price_col]],
            on=["shop_id", "item_id"],
            how="left",
            suffixes=("", "_median"),
        )

        sales_monthly_filled[price_col] = sales_monthly_filled[price_col].fillna(
            sales_monthly_filled[f"{price_col}_median"]
        )

        sales_monthly_filled = sales_monthly_filled.drop(
            columns=[f"{price_col}_median"]
        )

    # Заполняем пропуски в остальных полях нулями
    for col in ["transactions_count", "returns_count", "returns_sum"]:
        sales_monthly_filled[col] = sales_monthly_filled[col].fillna(0)

    sales_monthly_filled = sales_monthly_filled.sort_values(
        ["shop_id", "item_id", "date_block_num"]
    ).reset_index(drop=True)

    return sales_monthly_filled


def enrich_categories(item_categories: pd.DataFrame) -> pd.DataFrame:
    """
    Обогащение справочника item_categories.

    Извлекает main_category (до " - ") и sub_category (после " - ").

    Args:
        item_categories: Справочник категорий (item_category_id, item_category_name)

    Returns:
        item_categories_enriched с дополнительными колонками
    """
    item_categories_enriched = item_categories.copy()

    # Извлекаем основную категорию (до " - ")
    item_categories_enriched["main_category"] = (
        item_categories_enriched["item_category_name"].str.split(" - ").str[0]
    )

    # Извлекаем подкатегорию (после " - ")
    item_categories_enriched["sub_category"] = (
        item_categories_enriched["item_category_name"]
        .str.split(" - ")
        .str[1:]
        .str.join(" - ")
    )

    item_categories_enriched["sub_category"] = (
        item_categories_enriched["sub_category"]
        .replace("", np.nan)
        .fillna(item_categories_enriched["main_category"])
    )

    item_categories_enriched["is_digital"] = item_categories_enriched[
        "main_category"
    ].str.contains("Цифра", na=False) | item_categories_enriched[
        "sub_category"
    ].str.contains("Цифра", na=False)

    return item_categories_enriched


def enrich_items(
    items: pd.DataFrame,
    item_categories: pd.DataFrame,
    sales_train_clean: pd.DataFrame = None,
) -> pd.DataFrame:
    """
    Обогащение справочника items.

    Использует enrich_categories для извлечения main_category и sub_category.
    Добавляет флаг has_sales_history (есть ли товар в sales_train).

    Args:
        items: Справочник товаров (item_id, item_name, item_category_id)
        item_categories: Справочник категорий (item_category_id, item_category_name)
        sales_train_clean: Очищенные данные продаж (опционально, для флага has_sales_history)

    Returns:
        items_enriched с дополнительными колонками
    """
    items_enriched = items.copy()

    # Сначала обогащаем категории (переиспользуем функцию)
    item_categories_enriched = enrich_categories(item_categories)

    # Объединяем с обогащенными категориями для получения main_category и sub_category
    items_enriched = items_enriched.merge(
        item_categories_enriched[
            ["item_category_id", "main_category", "sub_category", "is_digital"]
        ],
        on="item_category_id",
        how="left",
    )

    # Добавляем флаг has_sales_history
    if sales_train_clean is not None:
        items_with_sales = set(sales_train_clean["item_id"].unique())
        items_enriched["has_sales_history"] = items_enriched["item_id"].isin(
            items_with_sales
        )
    else:
        items_enriched["has_sales_history"] = False

    return items_enriched


def enrich_shops(shops: pd.DataFrame) -> pd.DataFrame:
    """
    Обогащение справочника shops.

    Извлекает город из shop_name (первое слово, очистить от спецсимволов).
    Извлекает тип магазина (ТЦ, ТРЦ, Интернет и т.д.).
    Добавляет флаги is_online и is_franchise.

    Args:
        shops: Справочник магазинов (shop_id, shop_name)

    Returns:
        shops_enriched с дополнительными колонками
    """
    shops_enriched = shops.copy()

    # Извлекаем город (первое слово, очищаем от спецсимволов)
    shops_enriched["city"] = shops_enriched["shop_name"].str.split().str[0]
    shops_enriched["city"] = shops_enriched["city"].str.strip('!,"')

    non_city_tokens = ["Интернет-магазин", "Цифровой", "Выездная"]
    shops_enriched.loc[shops_enriched["city"].isin(non_city_tokens), "city"] = (
        "Неизвестно"
    )

    shops_enriched["city"] = shops_enriched["city"].fillna("Неизвестно")

    # Извлекаем тип магазина (ищем ключевые слова)
    shop_name_lower = shops_enriched["shop_name"].str.lower()

    def extract_shop_type(name: str) -> str:
        name_lower = name.lower()
        if "тц" in name_lower or "торговый центр" in name_lower:
            return "ТЦ"
        elif "трц" in name_lower or "торгово-развлекательный" in name_lower:
            return "ТРЦ"
        elif "трк" in name_lower:
            return "ТРК"
        elif "интернет" in name_lower or "онлайн" in name_lower:
            return "Интернет"
        else:
            return "Другое"

    shops_enriched["shop_type"] = shops_enriched["shop_name"].apply(extract_shop_type)

    # Флаг is_online (если содержит "интернет" или "онлайн")
    shops_enriched["is_online"] = shops_enriched["shop_name"].str.contains(
        "интернет|онлайн", case=False, na=False
    )

    # Флаг is_franchise (если содержит "фран")
    shops_enriched["is_franchise"] = shop_name_lower.str.contains(
        "фран", case=False, na=False
    )

    return shops_enriched


def join_with_references(
    sales_monthly_filled: pd.DataFrame,
    items_enriched: pd.DataFrame,
    shops_enriched: pd.DataFrame,
) -> pd.DataFrame:
    """
    Объединение sales_monthly_filled со справочниками.

    Выполняет джойны:
    - sales_monthly_filled → items_enriched (по item_id)
    - → shops_enriched (по shop_id)

    Примечание: item_categories_enriched уже включен в items_enriched через item_category_id.

    Args:
        sales_monthly_filled: Агрегированные данные продаж с полными временными рядами
        items_enriched: Обогащенный справочник товаров
        shops_enriched: Обогащенный справочник магазинов

    Returns:
        sales_monthly_enriched с полной информацией из всех справочников
    """
    sales_monthly_enriched = sales_monthly_filled.copy()

    items_cols_to_merge = [
        "item_id",
        "item_name",
        "item_category_id",
        "main_category",
        "sub_category",
        "is_digital",
        "has_sales_history",
    ]

    # Джойн с items_enriched (по item_id)
    sales_monthly_enriched = sales_monthly_enriched.merge(
        items_enriched[items_cols_to_merge], on="item_id", how="left"
    )

    # Джойн с shops_enriched (по shop_id)
    shops_cols_to_merge = [
        "shop_id",
        "shop_name",
        "city",
        "shop_type",
        "is_online",
        "is_franchise",
    ]

    sales_monthly_enriched = sales_monthly_enriched.merge(
        shops_enriched[shops_cols_to_merge], on="shop_id", how="left"
    )

    return sales_monthly_enriched


def create_basic_features(sales_monthly_enriched: pd.DataFrame) -> pd.DataFrame:
    """
    Создание базовых фичей для моделирования.

    Создает:
    - Временные фичи: month, year, is_holiday_season
    - Лаги: lag_1, lag_2, lag_3, lag_6, lag_12
    - Скользящие средние: mean_3m, mean_6m, mean_12m
    - Агрегаты по товару: item_total_sales, item_avg_price
    - Агрегаты по магазину: shop_total_sales
    - Агрегаты за все время: item_avg_sales_all_time, item_avg_price_all_time,
      shop_avg_sales_all_time, category_avg_sales_in_shop
    - Флаг: has_pair_history (всегда True для train)

    Args:
        sales_monthly_enriched: Обогащенные данные продаж со справочниками

    Returns:
        sales_monthly_with_features с дополнительными столбцами фичей
    """
    df = sales_monthly_enriched.copy()

    # Убеждаемся, что данные отсортированы для корректной работы shift() и rolling()
    df = df.sort_values(["shop_id", "item_id", "date_block_num"]).reset_index(drop=True)

    df["month"] = (df["date_block_num"] % 12 + 1).astype(int)
    df["year"] = (2013 + (df["date_block_num"] // 12)).astype(int)
    df["is_holiday_season"] = (df["month"] == 12) | (df["month"] == 1)

    # Лаги
    for lag in [1, 2, 3, 6, 12]:
        df[f"lag_{lag}"] = df.groupby(["shop_id", "item_id"])["item_cnt_month"].shift(
            lag
        )
        df[f"lag_{lag}"] = df[f"lag_{lag}"].fillna(0)

    # Скользящие средние
    for window in [3, 6, 12]:
        df[f"mean_{window}m"] = df.groupby(["shop_id", "item_id"])[
            "item_cnt_month"
        ].transform(lambda x: x.rolling(window=window, min_periods=1).mean())

    # Общие продажи товара за месяц (по всем магазинам)
    item_monthly = (
        df.groupby(["item_id", "date_block_num"])
        .agg({"item_cnt_month": "sum", "item_price_median": "mean"})
        .reset_index()
    )
    item_monthly.columns = [
        "item_id",
        "date_block_num",
        "item_total_sales",
        "item_avg_price",
    ]

    df = df.merge(item_monthly, on=["item_id", "date_block_num"], how="left")

    # Общие продажи магазина за месяц (по всем товарам)
    shop_monthly = (
        df.groupby(["shop_id", "date_block_num"])
        .agg(
            {
                "item_cnt_month": "sum",
            }
        )
        .reset_index()
    )
    shop_monthly.columns = ["shop_id", "date_block_num", "shop_total_sales"]

    df = df.merge(shop_monthly, on=["shop_id", "date_block_num"], how="left")

    # Агрегаты за все время (для совместимости с test)
    # Вычисляем агрегаты для каждого месяца, используя только данные до него (без leakage)
    item_aggregates_all_time = []
    shop_aggregates_all_time = []
    category_shop_aggregates_all_time = []

    for month in sorted(df["date_block_num"].unique()):
        month_mask = df["date_block_num"] == month
        # Данные до текущего месяца (без текущего)
        historical_mask = df["date_block_num"] < month

        if historical_mask.sum() > 0:
            # Агрегаты по товару (средние за все время до текущего месяца)
            item_agg = (
                df[historical_mask]
                .groupby("item_id")
                .agg({"item_cnt_month": "mean", "item_price_median": "mean"})
                .reset_index()
            )
            item_agg.columns = [
                "item_id",
                "item_avg_sales_all_time",
                "item_avg_price_all_time",
            ]
            item_agg["date_block_num"] = month
            item_aggregates_all_time.append(item_agg)

            # Агрегаты по магазину
            shop_agg = (
                df[historical_mask]
                .groupby("shop_id")
                .agg({"item_cnt_month": "mean"})
                .reset_index()
            )
            shop_agg.columns = ["shop_id", "shop_avg_sales_all_time"]
            shop_agg["date_block_num"] = month
            shop_aggregates_all_time.append(shop_agg)

            # Агрегаты по категории в магазине
            cat_shop_agg = (
                df[historical_mask]
                .groupby(["shop_id", "main_category"])
                .agg({"item_cnt_month": "mean"})
                .reset_index()
            )
            cat_shop_agg.columns = [
                "shop_id",
                "main_category",
                "category_avg_sales_in_shop",
            ]
            cat_shop_agg["date_block_num"] = month
            category_shop_aggregates_all_time.append(cat_shop_agg)
        else:
            # Для первого месяца (month=0) - создаем нулевые агрегаты для всех уникальных комбинаций
            month_data = df[month_mask][
                ["item_id", "shop_id", "main_category", "date_block_num"]
            ].drop_duplicates()

            # Item aggregates
            item_agg_zero = month_data[["item_id", "date_block_num"]].drop_duplicates()
            item_agg_zero["item_avg_sales_all_time"] = 0
            item_agg_zero["item_avg_price_all_time"] = 0
            item_aggregates_all_time.append(item_agg_zero)

            # Shop aggregates
            shop_agg_zero = month_data[["shop_id", "date_block_num"]].drop_duplicates()
            shop_agg_zero["shop_avg_sales_all_time"] = 0
            shop_aggregates_all_time.append(shop_agg_zero)

            # Category-shop aggregates
            cat_shop_agg_zero = month_data[
                ["shop_id", "main_category", "date_block_num"]
            ].drop_duplicates()
            cat_shop_agg_zero["category_avg_sales_in_shop"] = 0
            category_shop_aggregates_all_time.append(cat_shop_agg_zero)

    # Объединяем агрегаты
    if item_aggregates_all_time:
        item_agg_all = pd.concat(item_aggregates_all_time, ignore_index=True)
        df = df.merge(
            item_agg_all[
                [
                    "item_id",
                    "date_block_num",
                    "item_avg_sales_all_time",
                    "item_avg_price_all_time",
                ]
            ],
            on=["item_id", "date_block_num"],
            how="left",
        )
        df["item_avg_sales_all_time"] = df["item_avg_sales_all_time"].fillna(0)
        df["item_avg_price_all_time"] = df["item_avg_price_all_time"].fillna(0)

    if shop_aggregates_all_time:
        shop_agg_all = pd.concat(shop_aggregates_all_time, ignore_index=True)
        df = df.merge(
            shop_agg_all[["shop_id", "date_block_num", "shop_avg_sales_all_time"]],
            on=["shop_id", "date_block_num"],
            how="left",
        )
        df["shop_avg_sales_all_time"] = df["shop_avg_sales_all_time"].fillna(0)

    if category_shop_aggregates_all_time:
        cat_shop_agg_all = pd.concat(
            category_shop_aggregates_all_time, ignore_index=True
        )
        df = df.merge(
            cat_shop_agg_all[
                [
                    "shop_id",
                    "main_category",
                    "date_block_num",
                    "category_avg_sales_in_shop",
                ]
            ],
            on=["shop_id", "main_category", "date_block_num"],
            how="left",
        )
        df["category_avg_sales_in_shop"] = df["category_avg_sales_in_shop"].fillna(0)

    # Флаг has_pair_history (для совместимости с test)
    # Для train это всегда True, так как все пары из train имеют историю
    df["has_pair_history"] = True

    return df


def prepare_test_data(
    test: pd.DataFrame,
    sales_monthly_with_features: pd.DataFrame,
    items_enriched: pd.DataFrame,
    shops_enriched: pd.DataFrame,
) -> pd.DataFrame:
    """
    Подготовка тестовых данных для предсказания.

    Добавляет флаги для новых товаров/пар и статические фичи.

    Args:
        test: Тестовый датафрейм (ID, shop_id, item_id)
        sales_monthly_enriched: Обогащенные данные продаж (для проверки истории)
        items_enriched: Обогащенный справочник товаров
        shops_enriched: Обогащенный справочник магазинов

    Returns:
        test_enriched с флагами и базовыми фичами
    """
    test_enriched = test.copy()

    # Добавляем date_block_num = 34 для всех записей
    test_enriched["date_block_num"] = 34

    # Пары shop_id × item_id, которые были в sales_train
    pairs_in_train = set(
        sales_monthly_with_features[["shop_id", "item_id"]].apply(tuple, axis=1)
    )
    test_enriched["has_pair_history"] = (
        test_enriched[["shop_id", "item_id"]].apply(tuple, axis=1).isin(pairs_in_train)
    )

    # Джойн с items_enriched
    items_cols = [
        "item_id",
        "item_name",
        "item_category_id",
        "main_category",
        "sub_category",
        "is_digital",
        "has_sales_history",
    ]
    test_enriched = test_enriched.merge(
        items_enriched[items_cols], on="item_id", how="left"
    )

    # Джойн с shops_enriched
    shops_cols = [
        "shop_id",
        "shop_name",
        "city",
        "shop_type",
        "is_online",
        "is_franchise",
    ]
    test_enriched = test_enriched.merge(
        shops_enriched[shops_cols], on="shop_id", how="left"
    )

    # Создаем фичи для месяца 34
    # Берем данные месяца 33 для вычисления лагов
    month_33_data = sales_monthly_with_features[
        sales_monthly_with_features["date_block_num"] == 33
    ][
        [
            "shop_id",
            "item_id",
            "item_cnt_month",
            "lag_1",
            "lag_2",
            "lag_3",
            "lag_6",
            "lag_12",
        ]
    ].copy()

    # Для месяца 34:
    # lag_1 = item_cnt_month месяца 33
    month_33_data["lag_1"] = month_33_data["item_cnt_month"]

    # Пересчитываем скользящие средние для месяца 34
    for window in [3, 6, 12]:
        start_month = 34 - window
        window_data = sales_monthly_with_features[
            (sales_monthly_with_features["date_block_num"] >= start_month)
            & (sales_monthly_with_features["date_block_num"] <= 33)
        ]

        mean_col = f"mean_{window}m"
        window_means = (
            window_data.groupby(["shop_id", "item_id"])["item_cnt_month"]
            .mean()
            .reset_index()
        )
        window_means.columns = ["shop_id", "item_id", mean_col]

        month_33_data = month_33_data.merge(
            window_means, on=["shop_id", "item_id"], how="left"
        )

    # Мержим с test
    test_enriched = test_enriched.merge(
        month_33_data[
            [
                "shop_id",
                "item_id",
                "lag_1",
                "lag_2",
                "lag_3",
                "lag_6",
                "lag_12",
                "mean_3m",
                "mean_6m",
                "mean_12m",
            ]
        ],
        on=["shop_id", "item_id"],
        how="left",
    )

    # Для новых пар заполняем нулями
    lag_cols = ["lag_1", "lag_2", "lag_3", "lag_6", "lag_12"]
    mean_cols = ["mean_3m", "mean_6m", "mean_12m"]
    test_enriched[lag_cols + mean_cols] = test_enriched[lag_cols + mean_cols].fillna(0)

    # Временные фичи для месяца 34
    test_enriched["month"] = 11
    test_enriched["year"] = 2015
    test_enriched["is_holiday_season"] = False

    # Берем данные месяца 33 и вычисляем агрегаты для месяца 34
    month_33_data = sales_monthly_with_features[
        sales_monthly_with_features["date_block_num"] == 33
    ]

    # item_total_sales - сумма продаж товара по всем магазинам за месяц 33
    item_monthly_33 = (
        month_33_data.groupby("item_id")
        .agg({"item_cnt_month": "sum", "item_price_median": "mean"})
        .reset_index()
    )
    item_monthly_33.columns = ["item_id", "item_total_sales", "item_avg_price"]

    test_enriched = test_enriched.merge(item_monthly_33, on="item_id", how="left")

    # shop_total_sales - сумма продаж магазина по всем товарам за месяц 33
    shop_monthly_33 = (
        month_33_data.groupby("shop_id").agg({"item_cnt_month": "sum"}).reset_index()
    )
    shop_monthly_33.columns = ["shop_id", "shop_total_sales"]

    test_enriched = test_enriched.merge(shop_monthly_33, on="shop_id", how="left")

    # Заполняем пропуски нулями (для новых товаров/магазинов)
    test_enriched["item_total_sales"] = test_enriched["item_total_sales"].fillna(0)
    test_enriched["item_avg_price"] = test_enriched["item_avg_price"].fillna(0)
    test_enriched["shop_total_sales"] = test_enriched["shop_total_sales"].fillna(0)

    # Добавляем price/returns фичи из aggregate_to_monthly для месяца 33
    month_33_price_features = month_33_data[
        [
            "shop_id",
            "item_id",
            "item_price_mean",
            "item_price_median",
            "item_price_min",
            "item_price_max",
            "transactions_count",
            "returns_count",
            "returns_sum",
        ]
    ].copy()

    test_enriched = test_enriched.merge(
        month_33_price_features,
        on=["shop_id", "item_id"],
        how="left",
    )

    # Заполняем пропуски нулями (для новых пар)
    price_feature_cols = [
        "item_price_mean",
        "item_price_median",
        "item_price_min",
        "item_price_max",
        "transactions_count",
        "returns_count",
        "returns_sum",
    ]
    test_enriched[price_feature_cols] = test_enriched[price_feature_cols].fillna(0)

    # Агрегаты по товару (средние за все время)
    item_aggregates = (
        sales_monthly_with_features.groupby("item_id")
        .agg({"item_cnt_month": "mean", "item_price_median": "mean"})
        .reset_index()
    )
    item_aggregates.columns = [
        "item_id",
        "item_avg_sales_all_time",
        "item_avg_price_all_time",
    ]
    test_enriched = test_enriched.merge(item_aggregates, on="item_id", how="left")

    # Агрегаты по магазину (средние за все время)
    shop_aggregates = (
        sales_monthly_with_features.groupby("shop_id")
        .agg({"item_cnt_month": "mean"})
        .reset_index()
    )
    shop_aggregates.columns = ["shop_id", "shop_avg_sales_all_time"]
    test_enriched = test_enriched.merge(shop_aggregates, on="shop_id", how="left")

    # Агрегаты по категории в магазине (средние за все время)
    category_shop_aggregates = (
        sales_monthly_with_features.groupby(["shop_id", "main_category"])
        .agg({"item_cnt_month": "mean"})
        .reset_index()
    )
    category_shop_aggregates.columns = [
        "shop_id",
        "main_category",
        "category_avg_sales_in_shop",
    ]
    test_enriched = test_enriched.merge(
        category_shop_aggregates, on=["shop_id", "main_category"], how="left"
    )

    # Заполняем пропуски в агрегатах нулями (для новых товаров/пар)
    aggregate_cols = [
        "item_avg_sales_all_time",
        "item_avg_price_all_time",
        "shop_avg_sales_all_time",
        "category_avg_sales_in_shop",
    ]
    test_enriched[aggregate_cols] = test_enriched[aggregate_cols].fillna(0)

    return test_enriched


def save_processed_data(
    sales_monthly: pd.DataFrame,
    sales_monthly_with_features: pd.DataFrame,
    test_enriched: pd.DataFrame,
    items_enriched: pd.DataFrame,
    shops_enriched: pd.DataFrame,
    item_categories_enriched: pd.DataFrame,
    output_path: Path,
    sales_monthly_with_features_encoded: pd.DataFrame = None,
    test_enriched_encoded: pd.DataFrame = None,
) -> None:
    """
    Сохранение всех обработанных данных в формате Parquet.

    Args:
        sales_monthly: Агрегированные месячные данные
        sales_monthly_with_features: Данные с фичами
        sales_monthly_with_features_encoded: Данные с закодированными категориальными признаками (опционально)
        test_enriched: Обогащенный test
        test_enriched_encoded: Обогащенный test с закодированными признаками (опционально)
        items_enriched: Обогащенный справочник товаров
        shops_enriched: Обогащенный справочник магазинов
        item_categories_enriched: Обогащенный справочник категорий
        output_path: Путь к директории для сохранения (Path объект)
    """

    output_path.mkdir(parents=True, exist_ok=True)
    print("Сохранение обработанных данных в формате Parquet...")

    # Сохраняем все датафреймы
    files_to_save = {
        "sales_monthly_clean.parquet": sales_monthly,
        "sales_monthly_with_features.parquet": sales_monthly_with_features,
        "test_enriched.parquet": test_enriched,
        "items_enriched.parquet": items_enriched,
        "shops_enriched.parquet": shops_enriched,
        "item_categories_enriched.parquet": item_categories_enriched,
    }

    # Добавляем encoded версию если она есть
    if sales_monthly_with_features_encoded is not None:
        files_to_save["sales_monthly_with_features_encoded.parquet"] = (
            sales_monthly_with_features_encoded
        )

    if test_enriched_encoded is not None:
        files_to_save["test_enriched_encoded.parquet"] = test_enriched_encoded

    for filename, df in files_to_save.items():
        filepath = output_path / filename
        df.to_parquet(filepath, index=False, engine="fastparquet")
        file_size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"{filename}: {len(df):,} строк, {file_size_mb:.2f} MB")

    print(f"\nВсе данные сохранены в {output_path}")


def validate_etl_results(
    sales_train_original: pd.DataFrame,
    sales_train_clean: pd.DataFrame,
    sales_monthly: pd.DataFrame,
    sales_monthly_with_features: pd.DataFrame,
    test_enriched: pd.DataFrame,
    items_enriched: pd.DataFrame,
    shops_enriched: pd.DataFrame,
    item_categories_enriched: pd.DataFrame,
    sales_monthly_with_features_encoded: pd.DataFrame = None,
    test_enriched_encoded: pd.DataFrame = None,
) -> dict:
    """
    Валидация результатов ETL pipeline.

    Проверяет:
    - Размерности данных (ожидаемое количество строк)
    - Отсутствие пропусков в ключевых столбцах
    - Корректность агрегации (суммы совпадают)
    - Корректность джойнов (нет потерянных записей)
    - Корректность фичей (лаги, статистики)
    - Корректность encoded версий (если предоставлены)

    Выводит статистику по:
    - Количеству удаленных выбросов
    - Количеству возвратов
    - Количеству заполненных пропусков
    - Распределению флагов в test

    Args:
        sales_train_original: Исходные данные sales_train
        sales_train_clean: Очищенные данные sales_train
        sales_monthly: Агрегированные месячные данные
        sales_monthly_with_features: Данные с фичами
        test_enriched: Обогащенный test
        items_enriched: Обогащенный справочник товаров
        shops_enriched: Обогащенный справочник магазинов
        item_categories_enriched: Обогащенный справочник категорий
        sales_monthly_with_features_encoded: Данные с закодированными признаками (опционально)
        test_enriched_encoded: Test с закодированными признаками (опционально)

    Returns:
        Словарь с результатами валидации
    """
    validation_results = {"errors": [], "warnings": [], "stats": {}}

    # 1. Статистика по очистке данных
    print("\n1. СТАТИСТИКА ПО ОЧИСТКЕ ДАННЫХ")

    removed_outliers = len(sales_train_original) - len(sales_train_clean)
    validation_results["stats"]["removed_outliers"] = removed_outliers
    print(f"Удалено выбросов: {removed_outliers:,} записей")

    returns_count = sales_train_clean["is_return"].sum()
    validation_results["stats"]["returns_count"] = int(returns_count)
    print(f"Возвратов (отрицательных значений): {returns_count:,}")

    # 2. Проверка размерностей
    print("\n2. ПРОВЕРКА РАЗМЕРНОСТЕЙ")

    # sales_monthly: должна быть меньше или равна исходным данным
    if len(sales_monthly) > len(sales_train_clean):
        validation_results["errors"].append(
            f"sales_monthly имеет больше записей ({len(sales_monthly):,}) чем sales_train_clean ({len(sales_train_clean):,})"
        )
        print(f"sales_monthly: {len(sales_monthly):,} записей (ОШИБКА)")
    else:
        print(f"sales_monthly: {len(sales_monthly):,} записей")

    # sales_monthly_with_features: проверяем количество уникальных пар x 34 месяца
    unique_pairs = sales_monthly_with_features[["shop_id", "item_id"]].drop_duplicates()
    expected_rows = len(unique_pairs) * 34
    if len(sales_monthly_with_features) != expected_rows:
        validation_results["warnings"].append(
            f"sales_monthly_with_features: ожидалось {expected_rows:,}, получено {len(sales_monthly_with_features):,}"
        )
        print(
            f"sales_monthly_with_features: {len(sales_monthly_with_features):,} записей (ожидалось {expected_rows:,})"
        )
    else:
        print(
            f"sales_monthly_with_features: {len(sales_monthly_with_features):,} записей ({len(unique_pairs):,} пар x 34 месяца)"
        )

    # test_enriched: должна быть равна test
    if len(test_enriched) != 214200:
        validation_results["errors"].append(
            f"test_enriched имеет {len(test_enriched):,} записей вместо ожидаемых 214,200"
        )
        print(f"test_enriched: {len(test_enriched):,} записей (ОШИБКА)")
    else:
        print(f"test_enriched: {len(test_enriched):,} записей")

    # Справочники
    print(f"items_enriched: {len(items_enriched):,} записей")
    print(f"shops_enriched: {len(shops_enriched):,} записей")
    print(f"item_categories_enriched: {len(item_categories_enriched):,} записей")

    # 3. Проверка пропусков
    print("\n3. ПРОВЕРКА ПРОПУСКОВ")

    # Ключевые столбцы для проверки
    key_columns_train = ["shop_id", "item_id", "date_block_num", "item_cnt_month"]
    key_columns_test = [
        "ID",
        "shop_id",
        "item_id",
        "date_block_num",
        "has_pair_history",
        "main_category",
        "city",
        "shop_type",
    ]

    # Проверка train
    missing_train = sales_monthly_with_features[key_columns_train].isnull().sum()
    if missing_train.sum() > 0:
        validation_results["errors"].append(
            f"Пропуски в train данных: {dict(missing_train[missing_train > 0])}"
        )
        print("Найдены пропуски в train:")
        for col, count in missing_train[missing_train > 0].items():
            print(f"- {col}: {count:,}")
    else:
        print("Нет пропусков в ключевых столбцах train")

    # Проверка test
    missing_test = test_enriched[key_columns_test].isnull().sum()
    if missing_test.sum() > 0:
        validation_results["errors"].append(
            f"Пропуски в test данных: {dict(missing_test[missing_test > 0])}"
        )
        print("Найдены пропуски в test:")
        for col, count in missing_test[missing_test > 0].items():
            print(f"- {col}: {count:,}")
    else:
        print("Нет пропусков в ключевых столбцах test")

    # Проверка всех фичей на пропуски
    feature_cols = [
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

    missing_features_train = sales_monthly_with_features[feature_cols].isnull().sum()
    if missing_features_train.sum() > 0:
        validation_results["errors"].append(
            f"Пропуски в фичах train: {dict(missing_features_train[missing_features_train > 0])}"
        )
        print("Найдены пропуски в фичах train:")
        for col, count in missing_features_train[missing_features_train > 0].items():
            print(f"- {col}: {count:,}")
    else:
        print("Нет пропусков в фичах train")

    missing_features_test = test_enriched[feature_cols].isnull().sum()
    if missing_features_test.sum() > 0:
        validation_results["errors"].append(
            f"Пропуски в фичах test: {dict(missing_features_test[missing_features_test > 0])}"
        )
        print("Найдены пропуски в фичах test:")
        for col, count in missing_features_test[missing_features_test > 0].items():
            print(f"{col}: {count:,}")
    else:
        print("Нет пропусков в фичах test")

    # 4. Проверка корректности агрегации
    print("\n4. ПРОВЕРКА КОРРЕКТНОСТИ АГРЕГАЦИИ")

    # Проверяем, что item_total_sales = сумма item_cnt_month по всем магазинам
    sample_month = sales_monthly_with_features[
        sales_monthly_with_features["date_block_num"] == 33
    ]

    if len(sample_month) > 0:
        # Агрегируем
        manual_agg = (
            sample_month.groupby("item_id")["item_cnt_month"].sum().reset_index()
        )
        manual_agg.columns = ["item_id", "manual_total"]

        # Сравниваем с item_total_sales
        comparison = (
            sample_month[["item_id", "item_total_sales"]]
            .drop_duplicates()
            .merge(manual_agg, on="item_id")
        )

        # Допускаем небольшую погрешность из-за округления
        diff = (comparison["item_total_sales"] - comparison["manual_total"]).abs()
        if (diff > 0.01).any():
            validation_results["warnings"].append(
                f"Несоответствие в item_total_sales: найдено {(diff > 0.01).sum()} расхождений"
            )
            print(
                f"Найдены расхождения в item_total_sales ({(diff > 0.01).sum()} из {len(comparison)})"
            )
        else:
            print("Агрегация item_total_sales корректна")

    # 5. Проверка корректности джойнов
    print("\n5. ПРОВЕРКА КОРРЕКТНОСТИ ДЖОЙНОВ")

    # Проверяем, что все item_id из sales_monthly есть в items_enriched
    items_in_sales = set(sales_monthly_with_features["item_id"].unique())
    items_in_ref = set(items_enriched["item_id"].unique())
    missing_items = items_in_sales - items_in_ref

    if len(missing_items) > 0:
        validation_results["errors"].append(
            f"Потеряны товары при джойне: {len(missing_items)} товаров"
        )
        print(f"Потеряно товаров: {len(missing_items)}")
    else:
        print("Все товары из sales присутствуют в items_enriched")

    # Проверяем, что все shop_id из sales_monthly есть в shops_enriched
    shops_in_sales = set(sales_monthly_with_features["shop_id"].unique())
    shops_in_ref = set(shops_enriched["shop_id"].unique())
    missing_shops = shops_in_sales - shops_in_ref

    if len(missing_shops) > 0:
        validation_results["errors"].append(
            f"Потеряны магазины при джойне: {len(missing_shops)} магазинов"
        )
        print(f"Потеряно магазинов: {len(missing_shops)}")
    else:
        print("Все магазины из sales присутствуют в shops_enriched")

    # 6. Проверка корректности фичей
    print("\n6. ПРОВЕРКА КОРРЕКТНОСТИ ФИЧЕЙ")

    # Проверяем диапазоны лагов
    for lag in [1, 2, 3, 6, 12]:
        col = f"lag_{lag}"
        if col in sales_monthly_with_features.columns:
            negative_lags = (sales_monthly_with_features[col] < 0).sum()
            if negative_lags > 0:
                validation_results["warnings"].append(
                    f"Отрицательные значения в {col}: {negative_lags}"
                )
                print(f"{col}: найдено {negative_lags:,} отрицательных значений")
            else:
                print(f"{col}: все значения >= 0")

    # Проверяем диапазоны скользящих средних
    for window in [3, 6, 12]:
        col = f"mean_{window}m"
        if col in sales_monthly_with_features.columns:
            negative_means = (sales_monthly_with_features[col] < 0).sum()
            if negative_means > 0:
                validation_results["warnings"].append(
                    f"Отрицательные значения в {col}: {negative_means}"
                )
                print(f"{col}: найдено {negative_means:,} отрицательных значений")
            else:
                print(f"{col}: все значения >= 0")

    # Проверяем временные фичи
    if "month" in sales_monthly_with_features.columns:
        months = sales_monthly_with_features["month"].unique()
        expected_months = set(range(1, 13))
        if set(months) != expected_months:
            validation_results["warnings"].append(
                f"Неожиданные значения month: {sorted(months)}"
            )
            print(f"month: найдены неожиданные значения {sorted(months)}")
        else:
            print("month: корректные значения (1-12)")

    # 7. Статистика по заполненным пропускам
    print("\n7. СТАТИСТИКА ПО ЗАПОЛНЕННЫМ ПРОПУСКАМ")

    # Подсчитываем, сколько записей было заполнено нулями
    filled_zeros = (sales_monthly_with_features["item_cnt_month"] == 0).sum()
    validation_results["stats"]["filled_zeros"] = int(filled_zeros)
    print(f"Заполнено нулями (item_cnt_month = 0): {filled_zeros:,} записей")
    print(
        f"Записей с продажами (item_cnt_month > 0): {(sales_monthly_with_features['item_cnt_month'] > 0).sum():,} записей"
    )

    # 8. Статистика по флагам в test
    print("\n8. СТАТИСТИКА ПО ФЛАГАМ В TEST")

    if "has_sales_history" in test_enriched.columns:
        items_with_history = test_enriched["has_sales_history"].sum()
        new_items = (~test_enriched["has_sales_history"]).sum()
        validation_results["stats"]["test_items_with_history"] = int(items_with_history)
        validation_results["stats"]["test_new_items"] = int(new_items)
        print(
            f"Товаров с историей: {items_with_history:,} ({items_with_history / len(test_enriched) * 100:.1f}%)"
        )
        print(
            f"Новых товаров: {new_items:,} ({new_items / len(test_enriched) * 100:.1f}%)"
        )

    if "has_pair_history" in test_enriched.columns:
        pairs_with_history = test_enriched["has_pair_history"].sum()
        new_pairs = (~test_enriched["has_pair_history"]).sum()
        validation_results["stats"]["test_pairs_with_history"] = int(pairs_with_history)
        validation_results["stats"]["test_new_pairs"] = int(new_pairs)
        print(
            f"Пар с историей: {pairs_with_history:,} ({pairs_with_history / len(test_enriched) * 100:.1f}%)"
        )
        print(f"Новых пар: {new_pairs:,} ({new_pairs / len(test_enriched) * 100:.1f}%)")

    # 9. Проверка encoded версий (если предоставлены)
    if (
        sales_monthly_with_features_encoded is not None
        or test_enriched_encoded is not None
    ):
        print("\n9. ПРОВЕРКА ENCODED ВЕРСИЙ")

        if sales_monthly_with_features_encoded is not None:
            print(
                f"sales_monthly_with_features_encoded: {len(sales_monthly_with_features_encoded):,} строк, {sales_monthly_with_features_encoded.shape[1]} колонок"
            )

            # Проверка количества строк
            if len(sales_monthly_with_features_encoded) != len(
                sales_monthly_with_features
            ):
                validation_results["errors"].append(
                    f"Количество строк не совпадает: encoded={len(sales_monthly_with_features_encoded):,}, original={len(sales_monthly_with_features):,}"
                )
                print("ОШИБКА: Количество строк не совпадает")
            else:
                print("Количество строк совпадает с оригиналом")

            # Проверка пропусков
            missing_encoded_train = sales_monthly_with_features_encoded.isnull().sum()
            if missing_encoded_train.sum() > 0:
                validation_results["warnings"].append(
                    f"Пропуски в sales_monthly_with_features_encoded: {dict(missing_encoded_train[missing_encoded_train > 0])}"
                )
                print("Найдены пропуски в encoded train:")
                for col, count in missing_encoded_train[
                    missing_encoded_train > 0
                ].items():
                    print(f"- {col}: {count:,}")
            else:
                print("Нет пропусков в encoded train")

            # Проверка типов данных (не должно быть bool)
            bool_cols = sales_monthly_with_features_encoded.select_dtypes(
                include=["bool"]
            ).columns.tolist()
            if bool_cols:
                validation_results["warnings"].append(
                    f"Найдены bool колонки в sales_monthly_with_features_encoded: {bool_cols}"
                )
                print(f"Найдены bool колонки: {bool_cols}")
            else:
                print("Все колонки имеют числовые типы (нет bool)")

        if test_enriched_encoded is not None:
            print(
                f"\ntest_enriched_encoded: {len(test_enriched_encoded):,} строк, {test_enriched_encoded.shape[1]} колонок"
            )

            # Проверка количества строк
            if len(test_enriched_encoded) != len(test_enriched):
                validation_results["errors"].append(
                    f"Количество строк не совпадает: encoded={len(test_enriched_encoded):,}, original={len(test_enriched):,}"
                )
                print("ОШИБКА: Количество строк не совпадает")
            else:
                print("Количество строк совпадает с оригиналом")

            # Проверка пропусков
            missing_encoded_test = test_enriched_encoded.isnull().sum()
            if missing_encoded_test.sum() > 0:
                validation_results["warnings"].append(
                    f"Пропуски в test_enriched_encoded: {dict(missing_encoded_test[missing_encoded_test > 0])}"
                )
                print("Найдены пропуски в encoded test:")
                for col, count in missing_encoded_test[
                    missing_encoded_test > 0
                ].items():
                    print(f"- {col}: {count:,}")
            else:
                print("Нет пропусков в encoded test")

            # Проверка типов данных (не должно быть bool)
            bool_cols = test_enriched_encoded.select_dtypes(
                include=["bool"]
            ).columns.tolist()
            if bool_cols:
                validation_results["warnings"].append(
                    f"Найдены bool колонки в test_enriched_encoded: {bool_cols}"
                )
                print(f"Найдены bool колонки: {bool_cols}")
            else:
                print("Все колонки имеют числовые типы (нет bool)")

    # Итоговый отчет
    print("\nИТОГИ ВАЛИДАЦИИ")

    if len(validation_results["errors"]) == 0:
        print("КРИТИЧЕСКИХ ОШИБОК НЕ НАЙДЕНО")
    else:
        print(f"НАЙДЕНО КРИТИЧЕСКИХ ОШИБОК: {len(validation_results['errors'])}")
        for error in validation_results["errors"]:
            print(f"- {error}")

    if len(validation_results["warnings"]) == 0:
        print("ПРЕДУПРЕЖДЕНИЙ НЕТ")
    else:
        print(f"ПРЕДУПРЕЖДЕНИЙ: {len(validation_results['warnings'])}")
        for warning in validation_results["warnings"]:
            print(f"- {warning}")

    return validation_results


def encode_categorical_features(
    sales_monthly_with_features: pd.DataFrame, label_encoders: dict = None
) -> tuple[pd.DataFrame, dict]:
    """
    Кодирование категориальных признаков для моделирования.

    Применяет:
    - Булевы признаки → int (0/1)
    - shop_type → One-Hot Encoding
    - main_category, sub_category, city → Label Encoding
    - item_name → len_item_name (длина названия), затем удаляется
    - shop_name → удаляется

    Args:
        sales_monthly_with_features: Датафрейм с базовыми фичами
        label_encoders: Словарь с маппингами для Label Encoding (если None - создает новые)

    Returns:
        Кортеж: (датафрейм с закодированными признаками, словарь с маппингами)
    """
    df = sales_monthly_with_features.copy()

    if label_encoders is None:
        label_encoders = {}

    # Boolean -> Int
    bool_columns = [
        "is_digital",
        "has_sales_history",
        "is_online",
        "is_franchise",
        "is_holiday_season",
        "has_pair_history",
    ]
    for column in bool_columns:
        if column in df.columns:
            df[column] = df[column].astype(int)

    if "item_name" in df.columns:
        df["len_item_name"] = df["item_name"].str.len().fillna(0).astype(int)
        df = df.drop(columns=["item_name"])

    if "shop_name" in df.columns:
        df = df.drop(columns=["shop_name"])

    # One-Hot
    if "shop_type" in df.columns:
        dummies = pd.get_dummies(df["shop_type"], prefix="shop_type")
        dummies = dummies.astype(int)
        df = pd.concat([df, dummies], axis=1)
        df = df.drop(columns=["shop_type"])

    # Label Encoding
    categorical_columns = ["main_category", "sub_category", "city"]
    for column in categorical_columns:
        if column in df.columns:
            if column not in label_encoders:
                # Создаем новый маппинг
                unique_values = sorted(df[column].dropna().unique())
                label_encoders[column] = {
                    val: idx for idx, val in enumerate(unique_values)
                }

            # Применяем маппинг
            df[f"{column}_le"] = (
                df[column].map(label_encoders[column]).fillna(-1).astype("int32")
            )
            df = df.drop(columns=[column])

    return df, label_encoders
