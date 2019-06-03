import json
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


def evaluate_primitive_dataset_ok():
    """

    :return:
    """
    db_origin_path = config_dict["dataset_path"] + "/c_data_ok.db"
    db_origin = DBConnection(db_origin_path)
    QUERY = QUERY_ALL
    item_list = db_origin.execute(QUERY, "").fetchall()
    len_item_list = len(item_list)
    print("===============================================================")
    print("About correct codes:")
    print("- Total number of correct code submissions: {}".format(len_item_list))
    QUERY_PROBLEMS = QUERY_SUBMIT_PROBLEMS
    problem_list = db_origin.execute(QUERY_PROBLEMS, "").fetchall()
    len_problem_list = len(problem_list)
    print("- Total number of problems: {}".format(len_problem_list))
    QUERY_USERS = QUERY_SUBMIT_USERS
    user_list = db_origin.execute(QUERY_USERS, "").fetchall()
    len_user_list = len(user_list)
    print("- Total number of users: {}".format(len_user_list))
    QUERY_USERS_PROBLEMS = QUERY_SUBMIT_USERS_PROBLEMS
    user_problem_list = db_origin.execute(QUERY_USERS_PROBLEMS, "").fetchall()
    len_user_problem_list = len(user_problem_list)
    print("- Total number of unique user-problem pair: {}".format(len_user_problem_list))
    repetition_rate= (len_item_list - len_user_problem_list)/len_item_list * 100
    print("- Repetition rate of submissions by user-problem pair: {}%".format(format(repetition_rate, '.4f')))


def evaluate_primitive_dataset_wrong():
    """

    :return:
    """
    db_origin_path = config_dict["dataset_path"] + "/c_data.db"
    db_origin = DBConnection(db_origin_path)
    QUERY = QUERY_WRONG_SUBMIT
    item_list = db_origin.execute(QUERY, "").fetchall()
    len_item_list = len(item_list)
    print("===============================================================")
    print("About wrong codes:")
    print("- Total number of wrong code submissions: {}".format(len_item_list))
    QUERY_PROBLEMS = QUERY_WRONG_SUBMIT_PROBLEMS
    problem_list = db_origin.execute(QUERY_PROBLEMS, "").fetchall()
    len_problem_list = len(problem_list)
    print("- Total number of problems: {}".format(len_problem_list))
    QUERY_USERS = QUERY_WRONG_SUBMIT_USERS
    user_list = db_origin.execute(QUERY_USERS, "").fetchall()
    len_user_list = len(user_list)
    print("- Total number of users: {}".format(len_user_list))
    QUERY_USERS_PROBLEMS = QUERY_WRONG_SUBMIT_USERS_PROBLEMS
    user_problem_list = db_origin.execute(QUERY_USERS_PROBLEMS, "").fetchall()
    len_user_problem_list = len(user_problem_list)
    print("- Total number of unique user-problem pair: {}".format(len_user_problem_list))
    repetition_rate= (len_item_list - len_user_problem_list)/len_item_list * 100
    print("- Repetition rate of submissions by user-problem pair: {}%".format(format(repetition_rate, '.4f')))


def evaluate_primitive_dataset():
    """

    :return:
    """
    db_origin_path = config_dict["dataset_path"] + "/c_data.db"
    db_origin = DBConnection(db_origin_path)
    QUERY = QUERY_ALL
    item_list = db_origin.execute(QUERY, "").fetchall()
    len_item_list = len(item_list)
    print("===============================================================")
    print("Evaluating: primitive dataset ...")
    print("Overall:")
    print("- Total number of code submissions: {}".format(len_item_list))
    QUERY_PROBLEMS = QUERY_SUBMIT_PROBLEMS
    problem_list = db_origin.execute(QUERY_PROBLEMS, "").fetchall()
    len_problem_list = len(problem_list)
    print("- Total number of problems: {}".format(len_problem_list))
    QUERY_USERS = QUERY_SUBMIT_USERS
    user_list = db_origin.execute(QUERY_USERS, "").fetchall()
    len_user_list = len(user_list)
    print("- Total number of users: {}".format(len_user_list))
    evaluate_primitive_dataset_ok()
    evaluate_primitive_dataset_wrong()
    print("===============================================================")


def evaluate_c_def(task_name):
    """

    :param task_name:
    :return:
    """
    print("===============================================================")
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
    print("- Total number of code submissions: {}".format(len_item_list))
    print("- Total number of problems: {}".format(len_problem_list))
    LOCs = []
    LOC_sum = 0
    LOC_min = 100
    LOC_max = 0
    defect_count = {}
    token_change_count = 0
    for item in item_list:
        id, problem_id, submit_id, code, gen_code, annotations, status = item
        LOC = len(gen_code.split("\n"))
        LOCs.append(LOC)
        TOK = len(code)
        TOK_gen = len(gen_code)
        if LOC > LOC_max:
            LOC_max = LOC
        if LOC < LOC_min:
            LOC_min = LOC
        LOC_sum += LOC
        annotations = json.loads(annotations)
        """
        warning: count of token change is approximate
        """
        for annotation in annotations.values():
            defect_class = annotation["class"]
            if defect_class in defect_count.keys():
                defect_count[defect_class] += 1
            else:
                defect_count[defect_class] = 1
            if defect_class in {"STYP", "DCCR_to_const", "DCCR_to_var", "DRWV", "SRIF_replace_var",
                                "DCCA", "DRVA_to_const", "DRVA_to_var", "ORRN"}:
                token_change_count += 1
            elif defect_class in {"OFPO"}:
                token_change_count += 2
            elif defect_class in {"OILN_negate_cond"}:
                token_change_count += 3
            elif defect_class in {"SRIF_to_expr", "OAIS_add_op", "OAIS_del_op", "SRIF_wrap_func_call",
                                  "SRIF_unwrap_func_call"}:
                token_change_count += 4
            elif defect_class in {"OILN_add_or", "OILN_add_and", "OILN_del_or", "OILN_del_and"}:
                token_change_count += 6
            elif defect_class in {"SMOV"}:
                token_change_count += int((TOK + TOK_gen)/LOC)
            elif defect_class in {"SDFN"}:
                token_change_count += int(TOK/LOC)
            else:
                print(defect_class)

    print("===============================================================")
    print("About Codes:")
    print("- Range of Lines of Codes: {} - {}".format(LOC_min, LOC_max))
    print("- Average Lines of Codes: {}".format(format(LOC_sum/len_item_list, ".4f")))

    def get_median(data):
        data = sorted(data)
        size = len(data)
        if size % 2 == 0:
            median = (data[size // 2] + data[size // 2 - 1]) / 2
            data[0] = median
        if size % 2 == 1:
            median = data[(size - 1) // 2]
            data[0] = median
        return data[0]

    med = get_median(LOCs)
    print("- Median of Lines of Codes: {}".format(med))
    print("===============================================================")
    print("About Defects:")
    defect_sum = sum(defect_count.values())
    print("- Total Number of Defects: {}".format(defect_sum))
    print("- Total Number of Types of Defects: {}".format(len(defect_count.keys())))
    print("- Total Number of tokens changed: {}".format(token_change_count))
    print("- Average Number of tokens changed per file: {}".format(format(token_change_count/len_item_list, ".4f")))
    print("- Average Number of tokens changed per defect: {}".format(format(token_change_count/defect_sum, ".4f")))
    count_controw_flow = 0
    count_function_call = 0
    count_type_change = 0
    count_statement_move = 0
    count_arithmetic_operator = 0
    count_const = 0
    count_variant = 0
    count_array = 0
    count_statement = 0
    count_operator = 0
    count_operand = 0
    for k, v in defect_count.items():
        if k in {"SRIF_replace_var", "SRIF_to_expr", "SRIF_wrap_func_call", "SRIF_unwrap_func_call", "ORRN", "OILN_add_and", "OILN_add_or", "OILN_del_and", "OILN_del_or", "OILN_negate_cond"}:
            count_controw_flow += v
        if k in {"SRIF_wrap_func_call", "SRIF_unwrap_func_call", "SDFN", "OFPO"}:
            count_function_call += v
        if k in {"STYP", "DCCA"}:
            count_type_change += v
        if k in {"SMOV"}:
            count_statement_move += v
        if k in {"OAIS_add_op", "OAIS_del_op"}:
            count_arithmetic_operator += v
        if k in {"DCCR_to_const", "DCCR_to_var", "DCCA"}:
            count_const += v
        if k in {"DRVA_to_const", "DRVA_to_var", "SRIF_replace_var", "DRWV"}:
            count_variant += v
        if k in {"DCCA"}:
            count_array += v
        if k in {"SRIF_replace_var", "SRIF_to_expr", "SRIF_wrap_func_call", "SRIF_unwrap_func_call",
                 "SDFN", "STYP", "SMOV"}:
            count_statement += v
        if k in {"ORRN", "OILN_add_and", "OILN_add_or", "OILN_del_and", "OILN_del_or", "OILN_negate_cond",
                 "OAIS_add_op", "OAIS_del_op", "OFPO"}:
            count_operator += v
        if k in {"DCCR_to_const", "DCCR_to_var", "DRVA_to_const", "DRVA_to_var", "DRWV", "DCCA"}:
            count_operand += v

    print("- Number of each classification of defects:")
    print("\t# {}: {} defects, {}%".format("control flow related", count_controw_flow,
                                           format(count_controw_flow / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("function call related", count_function_call,
                                           format(count_function_call / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("type-change related", count_type_change,
                                           format(count_type_change / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("statement-move related", count_statement_move,
                                           format(count_statement_move / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("arithmetic-operator related", count_arithmetic_operator,
                                           format(count_arithmetic_operator / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("const related", count_const,
                                           format(count_const / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("variant related", count_variant,
                                           format(count_variant / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("array related", count_array,
                                           format(count_array / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("statement related", count_statement,
                                           format(count_statement / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("operator related", count_operator,
                                           format(count_operator / defect_sum * 100, ".4f")))
    print("\t# {}: {} defects, {}%".format("operand related", count_operand,
                                           format(count_operand / defect_sum * 100, ".4f")))
    print("- Number of each type of defects:")
    for k, v in defect_count.items():
        if v > 1:
            print("\t# {}: {} defects, {}%".format(k, v, format(v/defect_sum*100, ".4f")))
        else:
            print("\t# {}: {} defect, {}%".format(k, v, format(v / defect_sum * 100, ".4f")))
    print("===============================================================")


if __name__ == '__main__':
    # evaluate_primitive_dataset()
    evaluate_c_def("comprehensive_db_test")
