from utils.fs_util import gen_exp_cfg

"""
    Write your experiment configuration here.
    You can use the template below.
    <task_name>(str) is the name of the experiment
    <src_dir>(str) is the path of source files on which to experiment
    <method>(str) is the defect-planting method
        - 'enum': try all defect possibilities(DEBUG mode)
        - 'prob': plant defect based on probability distribution
        - 'freq': plant defect based on frequency distribution
    <number>(int) is the number of randomized defect to choose to plant, required if <method> is 'prob'
    <defects>(dict) is the dictionary of defects and their weights
        - <defect>::=<defect name>: <weight>
        - <weight> can be anything if <method> is 'enum'
        - <weight> can be any non-negative integer if <method> is 'freq'
        - <weight> can be some float between 0 and 1 if <method> is 'prob' 
"""
conf = {

}

conf_template_01 = {
    "task_name": "Test01_simple_try",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test01_simple_try",
    "method": "enum",
    "defects": {
        "ORRN": 1
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
        gen_exp_cfg(task_name, conf_template_01)
    else:
        gen_exp_cfg(task_name, conf)


if __name__ == '__main__':
    task_name = "Test05_OAIS"
    conf = OAIS
    generate_experiment_config(task_name)

