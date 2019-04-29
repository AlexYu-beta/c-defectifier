import json
from utils.fs_util import get_config

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


def evaluate(task_name):
    """

    :param task_name:
    :return:
    """
    get_log_info(task_name)


if __name__ == '__main__':
    evaluate("db_test")
