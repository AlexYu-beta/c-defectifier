import json
from subprocess import *
from utils.fs_util import get_config, get_exp_cfg
from utils.db_util import DBConnection
from utils.sqls import *

config_dict = get_config()


def get_log_info(task_name):
    """

    :param task_name:
    :return:
    """
    log_file = config_dict["log_path"] + "/" + task_name + ".log.json"
    load_dict = {}
    with open(log_file, "r") as f:
        load_dict = json.load(f)
    exp_conf_dir = load_dict["exp_conf_dir"]
    log_list = load_dict["log_list"]
    for log_item in log_list:
        print(log_item)
    print(len([log_item for log_item in log_list if log_item['def_type'] != "nothing"]))


def annotation_test(task_name):
    print("testing annotations...")
    exp_cfg = get_exp_cfg(task_name)
    db_origin_path = config_dict["exp_output_path"] + "/" + task_name + "/" + task_name + ".db"
    left_file = config_dict["exp_output_path"] + "/" + task_name + "/" + "left"
    right_file = config_dict["exp_output_path"] + "/" + task_name + "/" + "right"
    db_origin = DBConnection(db_origin_path)
    QUERY = QUERY_DEFECTIFY
    item_list = db_origin.execute(QUERY, "").fetchall()
    pass_ids = []
    fail_ids = []
    pass_count = 0
    fail_count = 0
    for item in item_list:
        id, problem_id, submit_id, code, gen_code, annotations, status = item
        annotations = json.loads(annotations)



def evaluate(task_name):
    """

    :param task_name:
    :return:
    """

    annotation_test(task_name)


if __name__ == '__main__':
    evaluate("single_db_test")
