# -*- coding: utf-8 -*-
import logging
import csv
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta


def create_database(db_name):
    """
    创建数据库。

    :param db_name: SQLite 数据库名称

    :return conn: SQLite 数据库连接对象
    """
    dir = Path(f"./data")
    if not dir.exists():
        dir.mkdir(parents=True, exist_ok=True)
        logging.info(f"目录{dir}创建成功")
    else:
        logging.info(f"目录{dir}已存在")

    db_path = f"{dir}/{db_name}.db"
    conn = sqlite3.connect(db_path)

    return conn


def close_database(conn):
    """关闭数据库"""
    conn.close()


def create_table(conn):
    """
    创建签到记录表（自增ID、签到人员名称、状态、记录创建时间、签到时间）。

    :param conn: SQLite 数据库连接对象
    """
    # 获取当前日期，并格式化为表名（例如：sign_in_records_2023_10_01）
    today = datetime.now().strftime("%Y_%m_%d")
    table_name = f"sign_in_records_{today}"

    cursor = conn.cursor()

    # 检查表是否已经存在
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    if cursor.fetchone() is not None:
        logging.info(f"表 {table_name} 已存在")
        return

    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- 整数类型，主键，自增
            name TEXT NOT NULL, -- 字符串类型，签到人员姓名,不能为空
            status INTEGER NOT NULL, -- 整数类型，签到人员状态（0：未签到，1：签到成功），不能为空
            created_at TEXT NOT NULL, -- 字符串类型，记录创建时间，不能为空
            sign_in_time TEXT NOT NULL, -- 字符串类型，签到人员签到时间，不能为空
            updated_at TEXT NOT NULL -- 字符串类型，签到人员更新时间，不能为空
        )
    ''')
    conn.commit()


def insert_sign_in_record(conn, name, status):
    """
    插入签到记录（名称、状态、记录创建时间）。

    :param conn: SQLite 数据库连接对象
    :param name: 签到人员姓名
    :param status: 签到人员状态（0：未签到；1：已签到）
    """
    # 获取当前日期，并格式化为表名（例如：sign_in_records_2023_10_01）
    today = datetime.now().strftime("%Y_%m_%d")
    table_name = f"sign_in_records_{today}"

    create_table(conn)

    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.cursor()

    # 检查记录是否已存在
    cursor.execute(f"SELECT * FROM {table_name} WHERE name = ?", (name,))
    existing_record = cursor.fetchone()
    if existing_record is None:
        cursor.execute(f'''
            INSERT INTO {table_name} (name,status, created_at, sign_in_time, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, status, time_now, time_now, time_now))
        conn.commit()
        logging.info(f"插入新记录{name}")
    else:
        logging.info(f"记录已存在{name}")


def update_sign_in_record(conn, name, status):
    """
    更新签到记录中的名称和/或签到时间。

    :param conn: SQLite 数据库连接对象
    :param name: 要更新的记录人员姓名
    :param status: 签到人员状态：0：未签到，1：签到成功
    """
    new_sign_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 获取当前日期，并格式化为表名（例如：sign_in_records_2023_10_01）
    today = datetime.now().strftime("%Y_%m_%d")
    table_name = f"sign_in_records_{today}"

    cursor = conn.cursor()

    # 构建更新语句
    update_query = f"UPDATE {table_name} SET "
    update_params = []

    update_query += "sign_in_time = ?, "
    update_params.append(new_sign_in_time)

    update_query += "updated_at = ?, "
    update_params.append(new_sign_in_time)

    update_query += "status = ?, "
    update_params.append(status)

    # 移除最后一个逗号和空格
    update_query = update_query.rstrip(", ")

    # 添加 WHERE 条件
    update_query += " WHERE name = ?"
    update_params.append(name)

    # 执行更新
    cursor.execute(update_query, tuple(update_params))
    conn.commit()
    logging.info(f"{name} 签到记录更新成功")


def query_sign_in_records(conn, status):
    """
    根据签到状态进行数据查询。

    :param conn: SQLite 数据库连接对象
    :param status: 签到人员状态：0：未签到，1：签到成功
    :return records: 返回对应状态列表
    """

    # 获取当前日期，并格式化为表名（例如：sign_in_records_2023_10_01）
    today = datetime.now().strftime("%Y_%m_%d")
    table_name = f"sign_in_records_{today}"

    cursor = conn.cursor()
    # 构建查询语句
    query = f"SELECT * FROM {table_name} WHERE 1=1"
    params = []

    query += " AND status = ?"
    params.append(status)

    # 执行查询
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()

    return records


def update_sign_in_record_with_update_time(conn, name):
    """
    更新签到记录中的名称和/或签到时间。

    :param conn: SQLite 数据库连接对象
    :param name: 要更新的记录人员姓名
    """
    new_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 获取当前日期，并格式化为表名（例如：sign_in_records_2023_10_01）
    today = datetime.now().strftime("%Y_%m_%d")
    table_name = f"sign_in_records_{today}"

    cursor = conn.cursor()

    # 构建更新语句
    update_query = f"UPDATE {table_name} SET "
    update_params = []

    update_query += "updated_at = ?, "
    update_params.append(new_update_time)

    # 移除最后一个逗号和空格
    update_query = update_query.rstrip(", ")

    # 添加 WHERE 条件
    update_query += " WHERE name = ?"
    update_params.append(name)

    # 执行更新
    cursor.execute(update_query, tuple(update_params))
    conn.commit()
    logging.info(f"{name} 签到记录更新时间更新成功")


# 查询某个人的签到记录
def query_sign_in_record(conn, name):
    """
    根据签到人员信息查询签到状态。

    :param conn: SQLite 数据库连接对象
    :param name: 签到人员姓名
    :return status: 人员签到状态: 0：未签到，1：签到成功
    """

    # 获取当前日期，并格式化为表名（例如：sign_in_records_2023_10_01）
    today = datetime.now().strftime("%Y_%m_%d")
    table_name = f"sign_in_records_{today}"

    cursor = conn.cursor()
    # 构建查询语句
    query = f"SELECT * FROM {table_name} WHERE name = ?"
    params = (name,)

    # 执行查询
    cursor.execute(query, params)
    record = cursor.fetchone()

    return record


def insert_csv_data(conn, csv_path):
    """
    读取 CSV 文件，并将第一列数据插入到 SQLite 表中。

    :param conn: SQLite 数据库连接对象
    :param csv_path: CSV 文件路径
    """
    cursor = conn.cursor()

    with open(csv_path, "r", encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name = row[0]  # 获取第一列数据
            insert_sign_in_record(conn, name, 0)

    logging.info("CSV 数据插入成功")
