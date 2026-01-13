from airflow.contrib.dagsetup.gen_airflow_dagfile import gen_airflow_dag,rm_airflow_dag,gen_airflow_config

def gen_dag_file(*args,**kwargs):
    '''generate the dags and script'''
    gen_airflow_dag(*args,**kwargs)

def rm_dag_file(name):
    rm_airflow_dag(name)

def gen_dag_config(name):
    return gen_airflow_config(name)
