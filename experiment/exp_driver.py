from __future__ import print_function
import os
import sys

from utils.fs_util import init_experiment_fs
from utils.random_picker import random_pick
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
    method = exp_cfg["method"]
    defects = exp_cfg["defects"].keys()
    logger = Logger(task_name)
    # in order to release the pressure of passing parameters,
    # move the functionality of code reading from fs_util to exp_driver
    file_list = os.listdir(src_folder)
    # in 'prob' and 'freq', you do not need read all codes from the file_list
    if method == "enum":
        for item in file_list:
            src_path = os.path.join(src_folder, item)
            if os.path.isfile(src_path):
                src_file = open(src_path, 'r')
                code = src_file.read()
                src_file.close()
                parser = c_parser.CParser()
                ast = parser.parse(code)
                for defect in defects:
                    defectify(ast, task_name, defect, "DEBUG", logger, None)
    elif method == "prob":
        number = exp_cfg["number"]
        prob = exp_cfg["defects"].values()
        for i in range(number):
            item = random_pick(file_list, None)
            src_path = os.path.join(src_folder, item)
            if os.path.isfile(src_path):
                src_file = open(src_path, 'r')
                code = src_file.read()
                src_file.close()
                parser = c_parser.CParser()
                ast = parser.parse(code)
                defect = random_pick(defects, prob)
                defectify(ast, task_name, defect, "RANDOM", logger, None)
    elif method == "freq":
        outer_count = 0
        for defect, freq in exp_cfg["defects"].items():
            for i in range(freq):
                item = random_pick(file_list, None)
                src_path = os.path.join(src_folder, item)
                if os.path.isfile(src_path):
                    src_file = open(src_path, 'r')
                    code = src_file.read()
                    src_file.close()
                    parser = c_parser.CParser()
                    ast = parser.parse(code)
                    outer_count += 1
                    defectify(ast, task_name, defect, "RANDOM", logger, outer_count)
    logger.write_log()


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

    defectify(ast, "test", "test", "RANDOM", logger, None)


if __name__ == '__main__':
    task_name = "Test07_SMOV"
    drive(task_name)
    # test()
