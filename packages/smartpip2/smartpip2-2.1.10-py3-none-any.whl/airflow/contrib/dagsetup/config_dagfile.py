# -*- coding:utf-8 -*-
import_format = '''# -*- coding:utf-8 -*-
import os
import sys
import datetime
import airflow
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.bash import BashOperator
from airflow import DAG
from airflow.models import Variable
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))

from common{common_path}.functions import *

dev=''
retry_delay_minutes = 3
'''

param_format = '''
# get your param from airflow web
{param} = Variable.get('{param}')
'''

break_point = '''
#airflow_break_point
def S_break_point():
    return 'success'
'''

execute_python_format = '''
def S_{filename}():
    job = os.path.join(ETL_FILE_PATH, '{project_name}/{filename}.py')
    run_python(job,{param},dev=dev)
'''

execute_python_bash_format = '''
def S_{filename}():
    job = os.path.join(ETL_FILE_PATH ,'{project_name}/{filename}.py')
    return 'python %s %s'%(job,{param})
'''

execute_dataxx_format = '''
def S_{filename}():
    job = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.json')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_dataxx(job,para_dict,dev=dev)
'''

execute_datax_format = '''
def S_{filename}():
    job = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_datax(job, para_dict, dev=dev)
'''

execute_flinkcdc_format = '''
def S_{filename}():
    job = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_flinkcdc(job, para_dict, dev=dev)
'''

execute_kafkastarrocks_format = '''
def S_{filename}():
    job = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    kafkaStarrocks(job, para_dict, dev=dev)
'''

execute_apistarrocks_format = '''
def S_{filename}():
    job = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    apiStarrocks(job, para_dict)
'''

execute_ktr_format = '''
# execute kettle transform
def S_{filename}():
    job=os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.ktr')
    run_kettle(job,{param_str},dev=dev)
'''

execute_kjb_format = '''
# execute kettle job
def S_{filename}():
    job=os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.kjb')
    run_kettle(job,{param_str},dev=dev)
'''

execute_ktr_r_format = '''
# execute kettle transform
def S_{filename}():
    job=os.path.join(ETL_FILE_PATH_R , '{project_name}/{filename}.ktr')
    run_kettle_remote(job,{param_str},dev=dev)
'''

execute_kjb_r_format = '''
# execute kettle job
def S_{filename}():
    job=os.path.join(ETL_FILE_PATH_R , '{project_name}/{filename}.kjb')
    run_kettle_remote(job,{param_str},dev=dev)
'''

execute_hdfs_format = '''
# execute kettle with hdfs job
def S_{filename}():
    job=os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.ktr')
    run_kettle(job,{param_str},dev=dev)
    load_hive(job)
'''

execute_sql_format = '''
# execute db sql script
def S_{filename}():
    path = os.path.join(ETL_FILE_PATH ,'{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_sql_file(path,'{db}',para_dict,dev=dev)
'''
execute_sqlstr_format = '''
# execute db sql script
def S_{filename}():
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_sql_str({remark},'{db}',para_dict,dev=dev)
'''

execute_sp_format = '''
# execute db procedure
def S_{filename}():
    run_sp('{filename}',[{param}],dev=dev)
'''

execute_sqoop_format = '''
# execute sqoop script
def S_{filename}():
    path = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_sqoop(path, para_dict)
'''

execute_hdfsstarrocks_format = '''
# execute starrocks script
def S_{filename}():
    path = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    hdfsStarrocks(path, para_dict)
'''

execute_sap_format = '''
# execute sap rfc script
def S_{filename}():
    path = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.json')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    run_rfc(path, para_dict)
'''

param_str_format = ''' ' "-param:{item_param}={{}}"'.format({item_param}) '''

dag_import_format = '''# -*- coding:utf-8 -*-
import os
import sys
pathname = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, pathname)
sys.path.insert(0, os.path.abspath(os.path.join(pathname, '..')))
from etl_script.{project_name} import *
'''

dag_config_format = '''
# dag config
args = {{
    'owner': '{owner}',
    'start_date': airflow.utils.dates.days_ago({days_ago}),
    'retries': {retries},
    'retry_delay_minutes': retry_delay_minutes,
    {extra_args}
}}
dag = DAG(
    dag_id='{project_name}',
    tags={tags},
    default_args=args,
    schedule_interval='{schedule_interval}',
    catchup=False,
    description = """{description}"""
)
dag.doc_md = """{dag_remark}"""
'''

dag_jobs_format = '''
{filename} = PythonOperator(
    task_id='{filename}',
    python_callable=S_{filename},
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''

dag_jobs_format_bash = '''
{filename} = BashOperator(
    task_id='{filename}',
    bash_command=S_{filename}(),
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''

dag_jobs_format_branch = '''
{filename} = BranchPythonOperator(
    task_id='{filename}',
    python_callable={funname},
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''


dag_jobs_format_diy = '''
{filename} = PythonOperator(
    task_id='{filename}',
    python_callable={funname},
    provide_context = True,
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''

dag_jobs_format_trigger = '''
{filename} = TriggerDagRunOperator(
    task_id='{filename}',
    trigger_dag_id='{trigger_dag_id}',
    dag=dag
)
{filename}.ui_color = '{color}'
{filename}.driver = '{driver}'
'''

dag_jobs_format_queue = '''
{filename}.queue = 'bg'
'''

# breaking_point
execute_point_format = '''
# decide Continue or terminate
def S_{dagname}():
    point_test('{dagname}','{sleeptime}','{maxtime}')
'''

# check data
execute_validate_format = '''
# execute validate script
def S_{filename}():
    path = os.path.join(ETL_FILE_PATH , '{project_name}/{filename}.sql')
    para_dict = dict(zip('{param}'.split(','),[{param}]))
    validate(path,'{db}',para_dict,dev=dev)
'''

# check dataset
execute_dataset_format = '''
# execute dataset script
def S_{filename}():
    dataset('{filename}','{param}','{remark}',{tolist})
'''
# check starrocks routine job
execute_routinestarrocks_format = '''
def S_{filename}():
    routineStarrocks('{label}','{flag}')
'''

# refresh dashboard
execute_dash_format = '''
def S_{filename}():
    refresh_dash('{filename}','{param}')
'''

# execute quality script
execute_quality_format = '''
def S_{filename}():
    refresh_quality('{filename}','{param}')
'''


# send mail
execute_mail_format = '''
def S_{filename}():
    dash_mail('{filename}',{ds_fun},{tolist})
'''

# refresh tableau source script
refresh_tableau_format = '''
def S_{filename}():
    refreshTableauSource({sourceID})
'''
