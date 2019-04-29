import os
import shutil
import json
from pycparser import c_generator
from utils.code_util import construct_program


def get_config():
    """
    get the configuration dictionary of project structure
    :return:
    """
    ret = {}
    project_path = os.path.dirname(os.path.abspath("./"))
    dataset_path = project_path + "/dataset"
    exp_src_path = project_path + "/exp_src"
    exp_output_path = project_path + "/exp_output"
    exp_config_path = project_path + "/exp_config"
    log_path = project_path + "/logs"
    ret["project_path"] = project_path
    ret["dataset_path"] = dataset_path
    ret["exp_src_path"] = exp_src_path
    ret["exp_output_path"] = exp_output_path
    ret["exp_config_path"] = exp_config_path
    ret["log_path"] = log_path
    return ret


config_dict = get_config()


def gen_c_from_ast(ast, target_path, headers):
    """
    generate c code from ast
    :param ast:             the defectified ast
    :param target_path:     target C path
    :param headers          code of c headers
    :return:
    """
    generator = c_generator.CGenerator()
    result = generator.visit(ast)
    result = construct_program(headers, result)
    target_file = open(target_path, 'w')
    target_file.write(result)
    target_file.close()


def remove_file(file_path):
    """
    remove a single file according to the file_path
    :param file_path:               the path of file to remove
    :return:
    """
    os.remove(file_path)


def remove_folder(rootdir):
    """
    remove a single folder according to the root dir
    :param rootdir:                 the path of folder to remove
    :return:
    """
    filelist = os.listdir(rootdir)
    for f in filelist:
        filepath = os.path.join(rootdir, f)
        if os.path.isfile(filepath):
            os.remove(filepath)
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)
    shutil.rmtree(rootdir, True)


def init_experiment_fs(task_name):
    """
    initialize file system for an experiment
    :param task_name:   name of the experiment
    :return:
    """

    """
    should be modified to reading several files in a folder
    """

    output_path = config_dict["exp_output_path"] + "/" + task_name
    config_file = config_dict["exp_config_path"] + "/" + task_name + ".json"

    # clear target folder
    if os.path.exists(output_path):
        remove_folder(output_path)
    ############################
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    if not os.path.exists(config_file):
        os.makedirs(config_file)
        print("Err: Please edit experiment configuration first.")
        return None
    else:
        exp_cfg = get_exp_cfg(task_name)
    log_path = config_dict["log_path"] + "/" + task_name + ".log.json"
    # clear log file
    if os.path.exists(log_path):
        remove_file(log_path)
    ############################
    log_file = open(log_path, 'w')
    log_file.close()
    return exp_cfg


def generate_exp_output_db(ast, headers):
    """

    :param ast:
    :param headers:
    :return:
    """
    generator = c_generator.CGenerator()
    result = generator.visit(ast)
    result = construct_program(headers, result)
    return result


def generate_exp_output(file_name, task_name, ast, headers):
    """
    find the location of outputs and generate c code
    :param file_name:               name of c file to generate
    :param task_name:               name of the experiment name
    :param ast:                     ast structure
    :param headers                  c code of headers
    :return:
    """
    output_path = config_dict["exp_output_path"] + "/" + task_name + "/" + file_name
    gen_c_from_ast(ast, output_path, headers)


def gen_exp_cfg(task_name, cfg_dict):
    """
    generate experiment config file from dictionary
    :param task_name:
    :param cfg_dict:
    :return:
    """
    config_path = config_dict["exp_config_path"] + "/" + task_name + ".json"
    with open(config_path, "w") as f:
        json.dump(cfg_dict, f)


def get_exp_cfg(task_name):
    """
    get the experiment config dictionary from local space
    :param task_name:
    :return:
    """
    config_path = config_dict["exp_config_path"] + "/" + task_name + ".json"
    load_dict = {}
    with open(config_path, "r") as f:
        load_dict = json.load(f)
    return load_dict


if __name__ == '__main__':
    task_name = "TrimSum_headerless"
    generate_exp_output("1.c", task_name, 'asfd')
