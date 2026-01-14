import json
import logging
from typing import Any, Iterable, Optional
from typing import List, Optional, Union
import pandas as pd
import vertica_python
from mnemosynecore.vault import get_secret
from airflow.operators.python import get_current_context
from airflow import DAG
from airflow.utils.task_group import TaskGroup
from airflow.operators.dummy import DummyOperator
from os import listdir, path


def load_sql_tasks_from_dir(dir_sql: str, vertica_conn_id: str):
    """
    Создаёт словарь VerticaOperator из всех SQL файлов в папке,
    автоматически используя текущий DAG из контекста.
    """
    from o3_vertica.airflow.operator import VerticaOperator

    context = get_current_context()
    dag = context['dag']  # берём текущий DAG

    tasks = {}
    files_list = listdir(dir_sql)
    for filename in files_list:
        if not filename.endswith(".sql"):
            continue
        path_file = path.join(dir_sql, filename)
        sql = read_sql_file(path_file)
        if sql:
            sql_statements = sql.split(';')
            task_name = 'task_' + filename.replace('.sql', '_vertica')
            tasks[task_name] = VerticaOperator(
                sql=sql_statements,
                task_id=task_name,
                vertica_conn_id=vertica_conn_id,
                dag=dag,
            )
    return tasks

def read_sql_file(file_path: str):
    if not path.exists(file_path):
        print('Error: no file ' + file_path)
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def vertica_dedupe(
    table_name: str,
    unique_keys: Union[str, List[str]],
    conn: Optional[vertica_python.Connection] = None,
    conn_id: Optional[str] = None,
    date_col: Optional[str] = None,
    keep: str = "last",
    commit: bool = True
):
    """
    Удаляет дубликаты из таблицы Vertica, оставляя только уникальные строки.

    Args:
        table_name: Полное имя таблицы (schema.table)
        unique_keys: Столбец или список столбцов для уникальности
        conn: Готовое соединение с Vertica
        conn_id: ID подключения/секрета (если conn не передан)
        date_col: Столбец с датой для определения последней строки при дубликатах
        keep: 'last' или 'first' — какая запись остаётся среди дубликатов
        commit: Выполнить commit после удаления
    """

    if isinstance(unique_keys, str):
        unique_keys = [unique_keys]

    close_conn = False
    if conn is None:
        if not conn_id:
            raise ValueError("Нужно указать conn или conn_id")
        conn = vertica_conn(conn_id)
        close_conn = True

    # Выбираем строки, которые нужно оставить
    order_clause = f"ORDER BY {date_col} DESC" if date_col and keep == "last" else ""
    unique_cols = ", ".join(unique_keys)

    dedupe_sql = f"""
        DELETE FROM {table_name} t
        USING (
            SELECT {unique_cols}, ROW_NUMBER() OVER (PARTITION BY {unique_cols} {order_clause}) AS rn
            FROM {table_name}
        ) x
        WHERE t.{unique_keys[0]} = x.{unique_keys[0]}
          AND x.rn > 1
    """

    vertica_sql(conn=conn, sql=dedupe_sql, commit=commit)

    if close_conn:
        conn.close()

    print(f"Удаление дубликатов из {table_name} завершено по ключам: {unique_keys}")


def vertica_upsert(
    df: pd.DataFrame,
    table_name: str,
    unique_keys: Union[str, List[str]],
    conn=None,
    date_col: Optional[str] = None,
    days_back: Optional[int] = None,
    commit: bool = True
):
    """
    Эффективно обновляет данные в Vertica:
    - вставляет новые строки,
    - обновляет существующие,
    - удаляет дубликаты.

    Args:
        df: DataFrame с новыми данными
        table_name: имя таблицы с полным путем (schema.table)
        unique_keys: столбец или список столбцов для уникальности
        conn: подключение к Vertica (если None, создается новое)
        date_col: если указано, фильтруем по последним `days_back` дням
        days_back: число дней для подгрузки (используется с date_col)
        commit: выполнять commit после вставки/мержа
    """
    if df.empty:
        print("Нет данных для обновления.")
        return

    if isinstance(unique_keys, str):
        unique_keys = [unique_keys]

    # Создаем соединение, если не передано
    close_conn = False
    if conn is None:
        conn = vertica_conn()
        close_conn = True

    # Создаем временную таблицу
    temp_table = f"{table_name}_tmp"
    create_temp_sql = f"""
        DROP TABLE IF EXISTS {temp_table};
        CREATE LOCAL TEMP TABLE {temp_table} AS
        SELECT * FROM {table_name} WHERE 1=0;
    """
    vertica_sql(conn, create_temp_sql, commit=False)

    # Вставляем данные во временную таблицу
    rows = [tuple(x) for x in df.to_numpy()]
    cols = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))

    insert_sql = f"INSERT INTO {temp_table} ({cols}) VALUES ({placeholders})"
    vertica_sql(conn, insert_sql, params=rows, many=True, commit=False)

    # Удаляем старые данные по date_col, если указано
    if date_col and days_back:
        delete_sql = f"""
            DELETE FROM {table_name}
            WHERE {date_col} >= CURRENT_DATE - INTERVAL '{days_back} day';
        """
        vertica_sql(conn, delete_sql, commit=False)

    # MERGE с основной таблицей по уникальным ключам
    merge_conditions = " AND ".join([f"t.{k} = s.{k}" for k in unique_keys])
    update_assignments = ", ".join([f"{c} = s.{c}" for c in df.columns if c not in unique_keys])

    merge_sql = f"""
        MERGE INTO {table_name} t
        USING {temp_table} s
        ON {merge_conditions}
        WHEN MATCHED THEN UPDATE SET {update_assignments}
        WHEN NOT MATCHED THEN INSERT ({cols}) VALUES ({cols});
    """
    vertica_sql(conn, merge_sql, commit=False)

    # Финальный commit
    if commit:
        conn.commit()

    if close_conn:
        conn.close()

    print(f"Обновление таблицы {table_name} завершено. {len(df)} строк обработано.")

    """
        Пример использования:
        vertica_upsert(
            df=df_new,
            table_name="schema.table",
            unique_keys=["id", "add_column"],
            conn=conn,
            date_col="date_column",
            days_back=3
        )
    """


def vertica_conn(conn_id: str) -> vertica_python.Connection:
    """
    Создаёт подключение к Vertica через Vault / Airflow Connection.

    :param conn_id: ID секрета (Vault / Airflow)
    """
    cfg = get_secret(conn_id)

    return vertica_python.connect(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["login"],
        password=cfg["password"],
        database=cfg.get("schema") or cfg.get("database"),
        autocommit=False,
    )


def vertica_sql(
    *,
    conn_id: Optional[str] = None,
    conn: Optional[vertica_python.Connection] = None,
    sql: str,
    params: Optional[Iterable[Any]] = None,
    many: bool = False,
    commit: bool = True,
) -> None:
    """
    Выполняет SQL-запрос в Vertica.

    Можно передать либо conn_id, либо готовое соединение.
    """

    if not conn and not conn_id:
        raise ValueError("Нужно указать conn или conn_id")

    close_conn = False
    if not conn:
        conn = vertica_conn(conn_id)
        close_conn = True

    try:
        with conn.cursor() as cur:
            if many:
                cur.executemany(sql, params)
            else:
                cur.execute(sql, params)

        if commit:
            conn.commit()

    except Exception:
        conn.rollback()
        logging.exception("Ошибка выполнения SQL в Vertica")
        raise

    finally:
        if close_conn:
            conn.close()

def vertica_select(
    *,
    conn_id: Optional[str] = None,
    conn: Optional[vertica_python.Connection] = None,
    sql: str,
    params: Optional[Iterable[Any]] = None,
) -> pd.DataFrame:
    """
    Выполняет SELECT-запрос и возвращает pandas DataFrame.
    """

    if not conn and not conn_id:
        raise ValueError("Нужно указать conn или conn_id")

    close_conn = False
    if not conn:
        conn = vertica_conn(conn_id)
        close_conn = True

    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            columns = [desc[0] for desc in cur.description]
            rows = cur.fetchall()

        return pd.DataFrame(rows, columns=columns)

    finally:
        if close_conn:
            conn.close()
