# -*- coding:utf-8 -*-
_DB_CONN = {
    'default': {'host': '', 'port': 21050, 'user': '', 'password': ''}
    , 'hive': {'host': '', 'port': 10000, 'user': '', 'password': ''}
    , 'airflow': {'host': 'localhost', 'port': 3306, 'user': '', 'password': '', 'db': 'airflow'}
    , 'oracle': {'host': '', 'user': '', '': '', 'db': ''}
    , 'starrocks': {'host': '', 'port': 9030, 'user': '', 'password': '', 'db': ''}
}

# Kafka config
_KAFKA_CONN = {
    'default': {'sasl_mechanism': 'PLAIN', 'security_protocol': 'SASL_PLAINTEXT', 'auto_offset_reset': 'earliest',
                'consumer_timeout_ms': 3000, 'api_version': (1, 0, 0),
                'bootstrap_servers': '',
                'sasl_plain_username': '',
                'sasl_plain_password': ''
                },
    'wydata': {}
}

# starrocks stream load BE connect
_STARROCKS_PARA = {
    'url': 'http://xxx:8040,http://xxx:8040',
    'user': '',
    'password': '',
}


from airflow.common.smartpip import smart_upload, get_dataset, dataset, refresh_dash, ETL_FILE_PATH
from airflow.common.smartpip import run_bash, run_python
from airflow.common.smartpip import run_dataxx, run_datax as _run_datax, run_kettle
from airflow.common.smartpip import run_sql_file as _run_sql_file, point_test as _point_test
from airflow.common.smartpip import hdfsStarrocks as _hdfsStarrocks, kafkaStarrocks as _kafkaStarrocks
import os
workpath = os.path.dirname(os.path.abspath(__file__))

def run_datax(job, para_dict, dev=''):
    return _run_datax(job, _DB_CONN,workpath, para_dict, dev)
def run_sql_file(sql_file, db_connect='starrocks', para_dict=None, dev=''):
    return _run_sql_file(sql_file, _DB_CONN, db_connect, para_dict, dev)
def hdfsStarrocks(job, para_dict=None):
    return _hdfsStarrocks(job, _DB_CONN, para_dict)
def kafkaStarrocks(job, para_dict, dev=''):
    return _kafkaStarrocks(job, _KAFKA_CONN, _STARROCKS_PARA, workpath, para_dict, dev)
def point_test(dagname, sleeptime='', maxtime=''):
    _point_test(dagname, _DB_CONN, sleeptime, maxtime)


