# https://dev.mysql.com/doc/connector-python/en/connector-python-example-connecting.html
# https://dev.mysql.com/doc/connector-python/en/connector-python-connectargs.html
# https://dev.mysql.com/doc/connector-python/en/connector-python-example-cursor-select.html
# https://dev.mysql.com/doc/connector-python/en/connector-python-api-mysqlcursor-executemany.html

from typing import Final
import os, inspect, logging
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import errorcode
from niamkeltd_pylib.helpers import debughelper

load_dotenv(dotenv_path=".env")
MYSQL_USERNAME: Final = os.getenv("MYSQL_USERNAME")
MYSQL_PASSWORD: Final = os.getenv("MYSQL_PASSWORD")
MYSQL_HOST: Final = os.getenv("MYSQL_HOST")
MYSQL_PORT: Final = int(os.getenv("MYSQL_PORT", ""))
MYSQL_DATABASE: Final = os.getenv("MYSQL_DATABASE")
MYSQL_TIMEOUT: Final = int(os.getenv("MYSQL_TIMEOUT", ""))

FILE_NAME: Final = debughelper.get_filename()

def initialise_connection():
    logging.info(f"[{FILE_NAME}] establishing connection via: {MYSQL_USERNAME}@{MYSQL_HOST}:{MYSQL_PORT}")
    return mysql.connector.connect(
      user=MYSQL_USERNAME,
      password=MYSQL_PASSWORD,
      host=MYSQL_HOST,
      port=MYSQL_PORT,
      database=MYSQL_DATABASE,
      connection_timeout=MYSQL_TIMEOUT)

def select(query: str, data=(), dictionary:bool = False):
  """
  Execute a select query against the database.

  :param query: The select query to execute.
  :param data: The data to use in the query.
  :param dictionary: Whether to return results as dictionaries.
  :return: The results of the query.
  """

  logging.info(f"[{inspect.stack()[0][3]}] called by [{inspect.stack()[1][3]}]")

  try:
    cnx = initialise_connection()

    try:
      with cnx.cursor(dictionary=dictionary) as cursor:
        result = cursor.execute(query, data)
        all = cursor.fetchall()
        logging.info(f"[{FILE_NAME}] Executed query:\n{query}")
        logging.info(f"[{FILE_NAME}] Provided data: {data}")
        return all

    except Exception as ex:
      logging.error(ex)

    finally:
      cnx.close()

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      logging.error(f"[{FILE_NAME}] Invalid username or password. Error: {err}")
      logging.info(f"[mysql] USERNAME:{MYSQL_USERNAME} HOST:{MYSQL_HOST} PORT:{MYSQL_PORT} DB:{MYSQL_DATABASE}")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      logging.error(f"[{FILE_NAME}] Database does not exist. Error: {err}")
    else:
      logging.error(f"[{FILE_NAME}] Error: {err}")
  except Exception as ex:
    logging.error(ex)

def update(query: str, data=()) -> int:
  logging.info(f"[{inspect.stack()[0][3]}] called by [{inspect.stack()[1][3]}]")
  return insert(query, data)

def insert(query: str, data=()) -> int:
  """
  Insert a record into the database.

  :param query: The insert query to execute.
  :param data: The data to insert.
  :return: The ID of the inserted row, or 0 if the insert failed.
  """

  logging.info(f"[{inspect.stack()[0][3]}] called by [{inspect.stack()[1][3]}]")

  try:
    row_id = 0
    cnx = initialise_connection()

    try:
      with cnx.cursor() as cursor:
        cursor.execute(query, data)

        row_id = cursor.lastrowid

        logging.warning(f"[{FILE_NAME}] Executed query:\n{query}")
        logging.info(f"[{FILE_NAME}] Provided data: {data}")

        cnx.commit()

        logging.info(f"[{FILE_NAME}] Resulting row_id: {row_id}")

    except Exception as ex:
      logging.error(ex)

    finally:
      cnx.close()
      return row_id if isinstance(row_id, int) else 0

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      logging.error(f"[{FILE_NAME}] Invalid username or password. Error: {err}")
      logging.info(f"[mysql] USERNAME:{MYSQL_USERNAME} HOST:{MYSQL_HOST} PORT:{MYSQL_PORT} DB:{MYSQL_DATABASE}")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      logging.error(f"[{FILE_NAME}] Database does not exist. Error: {err}")
    else:
      logging.error(f"[{FILE_NAME}] Error: {err}")
    return 0

  except Exception as ex:
    logging.error(ex)
    return 0

def insert_bulk(query: str, data=()) -> int:
  """
  Insert multiple records into the database.

  :param query: The insert query to execute.
  :param data: The data to insert.
  :return: The ID of the last inserted row, or 0 if the insert failed.
  """

  logging.info(f"[{inspect.stack()[0][3]}] called by [{inspect.stack()[1][3]}]")

  try:
    row_id = 0
    cnx = initialise_connection()

    try:
      with cnx.cursor() as cursor:
        cursor.executemany(query, data)

        row_id = cursor.lastrowid

        logging.warning(f"[{FILE_NAME}] Executed query:\n{query}")
        logging.info(f"[{FILE_NAME}] Provided data: {data}")
        logging.info(f"[{FILE_NAME}] Row: {row_id}")

        cnx.commit()

    except Exception as ex:
      logging.error(ex)

    finally:
      cnx.close()
      return row_id if isinstance(row_id, int) else 0

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      logging.error(f"[{FILE_NAME}] Invalid username or password. Error: {err}")
      logging.info(f"[mysql] USERNAME:{MYSQL_USERNAME} HOST:{MYSQL_HOST} PORT:{MYSQL_PORT} DB:{MYSQL_DATABASE}")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      logging.error(f"[{FILE_NAME}] Database does not exist. Error: {err}")
    else:
      logging.error(f"[{FILE_NAME}] Error: {err}")
    return 0

  except Exception as ex:
    logging.error(ex)
    return 0

def delete(queries: list[str], data=()):
  """
  Execute multiple delete queries against the database.

  :param queries: The delete queries to execute.
  :param data: The data to use in the queries.
  """

  logging.info(f"[{inspect.stack()[0][3]}] called by [{inspect.stack()[1][3]}]")
  try:
    cnx = initialise_connection()

    try:
      with cnx.cursor() as cursor:
        cnx.start_transaction()

        for query in queries:
          cursor.execute(query, data)
          logging.warning(f"[{FILE_NAME}] Executed query:\n{query}")
          logging.info(f"[{FILE_NAME}] Provided data: {data}")

        cnx.commit()

    except mysql.connector.Error as err:
      cnx.rollback()
      logging.error(f"[{FILE_NAME}] Error: {err}")
    finally:
      cursor.close()

  except mysql.connector.Error as err:
    if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
      logging.error(f"[{FILE_NAME}] Invalid username or password. Error: {err}")
      logging.info(f"[mysql] USERNAME:{MYSQL_USERNAME} HOST:{MYSQL_HOST} PORT:{MYSQL_PORT} DB:{MYSQL_DATABASE}")
    elif err.errno == errorcode.ER_BAD_DB_ERROR:
      logging.error(f"[{FILE_NAME}] Database does not exist. Error: {err}")
    else:
      logging.error(f"[{FILE_NAME}] Error: {err}")
  except Exception as ex:
    logging.error(ex)