from utils.fs_util import gen_exp_cfg

"""
    Write your experiment configuration here.
    You can use the template below.
    <task_name>(str) is the name of the experiment
    <src_dir>(str) is the path of source code on which to experiment
    <src_type>(str): decides the type of source code
        - 'files': source code stored as .c files
        - 'db': source code stored as database items
    <sift_option>: used as optional description of sifting condition(maybe query), keep blank with no sift option
    <limit>(int): limit the number of items in <src_dir>
    <defects>(dict): is the dictionary of defects and their weights
        - <defect name>(str):<weight>(float)
            ...
    <repeat_min>(int): the minimum times of repetition for each item
    <repeat_max>(int): the maximum times of repetition for each item 
    <specifications>(dict): stores the detailed specifications of the experiment, including each type of defects
        - <spec item>(str):<specification>
            ...
"""
conf = {

}

conf_template = {
    "task_name": "Test01_simple_try",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test01_simple_try",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "ORRN": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 10,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

OILN = {
    "task_name": "Test02_OILN",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test02_OILN",
    "method": "freq",
    "defects": {
        "OILN": 10
    }
}

SRIF = {
    "task_name": "Test03_SRIF",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test03_SRIF",
    "method": "freq",
    "defects": {
        "SRIF": 20
    }
}

SDFN = {
    "task_name": "Test04_SDFN",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test04_SDFN",
    "method": "freq",
    "defects": {
        "SDFN": 10
    }
}

OAIS = {
    "task_name": "Test05_OAIS",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test05_OAIS",
    "method": "freq",
    "defects": {
        "OAIS": 10
    }
}

STYP = {
    "task_name": "Test06_STYP",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test06_STYP",
    "method": "freq",
    "defects": {
        "STYP": 10
    }
}

SMOV = {
    "task_name": "Test07_SMOV",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test07_SMOV",
    "method": "freq",
    "defects": {
        "SMOV": 10
    }
}

OFPO = {
    "task_name": "Test08_OFPO",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test08_OFPO",
    "method": "freq",
    "defects": {
        "OFPO": 10
    }
}

conf_prob_test = {
    "task_name": "prob_test",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/prob_test",
    "method": "prob",
    "number": 20,
    "defects": {
        "ORRN": 0.1,
        "OEDE": 0.2,
        "OILN": 0.7
    }
}


def generate_experiment_config(task_name):
    """
    user's interface to generate an experiment configuration
    :param task_name:
    :return:
    """
    if conf == {}:
        gen_exp_cfg(task_name, conf_template)
    else:
        gen_exp_cfg(task_name, conf)


if __name__ == '__main__':
    task_name = "Test01_simple_try"
    conf = conf_template
    generate_experiment_config(task_name)

