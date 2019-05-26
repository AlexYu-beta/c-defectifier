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


def evaluate(task_name):
    """

    :param task_name:
    :return:
    """
    print("=============================================")
    print("Evaluating: {} ...".format(task_name))
    print("Overall:")
    db_origin_path = config_dict["exp_output_path"] + "/" + task_name + "/" + task_name + ".db"
    db_origin = DBConnection(db_origin_path)
    QUERY = QUERY_DEFECTIFY
    item_list = db_origin.execute(QUERY, "").fetchall()
    QUERY_PROBLEMS = QUERY_DEFECTIFY_PROBLEMS
    problem_list = db_origin.execute(QUERY_PROBLEMS, "").fetchall()
    len_item_list = len(item_list)
    len_problem_list = len(problem_list)
    print("- Total number of code sumbissions: {}".format(len_item_list))
    print("- Total number of problems: {}".format(len_problem_list))
    LOC_sum = 0
    LOC_min = 100
    LOC_max = 0
    defect_count = {}
    for item in item_list:
        id, problem_id, submit_id, code, gen_code, annotations, status = item
        LOC = len(gen_code.split("\n"))
        if LOC > LOC_max:
            LOC_max = LOC
        if LOC < LOC_min:
            LOC_min = LOC
        LOC_sum += LOC
        annotations = json.loads(annotations)
        for annotation in annotations.values():
            defect_class = annotation["class"]
            if defect_class in defect_count.keys():
                defect_count[defect_class] += 1
            else:
                defect_count[defect_class] = 1
    print("=============================================")
    print("About Codes:")
    print("- Range of Lines of Codes: {} - {}".format(LOC_min, LOC_max))
    print("- Average Lines of Codes: {}".format(format(LOC_sum/len_item_list, ".4f")))
    print("=============================================")
    print("About Defects:")
    defect_sum = sum(defect_count.values())
    print("- Total Number of Defects: {}".format(defect_sum))
    print("- Total Number of Types of Defects: {}".format(len(defect_count.keys())))
    print("- Number of each type of defects:")
    for k, v in defect_count.items():
        if v > 1:
            print("\t# {}: {} defects, {}%".format(k, v, format(v/defect_sum*100, ".4f")))
        else:
            print("\t# {}: {} defect, {}%".format(k, v, format(v / defect_sum * 100, ".4f")))


if __name__ == '__main__':
    evaluate("comprehensive_db_test")
