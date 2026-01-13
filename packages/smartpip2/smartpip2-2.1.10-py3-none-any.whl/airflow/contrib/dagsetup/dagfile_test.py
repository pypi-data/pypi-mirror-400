import requests
import json


def get_header():
    import base64
    name = 'admin'
    pwd = 'admin'
    auth = str(base64.b64encode(f'{name}:{pwd}'.encode('utf-8')), 'utf-8')
    header = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {auth}'
    }
    return header


def t_create_dagfile():
    owner = 'john'
    schedule_interval = '10 08 * * *'
    # schedule_interval = '@once'
    schedule_rate = 'day'  # 每周,每月
    project_name = 'P2'  # which is used as id and file name
    # the job will execute in dag by sequence as listed, first item is to use what driver to execute
    # 数据库及文件类型,文件命名,参数
    job_list = '''
    #hive_sql predict para1,para2
    #impala_sql center
    #hive_sql huli
    #impala_sql test1
    #ktr test para3
    #/diy diy1
    #trigger trigger2  targetdag2
    #/branch  branch1
    #hdfs abcc
    '''
    dag_sequence = '''
center >> test1 >> trigger2
test
    '''
    retries = 5
    dag_remark = 'finance'
    kwargs = {
        'owner': owner,
        'project_name': project_name,
        'schedule_interval': schedule_interval,
        'schedule_rate': schedule_rate,
        'job_list': job_list,
        'tags': 'test1,test2',
        'dag_sequence': dag_sequence,
        'dag_remark': '##dag_remark',
        'description': 'description'
    }
    # gen_airflow_dag(**kwargs)
    # url = 'http://0.0.0.0:8080/api/experimental/create_dagfile?token=jzbuxdr!wkh1_dhknzxhpo1t7no_bw*ar!t$pb5wqncrr4_k3y'
    # response = requests.post(url,data=json.dumps(kwargs),headers={'Content-Type': 'application/json'})
    url = 'http://0.0.0.0:8080/api/v1/create_dagfile'
    # url = 'http://10.10.1.184:8080/api/v1/create_dagfile'
    response = requests.post(url, data=json.dumps(kwargs), headers=get_header())
    print(response.text)


def t_save_etlfile():
    url = 'http://0.0.0.0:8080/api/v1/create_etlfile'
    # url = 'http://10.10.1.184:8080/api/v1/create_dagfile'
    kwargs = {
        'project_name': 't_etlfile',
        'filename': 'p1',
        'driver': 'impala_sql',
        'txt': 'select * from abc'
    }
    response = requests.post(url, data=json.dumps(kwargs), headers=get_header())
    print(response.text)

def t_get_etlfile():
    url = 'http://0.0.0.0:8080/api/v1/gen_etlconfig'
    kwargs = {
        'name': 't_etlfile',
        'filename': 'p1',
        'driver': 'impala_sql'
    }
    response = requests.get(url=url, params=kwargs, headers=get_header())
    print(response.text)


if __name__ == '__main__':
    # t_save_etlfile()
    t_get_etlfile()
