import datetime
import json
import logging
import os

import pymysql

logger = logging.getLogger(__name__)


class MysqlUtil:
    """
    mysql工具类
    """

    def _get_connect(self):
        """
        获取mysql链接
        :return:
        """
        if os.getenv("ENV") == "test":
            host = os.getenv("MYSQL_HOST_TEST")
            port = int(os.getenv("MYSQL_PORT_TEST"))
            user = os.getenv("MYSQL_USER_TEST")
            password = os.getenv("MYSQL_PASSWORD_TEST")
            database = os.getenv("MYSQL_DATABASE_TEST")
        else:
            host = os.getenv("MYSQL_HOST_DEV")
            port = int(os.getenv("MYSQL_PORT_DEV"))
            user = os.getenv("MYSQL_USER_DEV")
            password = os.getenv("MYSQL_PASSWORD_DEV")
            database = os.getenv("MYSQL_DATABASE_DEV")

        conn = pymysql.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database,
        )
        return conn

    """
     连接 MySQL 数据库，执行查询，并将查询结果转化为 Pandas DataFrame 对象。
    :param sql_query: SQL 查询语句
    :param mysql_host: 主机名，默认为 None
    :param port: 端口号，默认为 None
    :param user: 用户名，默认为 None
    :param password: 密码，默认为 None
    :param database: 数据库名称，默认为 None
    :param engine: SQLAlchemy 的数据库引擎对象，默认为 None

    :return: Pandas DataFrame 对象
    """

    # 如果未提供数据库连接引擎，则使用 pymysql 库连接 MySQL 数据库

    def query_mysql(self, sql_query):
        """
        @param: sql_query 查询的sql语句
        @return 查询结果
        """
        # 获得链接
        conn = self._get_connect()
        # 获得游标
        cursor = conn.cursor()
        # 执行 SQL 查询语句
        cursor.execute(sql_query)
        # 获取查询结果
        result = cursor.fetchall()
        # 关闭游标和数据库连接
        cursor.close()
        conn.close()
        return result

    def insert(self, sql: str, params: []):
        conn = self._get_connect()
        cursor = conn.cursor()
        cursor.execute(sql, params)
        data = cursor.fetchall()
        conn.commit()
        cursor.close()
        conn.close()
        return data

    def update_params(self, sql: str, params: []):
        # 获得链接
        conn = self._get_connect()
        # 获得游标
        cursor = conn.cursor()
        # 执行 SQL 查询语句
        cursor.execute(sql, params)
        # 获取查询结果
        result = cursor.fetchall()
        # 将查询结果转化为 Pandas DataFrame 对象
        # df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        conn.commit()
        # 关闭游标和数据库连接
        cursor.close()
        conn.close()
        return result

    def update(self, sql: str):
        # 获得链接
        conn = self._get_connect()
        # 获得游标
        cursor = conn.cursor()
        # 执行 SQL 查询语句
        cursor.execute(sql)
        # 获取查询结果
        result = cursor.fetchall()
        # 将查询结果转化为 Pandas DataFrame 对象
        # df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        conn.commit()
        # 关闭游标和数据库连接
        cursor.close()
        conn.close()
        return result

    def query_mysql_dict(self, sql_query):
        """
        @param: sql_query 查询的sql语句
        @return 查询结果
        """
        # 获得链接
        conn = self._get_connect()
        # 获得游标
        cursor = conn.cursor()
        # 执行 SQL 查询语句
        cursor.execute(sql_query)
        # 获取查询结果
        rows = cursor.fetchall()
        index = cursor.description
        result = []
        for res in rows:
            row = {}
            for i in range(len(index)):
                if isinstance(res[i], datetime.datetime):
                    value = res[i].strftime("%Y-%m-%d %H:%M:%S")
                    row[index[i][0]] = value
                else:
                    row[index[i][0]] = res[i]

            result.append(row)

        # 关闭游标和数据库连接
        cursor.close()
        conn.close()
        return result

    def execute_mysql(self, sql):
        """
        @param: sql_query 查询的sql语句
        @return 查询结果
        """
        # 获得链接
        conn = self._get_connect()
        # 获得游标
        cursor = conn.cursor()
        # 执行 SQL 查询语句
        cursor.execute(sql)
        # 获取查询结果
        result = cursor.fetchall()
        # 将查询结果转化为 Pandas DataFrame 对象
        # df = pd.DataFrame(result, columns=[i[0] for i in cursor.description])
        conn.commit()
        # 关闭游标和数据库连接
        cursor.close()
        conn.close()
        return result

    def get_multiple_tables_column_comments(self, tables, dbname="dap"):
        """
        获取mysql表schema信息

        Args:
            tables 表名称
            dbname 数据库名称

        Return:
            {
              "schema": [
                {
                  "tableName": "table_1",
                  "schema": [
                    {
                      "column": "name",
                      "comment": "姓名"
                    }
                  ]
                }
              ]
            }
        """
        connection = None
        try:
            # 连接数据库
            connection = self._get_connect()
            result_data = {"schema": []}
            with connection.cursor() as cursor:
                for table in tables:
                    # 查询每个表的列信息及注释
                    sql = f"""
                            SELECT COLUMN_NAME AS `column`, COLUMN_COMMENT AS `comment`
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_SCHEMA = '{dbname}' AND TABLE_NAME = '{table}';
                            """
                    cursor.execute(sql)

                    # 获取查询结果并构造字典
                    columns_info = [{"column": col, "comment": comment} for col, comment in cursor.fetchall()]

                    # 将当前表的列信息添加到结果数据中
                    result_data["schema"].append({"tableName": table, "schemaData": columns_info})

            # return json.dumps(result_data, ensure_ascii=False)
            return result_data
        except pymysql.MySQLError as e:
            logger.error(f"get_multiple_tables_column_comments error {e}")
        finally:
            if connection:
                connection.close()

    def query_ex(self, query: str):
        """
        Execute SQL and return column desc and result

        Args:
            query SQL query to run

        Returns:
            Json: {"column":[],result:[]}
        """
        logger.info(f"query_sql: {query}")
        if not query:
            return json.dumps({"column": [], "result": []})

        connection = None
        try:
            connection = self._get_connect()
            with connection.cursor() as cursor:
                # 执行SQL查询
                cursor.execute(query)
                # 获取查询结果的字段名称
                column_names = [desc[0] for desc in cursor.description]
                # 获取查询结果
                rows = cursor.fetchall()

                # 将查询结果转换为指定格式
                result = []
                index = cursor.description
                for res in rows:
                    row = {}
                    for i in range(len(index)):
                        if isinstance(res[i], datetime.datetime):
                            value = res[i].strftime("%Y-%m-%d %H:%M:%S")
                            row[index[i][0]] = value
                        else:
                            row[index[i][0]] = res[i]
                    result.append(row)

                    # return json.dumps({"column": column_names, "result": result})
                return {"column": column_names, "result": result}
        except pymysql.MySQLError as e:
            logger.error(f"query_ex error query_sql: {query},{e}")
            return None
        finally:
            if connection:
                connection.close()
