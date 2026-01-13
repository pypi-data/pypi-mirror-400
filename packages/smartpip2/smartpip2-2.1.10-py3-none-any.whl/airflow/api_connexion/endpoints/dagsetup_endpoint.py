from flask import request, jsonify

from airflow.api_connexion import security
from airflow.contrib.dagsetup.gen_airflow_dagfile import gen_airflow_dag, rm_airflow_dag, gen_airflow_config, \
    get_etlfile_txt, save_etlfile_txt, save_dataxfile_txt, save_resfile_txt, rm_dataxfile, rm_resfile
from airflow.exceptions import AirflowException
from airflow.security import permissions


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def post_create_dagfile():
    """Create a dag file."""
    params = request.get_json(force=True)
    print(params)
    try:
        msg = gen_airflow_dag(**params)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=msg)


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def get_delete_dagfile():
    """delete the dag."""
    try:
        name = request.args.get('name')
        rm_airflow_dag(name)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=f'success delete dag file {name}')


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def get_gen_dagconfig():
    """generate the dag config base on etl script."""
    try:
        name = request.args.get('name')
        dag_str = gen_airflow_config(name)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=dag_str)


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def post_create_etlfile():
    """save the etl file context."""
    params = request.get_json(force=True)
    print(params)
    try:
        msg = save_etlfile_txt(**params)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=msg)


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def get_gen_etlconfig():
    """get the etl file context."""
    try:
        name = request.args.get('name')
        filename = request.args.get('filename')
        driver = request.args.get('driver')
        etl_dict = get_etlfile_txt(name, filename, driver)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(**etl_dict)


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def post_create_dataxfile():
    """save the datax file context."""
    params = request.get_json(force=True)
    print(params)
    try:
        msg = save_dataxfile_txt(**params)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=msg)

@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def post_create_resfile():
    """save the resource file context."""
    params = request.get_json(force=True)
    print(params)
    try:
        msg = save_resfile_txt(**params)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=msg)

@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def get_delete_resfile():
    """delete the res."""
    try:
        res_id = request.args.get('res_id')
        rm_resfile(res_id)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=f'success delete res {res_id}')


@security.requires_access(
    [
        (permissions.ACTION_CAN_READ, permissions.RESOURCE_DAG),
        (permissions.ACTION_CAN_DELETE, permissions.RESOURCE_DAG_RUN),
    ]
)
def get_delete_dataxfile():
    """delete the datax template"""
    try:
        res_id = request.args.get('res_id')
        tp_id = request.args.get('tp_id')
        rm_dataxfile(res_id, tp_id)
    except AirflowException as err:
        response = jsonify(error="{}".format(err))
        response.status_code = err.status_code
        return response
    else:
        return jsonify(msg=f'success delete res {res_id}, datax tp {tp_id}')
