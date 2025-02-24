from utils.config import DB_CONFIG
import pymysql


def querys(sql, params, type="no_select"):
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()
    params = tuple(params)
    cursor.execute(sql, params)
    if type != "no_select":
        data_list = cursor.fetchall()
        if conn:
            cursor.close()
            conn.close()
        return data_list
    else:
        conn.commit()
        if conn:
            cursor.close()
            conn.close()
        return "success"
