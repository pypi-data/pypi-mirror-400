import numpy as np


def check_missing_values(df, name="Dataset"):
    """
    Проверяет пропущенные значения в датафрейме

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    name : str
        Название датасета для вывода

    Returns:
    --------
    pd.Series
        Series с количеством пропущенных значений по столбцам
    """
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print(f"{name}: Найдены пропущенные значения:")
        print(missing[missing > 0])
    else:
        print(f"{name}: Пропущенных значений нет")
    return missing


def print_numeric_stats(series, name="Значение", decimals=2):
    """
    Выводит статистику по числовому столбцу

    Parameters:
    -----------
    series : pd.Series
        Числовой столбец для анализа
    name : str
        Название столбца для вывода
    decimals : int
        Количество знаков после запятой
    """
    print(f"\nСтатистика по {name}:")
    print(f"Минимальное: {series.min():.{decimals}f}")
    print(f"Максимальное: {series.max():.{decimals}f}")
    print(f"Среднее: {series.mean():.{decimals}f}")
    print(f"Медианное: {series.median():.{decimals}f}")
    print(f"Стандартное отклонение: {series.std():.{decimals}f}")

    quantiles = series.quantile([0.25, 0.5, 0.75, 0.95, 0.99])
    print("\nКвантили:")
    for q, val in quantiles.items():
        print(f"{int(q * 100)}% перцентиль: {val:.{decimals}f}")


def check_anomalies(series, name="Значение", thresholds=None):
    """
    Проверяет аномалии в числовом столбце

    Parameters:
    -----------
    series : pd.Series
        Числовой столбец для проверки
    name : str
        Название столбца для вывода
    thresholds : dict, optional
        Словарь с порогами для проверки, например:
        {'<= 0': 0, '> 100000': 100000}

    Returns:
    --------
    dict
        Словарь с результатами проверки
    """
    if thresholds is None:
        thresholds = {"<= 0": 0}

    results = {}
    total = len(series)

    print(f"\nПроверка на аномалии ({name}):")
    for label, threshold in thresholds.items():
        if ">=" in label or ">" in label:
            count = (series > threshold).sum()
        elif "<=" in label or "<" in label:
            count = (series <= threshold).sum()
        else:
            count = (series == threshold).sum()

        percentage = count / total * 100 if total > 0 else 0
        print(f"{label}: {count:,} ({percentage:.2f}%)")
        results[label] = {"count": count, "percentage": percentage}

    return results


def check_id_uniqueness(df, id_column, name="Dataset"):
    """
    Проверяет уникальность ID в датафрейме

    Parameters:
    -----------
    df : pd.DataFrame
        Датафрейм для проверки
    id_column : str
        Название столбца с ID
    name : str
        Название датасета для вывода

    Returns:
    --------
    bool
        True если все ID уникальны, False иначе
    """
    unique_count = df[id_column].nunique()
    total_count = len(df)

    print(f"\nПроверка уникальности {id_column} ({name}):")
    print(f"Уникальных {id_column}: {unique_count:,}")
    print(f"Всего записей: {total_count:,}")

    if unique_count == total_count:
        print(f"Все {id_column} уникальны")
        return True
    else:
        print("Несоответствие количества")
        return False


def check_datasets_overlap(
    df1,
    id_column1,
    df2,
    id_column2,
    name1="Dataset 1",
    name2="Dataset 2",
    return_sets=True,
):
    """
    Проверяет пересечение ID между двумя датафреймами

    Parameters:
    -----------
    df1 : pd.DataFrame
        Первый датафрейм
    id_column1 : str
        Название столбца с ID в первом датафрейме
    df2 : pd.DataFrame
        Второй датафрейм
    id_column2 : str
        Название столбца с ID во втором датафрейме
    name1 : str
        Название первого датасета
    name2 : str
        Название второго датасета
    return_sets : bool
        Если True, возвращает множества индексов. Если False, возвращает только длины.

    Returns:
    --------
    dict
        Словарь с результатами проверки
    """
    ids1 = set(df1[id_column1].unique())
    ids2 = set(df2[id_column2].unique())

    overlap = ids1 & ids2
    only_in_1 = ids1 - ids2
    only_in_2 = ids2 - ids1

    print(f"\nСоответствие между {name1} и {name2}:")
    print(f"{name1}: {len(ids1):,} уникальных {id_column1}")
    print(f"{name2}: {len(ids2):,} уникальных {id_column2}")
    print(f"Пересечение: {len(overlap):,}")
    print(f"Только в {name1}: {len(only_in_1):,}")
    print(f"Только в {name2}: {len(only_in_2):,}")

    if len(only_in_2) > 0:
        print(f"{len(only_in_2)} элементов из {name2} отсутствуют в {name1}")
    else:
        print(f"Все элементы из {name2} присутствуют в {name1}")

    if return_sets:
        return {
            "ids1": ids1,
            "ids2": ids2,
            "overlap": overlap,
            "only_in_1": only_in_1,
            "only_in_2": only_in_2,
            "overlap_count": len(overlap),
        }
    else:
        return {
            "ids1_count": len(ids1),
            "ids2_count": len(ids2),
            "overlap_count": len(overlap),
            "only_in_1_count": len(only_in_1),
            "only_in_2_count": len(only_in_2),
        }


def create_histogram(
    ax,
    data,
    bins=50,
    title="",
    xlabel="",
    ylabel="Частота",
    color="steelblue",
    show_mean=True,
    show_median=False,
    xlim=None,
    log_scale=False,
):
    """
    Создает гистограмму с настройками

    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Ось для построения графика
    data : array-like
        Данные для гистограммы
    bins : int
        Количество бинов
    title : str
        Заголовок графика
    xlabel : str
        Подпись оси X
    ylabel : str
        Подпись оси Y
    color : str
        Цвет гистограммы
    show_mean : bool
        Показывать ли среднее значение
    show_median : bool
        Показывать ли медиану
    xlim : tuple, optional
        Ограничения по оси X (min, max)
    log_scale : bool
        Использовать ли логарифмическую шкалу
    """
    if log_scale:
        data = np.log1p(data)

    ax.hist(data, bins=bins, edgecolor="black", alpha=0.7, color=color)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    if show_mean:
        mean_val = np.mean(data) if not log_scale else np.mean(np.log1p(data))
        ax.axvline(
            mean_val, color="red", linestyle="--", label=f"Среднее: {mean_val:.1f}"
        )

    if show_median:
        median_val = np.median(data) if not log_scale else np.median(np.log1p(data))
        ax.axvline(
            median_val,
            color="green",
            linestyle="--",
            label=f"Медиана: {median_val:.1f}",
        )

    if show_mean or show_median:
        ax.legend()

    if xlim:
        ax.set_xlim(xlim)


def create_boxplot(
    ax,
    data,
    title="",
    ylabel="",
    show_fliers=False,
    color="lightblue",
    vert=True,
    patch_artist=True,
):
    """
    Создает boxplot с настройками

    Parameters:
    -----------
    ax : matplotlib.axes.Axes
        Ось для построения графика
    data : array-like
        Данные для boxplot
    title : str
        Заголовок графика
    ylabel : str
        Подпись оси Y
    show_fliers : bool
        Показывать ли выбросы
    color : str
        Цвет заливки коробки
    vert : bool
        Вертикальная ориентация
    patch_artist : bool
        Включить заливку коробки
    """
    bp = ax.boxplot(data, vert=vert, showfliers=show_fliers, patch_artist=patch_artist)
    if patch_artist:
        bp["boxes"][0].set_facecolor(color)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if vert:
        ax.set_xticklabels([""])
    ax.grid(True, alpha=0.3, axis="y" if vert else "x")


def print_top_n(series, n=10, name="элементов", show_percentage=False, total=None):
    """
    Выводит топ-N элементов

    Parameters:
    -----------
    series : pd.Series
        Series с подсчетами
    n : int
        Количество элементов для вывода
    name : str
        Название элементов
    show_percentage : bool
        Показывать ли процент
    total : int, optional
        Общее количество для расчета процента
    """
    top = series.head(n)
    print(f"\nТоп-{n} {name}:")
    for idx, (key, value) in enumerate(top.items(), 1):
        if show_percentage and total:
            pct = value / total * 100
            print(f"{idx}. {key}: {value:,} ({pct:.1f}%)")
        else:
            print(f"{idx}. {key}: {value:,}")
