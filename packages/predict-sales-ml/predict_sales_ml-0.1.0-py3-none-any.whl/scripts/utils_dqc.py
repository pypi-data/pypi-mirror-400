import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Callable


def check_completeness(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    threshold: float = 1.0,
    name: str = "Dataset",
) -> Dict:
    """
    Проверяет полноту данных (Completeness)

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    columns : list of str, optional
        Список столбцов для проверки. Если None, проверяются все столбцы
    threshold : float
        Минимальный порог полноты (0.0 - 1.0)
    name : str
        Название датасета для вывода

    Returns:
    --------
    dict
        Словарь с результатами проверки полноты
    """
    if columns is None:
        columns = df.columns.tolist()

    total_rows = len(df)
    results = {
        "columns": {},
        "overall_completeness": 0.0,
        "threshold": threshold,
        "passed": True,
    }

    print(f"\nПроверка полноты данных ({name}):")
    print(f"Всего строк: {total_rows:,}")

    total_missing = 0
    total_cells = total_rows * len(columns)

    for col in columns:
        if col not in df.columns:
            print(f"Столбец '{col}' не найден в датафрейме")
            continue

        missing_count = df[col].isnull().sum()
        missing_pct = (missing_count / total_rows) * 100 if total_rows > 0 else 0
        completeness = 1 - (missing_count / total_rows) if total_rows > 0 else 0

        results["columns"][col] = {
            "missing_count": int(missing_count),
            "missing_percentage": round(missing_pct, 2),
            "completeness": round(completeness, 4),
            "passed": completeness >= threshold,
        }

        total_missing += missing_count

        status = "passed" if completeness >= threshold else "failed"
        print(
            f"{status} {col}: пропущено {missing_count:,} ({missing_pct:.2f}%), полнота: {completeness * 100:.2f}%"
        )

    results["overall_completeness"] = round(
        1 - (total_missing / total_cells) if total_cells > 0 else 0, 4
    )
    results["passed"] = results["overall_completeness"] >= threshold

    print(f"\nОбщая полнота: {results['overall_completeness'] * 100:.2f}%")
    print(f"Порог: {threshold * 100:.2f}%")
    print(f"Результат: {'ПРОЙДЕНО' if results['passed'] else 'НЕ ПРОЙДЕНО'}")

    return results


def check_accuracy(
    df: pd.DataFrame, rules: Dict[str, Callable], name: str = "Dataset"
) -> Dict:
    """
    Проверяет точность данных (Accuracy)

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    rules : dict
        Словарь с правилами проверки {column: validation_function}
    name : str
        Название датасета для вывода

    Returns:
    --------
    dict
        Словарь с результатами проверки точности
    """
    results: Dict = {"columns": {}, "overall_accuracy": 0.0}

    print(f"\nПроверка точности данных ({name}):")

    total_valid = 0
    total_checked = 0

    for col, rule in rules.items():
        if col not in df.columns:
            print(f"Столбец '{col}' не найден в датафрейме — пропуск")
            continue

        series = df[col]
        n = len(series)

        if n == 0:
            print(f"{col}: пустой столбец, пропуск проверки")
            results["columns"][col] = {
                "valid_count": 0,
                "invalid_count": 0,
                "total": 0,
                "accuracy": 0.0,
                "invalid_percentage": 0.0,
            }
            continue

        # Применяем правило проверки
        try:
            mask = rule(series)
        except Exception:
            mask = series.apply(rule)

        if isinstance(mask, (list, np.ndarray, pd.Series)):
            mask = pd.Series(mask, index=series.index).astype(bool)
        else:
            mask = pd.Series(bool(mask), index=series.index)

        valid_count = int(mask.sum())
        invalid_count = int(n - valid_count)
        accuracy = valid_count / n if n > 0 else 0.0
        invalid_pct = invalid_count / n * 100 if n > 0 else 0.0

        total_valid += valid_count
        total_checked += n

        results["columns"][col] = {
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "total": n,
            "accuracy": round(accuracy, 4),
            "invalid_percentage": round(invalid_pct, 2),
        }

        print(
            f"{col}: валидных {valid_count:,} из {n:,} "
            f"({accuracy * 100:.2f}% точных, "
            f"некорректных {invalid_count:,} = {invalid_pct:.2f}%)"
        )

    results["overall_accuracy"] = (
        round(total_valid / total_checked, 4) if total_checked > 0 else 0.0
    )

    print(
        f"\nОбщая точность по всем проверенным столбцам: "
        f"{results['overall_accuracy'] * 100:.2f}%"
    )

    return results


def check_consistency(
    df: pd.DataFrame, consistency_rules: List[Callable], name: str = "Dataset"
) -> Dict:
    """
    Проверяет согласованность данных (Consistency)

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    consistency_rules : list of callable
        Список функций для проверки согласованности
    name : str
        Название датасета для вывода

    Returns:
    --------
    dict
        Словарь с результатами проверки согласованности
    """
    results: Dict = {"rules": {}, "overall_consistency": 0.0}

    print(f"\nПроверка согласованности данных ({name}):")

    total_passed = 0
    total_checked = 0
    n_rows = len(df)

    for idx, rule in enumerate(consistency_rules, 1):
        rule_name = getattr(rule, "__name__", f"rule_{idx}")

        if n_rows == 0:
            print(f"{rule_name}: датафрейм пустой, пропуск проверки")
            results["rules"][rule_name] = {
                "passed_count": 0,
                "failed_count": 0,
                "total": 0,
                "consistency": 0.0,
                "failed_percentage": 0.0,
            }
            continue

        try:
            mask = rule(df)
        except Exception as e:
            print(f"{rule_name}: ошибка при выполнении правила: {e}")
            results["rules"][rule_name] = {
                "passed_count": 0,
                "failed_count": n_rows,
                "total": n_rows,
                "consistency": 0.0,
                "failed_percentage": 100.0,
                "error": str(e),
            }
            total_checked += n_rows
            continue

        if isinstance(mask, (list, np.ndarray, pd.Series)):
            mask = pd.Series(mask, index=df.index).astype(bool)
        else:
            mask = pd.Series(bool(mask), index=df.index)

        passed_count = int(mask.sum())
        failed_count = int(n_rows - passed_count)
        consistency = passed_count / n_rows if n_rows > 0 else 0.0
        failed_pct = failed_count / n_rows * 100 if n_rows > 0 else 0.0

        total_passed += passed_count
        total_checked += n_rows

        results["rules"][rule_name] = {
            "passed_count": passed_count,
            "failed_count": failed_count,
            "total": n_rows,
            "consistency": round(consistency, 4),
            "failed_percentage": round(failed_pct, 2),
        }

        print(
            f"{rule_name}: согласованных {passed_count:,} из {n_rows:,} "
            f"({consistency * 100:.2f}% согласованных, "
            f"несогласованных {failed_count:,} = {failed_pct:.2f}%)"
        )

    results["overall_consistency"] = (
        round(total_passed / total_checked, 4) if total_checked > 0 else 0.0
    )

    print(
        f"\nОбщая согласованность по всем правилам: "
        f"{results['overall_consistency'] * 100:.2f}%"
    )

    return results


def check_validity(
    df: pd.DataFrame,
    validation_rules: Dict[str, Union[Callable, Dict]],
    name: str = "Dataset",
) -> Dict:
    """
    Проверяет валидность данных (Validity)

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    validation_rules : dict
        Словарь с правилами валидации {column: rule}
        rule может быть:
        - Callable: функция, принимающая pd.Series и возвращающая булевую маску
        - Dict: словарь с правилами (для будущего расширения)
    name : str
        Название датасета для вывода

    Returns:
    --------
    dict
        Словарь с результатами проверки валидности
    """
    results: Dict = {"columns": {}, "overall_validity": 0.0}

    print(f"\nПроверка валидности данных ({name}):")

    total_valid = 0
    total_checked = 0

    for col, rule in validation_rules.items():
        if col not in df.columns:
            print(f"Столбец '{col}' не найден в датафрейме — пропуск")
            continue

        series = df[col]
        n = len(series)

        if n == 0:
            print(f"{col}: пустой столбец, пропуск проверки")
            results["columns"][col] = {
                "valid_count": 0,
                "invalid_count": 0,
                "total": 0,
                "validity": 0.0,
                "invalid_percentage": 0.0,
            }
            continue

        # Применяем правило валидации
        try:
            if callable(rule):
                # Если правило - функция, применяем как в check_accuracy
                mask = rule(series)
            elif isinstance(rule, dict):
                # Если правило - словарь, обрабатываем специальные случаи
                # Пока поддерживаем только простые случаи, можно расширить
                mask = _apply_dict_rule(series, rule)
            else:
                print(f"{col}: неподдерживаемый тип правила, пропуск")
                continue
        except Exception as e:
            # Если правило ожидает поэлементный вызов
            if callable(rule):
                try:
                    mask = series.apply(rule)
                except Exception:
                    print(f"{col}: ошибка при выполнении правила: {e}")
                    results["columns"][col] = {
                        "valid_count": 0,
                        "invalid_count": n,
                        "total": n,
                        "validity": 0.0,
                        "invalid_percentage": 100.0,
                        "error": str(e),
                    }
                    total_checked += n
                    continue
            else:
                print(f"{col}: ошибка при выполнении правила: {e}")
                continue

        # Приводим результат к булевой Series
        if isinstance(mask, (list, np.ndarray, pd.Series)):
            mask = pd.Series(mask, index=series.index).astype(bool)
        else:
            mask = pd.Series(bool(mask), index=series.index)

        valid_count = int(mask.sum())
        invalid_count = int(n - valid_count)
        validity = valid_count / n if n > 0 else 0.0
        invalid_pct = invalid_count / n * 100 if n > 0 else 0.0

        total_valid += valid_count
        total_checked += n

        results["columns"][col] = {
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "total": n,
            "validity": round(validity, 4),
            "invalid_percentage": round(invalid_pct, 2),
        }

        print(
            f"{col}: валидных {valid_count:,} из {n:,} "
            f"({validity * 100:.2f}% валидных, "
            f"невалидных {invalid_count:,} = {invalid_pct:.2f}%)"
        )

    results["overall_validity"] = (
        round(total_valid / total_checked, 4) if total_checked > 0 else 0.0
    )

    print(
        f"\nОбщая валидность по всем проверенным столбцам: "
        f"{results['overall_validity'] * 100:.2f}%"
    )

    return results


def _apply_dict_rule(series: pd.Series, rule: Dict) -> pd.Series:
    """
    Вспомогательная функция для применения правил в формате словаря.

    Поддерживаемые правила:
    - {"type": "datetime", "format": "%d.%m.%Y"} - проверка формата даты
    - {"type": "int"} - проверка что значения целые
    - {"type": "float"} - проверка что значения float-числа
    - {"min": value, "max": value} - проверка диапазона
    - {"not_null": True} - проверка что нет null
    """
    mask = pd.Series(True, index=series.index)

    if "type" in rule:
        if rule["type"] == "datetime":
            format_str = rule.get("format", None)
            if format_str:
                parsed = pd.to_datetime(series, format=format_str, errors="coerce")
                mask = mask & parsed.notna()
            else:
                parsed = pd.to_datetime(series, errors="coerce")
                mask = mask & parsed.notna()
        elif rule["type"] == "int":
            mask = mask & series.apply(
                lambda x: isinstance(x, (int, np.integer))
                or (pd.isna(x) and pd.api.types.is_integer_dtype(series))
            )
        elif rule["type"] == "float":
            mask = mask & pd.api.types.is_numeric_dtype(series)

    if "min" in rule:
        mask = mask & (series >= rule["min"])

    if "max" in rule:
        mask = mask & (series <= rule["max"])

    if rule.get("not_null", False):
        mask = mask & series.notna()

    return mask


def check_uniqueness(
    df: pd.DataFrame, unique_columns: Union[List[str], str], name: str = "Dataset"
) -> Dict:
    """
    Проверяет уникальность данных (Uniqueness)

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    unique_columns : str or list of str
        Столбец(ы) для проверки уникальности
    name : str
        Название датасета для вывода

    Returns:
    --------
    dict
        Словарь с результатами проверки уникальности
    """
    # Нормализуем вход: приводим к списку
    if isinstance(unique_columns, str):
        columns_list = [unique_columns]
    else:
        columns_list = unique_columns

    results: Dict = {"columns": {}, "overall_uniqueness": 0.0}

    print(f"\nПроверка уникальности данных ({name}):")

    total_unique = 0
    total_checked = 0

    for cols in columns_list:
        # Если один столбец - используем его имя, иначе комбинацию
        if isinstance(cols, str):
            col_name = cols
            cols = [cols]
        else:
            col_name = "_".join(cols)

        # Проверяем что все столбцы существуют
        missing_cols = [c for c in cols if c not in df.columns]
        if missing_cols:
            print(f"Столбцы {missing_cols} не найдены в датафрейме — пропуск")
            continue

        # Проверяем уникальность
        if len(cols) == 1:
            # Один столбец
            series = df[cols[0]]
            unique_count = series.nunique()
            total_count = len(series)
        else:
            # Комбинация столбцов
            unique_count = df[cols].drop_duplicates().shape[0]
            total_count = len(df)

        duplicate_count = total_count - unique_count
        uniqueness = unique_count / total_count if total_count > 0 else 0.0
        is_unique = unique_count == total_count

        total_unique += unique_count
        total_checked += total_count

        results["columns"][col_name] = {
            "unique_count": int(unique_count),
            "total_count": int(total_count),
            "duplicate_count": int(duplicate_count),
            "uniqueness": round(uniqueness, 4),
            "is_unique": is_unique,
        }

        status = "уникальны" if is_unique else "есть дубликаты"
        print(
            f"{col_name}: уникальных {unique_count:,} из {total_count:,} "
            f"({uniqueness * 100:.2f}% уникальности, "
            f"дубликатов {duplicate_count:,}) — {status}"
        )

    results["overall_uniqueness"] = (
        round(total_unique / total_checked, 4) if total_checked > 0 else 0.0
    )

    print(f"\nОбщая уникальность: {results['overall_uniqueness'] * 100:.2f}%")

    return results


def check_integrity(
    df: pd.DataFrame,
    reference_df: pd.DataFrame,
    foreign_keys: Dict[str, str],
    name: str = "Dataset",
    reference_name: str = "Reference Dataset",
) -> Dict:
    """
    Проверяет целостность данных (Integrity)

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    reference_df : pd.DataFrame
        Референсный датафрейм для проверки внешних ключей
    foreign_keys : dict
        Словарь соответствий {column_in_df: column_in_reference_df}
    name : str
        Название датасета для вывода
    reference_name : str
        Название референсного датасета

    Returns:
    --------
    dict
        Словарь с результатами проверки целостности
    """
    results: Dict = {"foreign_keys": {}, "overall_integrity": 0.0}

    print(f"\nПроверка целостности данных ({name} -> {reference_name}):")

    total_valid = 0
    total_checked = 0

    for col_in_df, col_in_ref in foreign_keys.items():
        if col_in_df not in df.columns:
            print(f"Столбец '{col_in_df}' не найден в датафрейме {name} — пропуск")
            continue
        if col_in_ref not in reference_df.columns:
            print(
                f"Столбец '{col_in_ref}' не найден в датафрейме {reference_name} — пропуск"
            )
            continue

        series = df[col_in_df]
        n = len(series)

        if n == 0:
            print(f"{col_in_df}: пустой столбец, пропуск проверки")
            results["foreign_keys"][col_in_df] = {
                "valid_count": 0,
                "invalid_count": 0,
                "total": 0,
                "integrity": 0.0,
                "invalid_percentage": 0.0,
                "invalid_values": [],
            }
            continue

        # Получаем множество допустимых значений из референсного датафрейма
        valid_values = set(reference_df[col_in_ref].unique())

        # Проверяем какие значения из df присутствуют в reference_df
        mask = series.isin(valid_values)

        valid_count = int(mask.sum())
        invalid_count = int(n - valid_count)
        integrity = valid_count / n if n > 0 else 0.0
        invalid_pct = invalid_count / n * 100 if n > 0 else 0.0

        # Получаем примеры невалидных значений (первые 10 уникальных)
        invalid_values = series[~mask].unique()[:10].tolist()

        total_valid += valid_count
        total_checked += n

        results["foreign_keys"][col_in_df] = {
            "valid_count": valid_count,
            "invalid_count": invalid_count,
            "total": n,
            "integrity": round(integrity, 4),
            "invalid_percentage": round(invalid_pct, 2),
            "invalid_values": invalid_values,
        }

        status = "ПРОЙДЕНО" if integrity == 1.0 else "НЕ ПРОЙДЕНО"
        print(
            f"{col_in_df} -> {col_in_ref}: валидных {valid_count:,} из {n:,} "
            f"({integrity * 100:.2f}% целостности, "
            f"невалидных {invalid_count:,} = {invalid_pct:.2f}%) — {status}"
        )

        if invalid_count > 0 and len(invalid_values) > 0:
            print(f"  Примеры невалидных значений: {invalid_values[:5]}")

    results["overall_integrity"] = (
        round(total_valid / total_checked, 4) if total_checked > 0 else 0.0
    )

    print(f"\nОбщая целостность: {results['overall_integrity'] * 100:.2f}%")

    return results


def check_timeliness(
    df: pd.DataFrame,
    date_column: str,
    period_column: str,
    group_columns: List[str],
    expected_periods: Optional[List] = None,
    name: str = "Dataset",
) -> Dict:
    """
    Проверяет актуальность и непрерывность временных рядов (Timeliness)
    """
    results: Dict = {
        "groups": {},
        "summary": {
            "total_groups": 0,
            "groups_with_gaps": 0,
            "total_gaps": 0,
            "avg_gaps_per_group": 0.0,
        },
    }

    print(f"\nПроверка актуальности данных ({name}):")

    # Проверяем наличие столбцов
    required_cols = [date_column, period_column] + group_columns
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"Столбцы {missing_cols} не найдены в датафрейме")
        return results

    if len(df) == 0:
        print("Датафрейм пустой")
        return results

    # Определяем ожидаемые периоды
    if expected_periods is None:
        min_period = df[period_column].min()
        max_period = df[period_column].max()
        expected_periods = list(range(int(min_period), int(max_period) + 1))

    expected_periods_set = set(expected_periods)

    # Группируем данные
    grouped = df.groupby(group_columns)[period_column].apply(set).reset_index()
    grouped.columns = group_columns + ["observed_periods"]

    total_groups = len(grouped)
    groups_with_gaps = 0
    total_gaps = 0

    for _, row in grouped.iterrows():
        observed = row["observed_periods"]
        missing = expected_periods_set - observed
        gap_count = len(missing)

        group_key = tuple(row[col] for col in group_columns)
        group_name = "_".join(str(v) for v in group_key)

        if gap_count > 0:
            groups_with_gaps += 1
            total_gaps += gap_count

        results["groups"][group_name] = {
            "observed_periods": sorted(list(observed)),
            "missing_periods": sorted(list(missing)),
            "gap_count": gap_count,
            "completeness": round(len(observed) / len(expected_periods_set), 4),
        }

    results["summary"]["total_groups"] = total_groups
    results["summary"]["groups_with_gaps"] = groups_with_gaps
    results["summary"]["total_gaps"] = total_gaps
    results["summary"]["avg_gaps_per_group"] = round(
        total_gaps / total_groups if total_groups > 0 else 0, 2
    )

    print(f"Всего групп: {total_groups:,}")
    print(
        f"Групп с пропусками: {groups_with_gaps:,} "
        f"({groups_with_gaps / total_groups * 100:.2f}%)"
    )
    print(f"Всего пропусков: {total_gaps:,}")
    print(
        f"Среднее пропусков на группу: {results['summary']['avg_gaps_per_group']:.2f}"
    )

    # Показываем топ групп с наибольшим количеством пропусков
    if groups_with_gaps > 0:
        top_gaps = sorted(
            [
                (k, v["gap_count"])
                for k, v in results["groups"].items()
                if v["gap_count"] > 0
            ],
            key=lambda x: x[1],
            reverse=True,
        )[:10]
        print("\nТоп-10 групп с наибольшим количеством пропусков:")
        for group_name, gap_count in top_gaps:
            print(f"  {group_name}: {gap_count} пропусков")

    return results


def check_poor_dynamic(
    df: pd.DataFrame,
    date_column: str,
    period_column: str,
    value_column: str,
    group_columns: List[str],
    name: str = "Dataset",
) -> Dict:
    """
    Проверяет плохую динамику продаж (Poor Dynamic)

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    date_column : str
        Столбец с датой
    period_column : str
        Столбец с номером периода (например, date_block_num)
    value_column : str
        Столбец со значениями для анализа (например, item_cnt_day)
    group_columns : list of str
        Столбцы для группировки (например, ['shop_id', 'item_id'])
    name : str
        Название датасета для вывода

    Returns:
    --------
    dict
        Словарь с результатами проверки плохой динамики
    """
    results: Dict = {
        "groups": {},
        "summary": {
            "total_groups": 0,
            "groups_with_zero_sales": 0,
            "groups_with_sudden_drops": 0,
            "groups_with_sudden_growths": 0,
        },
    }

    print(f"\nПроверка динамики продаж ({name}):")

    # Проверяем наличие столбцов
    required_cols = [date_column, period_column, value_column] + group_columns
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"Столбцы {missing_cols} не найдены в датафрейме")
        return results

    if len(df) == 0:
        print("Датафрейм пустой")
        return results

    # Агрегируем данные по группам и периодам
    agg_df = (
        df.groupby(group_columns + [period_column])[value_column].sum().reset_index()
    )
    agg_df = agg_df.sort_values(group_columns + [period_column])

    # Группируем по основным столбцам
    grouped = agg_df.groupby(group_columns)

    total_groups = len(grouped)
    groups_with_zero_sales = 0
    groups_with_sudden_drops = 0
    groups_with_sudden_growths = 0

    # Пороги для определения резких изменений (в процентах)
    drop_threshold = 0.8  # падение на 80% и более
    growth_threshold = 5.0  # рост в 5 раз и более

    for group_key, group_data in grouped:
        group_name = "_".join(str(v) for v in group_key)
        values = group_data[value_column].values
        periods = group_data[period_column].values

        # Проверка на нулевые продажи
        zero_periods = np.sum(values == 0)
        has_zero_sales = zero_periods > 0

        # Проверка на резкие падения
        sudden_drops = []
        if len(values) > 1:
            for i in range(1, len(values)):
                if values[i - 1] > 0 and values[i] > 0:
                    change_ratio = values[i] / values[i - 1]
                    if change_ratio < (1 - drop_threshold):
                        sudden_drops.append(
                            {
                                "period": int(periods[i]),
                                "from": float(values[i - 1]),
                                "to": float(values[i]),
                                "drop_pct": round((1 - change_ratio) * 100, 2),
                            }
                        )

        # Проверка на резкий рост
        sudden_growths = []
        if len(values) > 1:
            for i in range(1, len(values)):
                if values[i - 1] > 0 and values[i] > 0:
                    change_ratio = values[i] / values[i - 1]
                    if change_ratio > growth_threshold:
                        sudden_growths.append(
                            {
                                "period": int(periods[i]),
                                "from": float(values[i - 1]),
                                "to": float(values[i]),
                                "growth_pct": round((change_ratio - 1) * 100, 2),
                            }
                        )

        if has_zero_sales:
            groups_with_zero_sales += 1

        if len(sudden_drops) > 0:
            groups_with_sudden_drops += 1

        if len(sudden_growths) > 0:
            groups_with_sudden_growths += 1

        results["groups"][group_name] = {
            "zero_periods": int(zero_periods),
            "total_periods": len(values),
            "has_zero_sales": has_zero_sales,
            "sudden_drops": sudden_drops[:5],
            "sudden_growths": sudden_growths[:5],
            "avg_value": round(float(np.mean(values)), 2),
            "max_value": float(np.max(values)),
            "min_value": float(np.min(values)),
        }

    results["summary"]["total_groups"] = total_groups
    results["summary"]["groups_with_zero_sales"] = groups_with_zero_sales
    results["summary"]["groups_with_sudden_drops"] = groups_with_sudden_drops
    results["summary"]["groups_with_sudden_growths"] = groups_with_sudden_growths

    print(f"Всего групп: {total_groups:,}")
    print(
        f"Групп с нулевыми продажами: {groups_with_zero_sales:,} ({groups_with_zero_sales / total_groups * 100:.2f}%)"
    )
    print(
        f"Групп с резкими падениями: {groups_with_sudden_drops:,} ({groups_with_sudden_drops / total_groups * 100:.2f}%)"
    )
    print(
        f"Групп с резким ростом: {groups_with_sudden_growths:,} ({groups_with_sudden_growths / total_groups * 100:.2f}%)"
    )

    return results
