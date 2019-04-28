from __future__ import print_function
import os
import sys

from utils.fs_util import init_experiment_fs, generate_exp_output
from utils.random_picker import random_pick, get_randint
from pycparser import c_parser
from defect.defectify import defectify
from utils.logger import Logger


sys.path.extend(['.', '..'])


def drive(task_name):
    """
    drive a defectify task from configuration file
    :param task_name:       the experiment name
    :return:
    """
    # initialize the experiment file system and fetch the config
    exp_cfg = init_experiment_fs(task_name)
    src_folder = exp_cfg["src_dir"]
    src_type = exp_cfg["src_type"]
    defects = list(exp_cfg["defects"].keys())
    prob = list(exp_cfg["defects"].values())
    repeat_min = exp_cfg["repeat_min"]
    repeat_max = exp_cfg["repeat_max"]
    exp_spec_dict = exp_cfg["specifications"]
    # instantiate some self-defined objects
    logger = Logger(task_name)
    if src_type == "files":
        # in order to release the pressure of passing parameters,
        # move the functionality of code reading from fs_util to exp_driver
        file_list = os.listdir(src_folder)
        count = 0
        for file in file_list:
            src_path = os.path.join(src_folder, file)
            if os.path.isfile(src_path):
                src_file = open(src_path, 'r')
                code = src_file.read()
                src_file.close()
                parser = c_parser.CParser()
                ast = parser.parse(code)
            for i in range(get_randint(repeat_min, repeat_max)):
                defect = random_pick(defects, prob)
                success = defectify(ast, task_name, defect, logger, exp_spec_dict)
                if success:
                    count += 1
                    generate_exp_output(str(count) + ".c", task_name, ast)
                else:
                    logger.log_nothing()
            logger.write_log()
    elif src_type == "db":
        sift_option = exp_cfg["sift_option"]
        limit = exp_cfg["limit"]
        # access to database
    else:
        print("Err: Wrong source type.")


def test():
    """
    test a defective task

    :return:
    """
    exp_src = "/home/alex/PycharmProjects/c-defectifier/exp_src/test.c"
    src_file = open(exp_src, 'r')
    code = src_file.read()
    src_file.close()
    parser = c_parser.CParser()
    ast = parser.parse(code)
    logger = Logger("test")
    exp_spec_dict = {
        "OEDE": {
            "from": '='
        }
    }
    defectify(ast, "test", "test", logger, exp_spec_dict)


if __name__ == '__main__':
    task_name = "Test03_SRIF"
    drive(task_name)
    # test()
