import pymysql

pymysql.version_info = (1, 3, 13, "final", 0)
pymysql.install_as_MySQLdb()

default_app_config = 'api.apps.ApiConfig'
