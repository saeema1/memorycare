"""
Project package initializer.

Configures PyMySQL as a drop-in replacement for MySQLdb so that
the project can use MySQL on Windows without needing mysqlclient.
"""

# Only import pymysql if not using SQLite
import os
from decouple import config

USE_SQLITE = config('USE_SQLITE', default=False, cast=bool)

if not USE_SQLITE:
    try:
        import pymysql
        pymysql.install_as_MySQLdb()
    except ImportError:
        pass
