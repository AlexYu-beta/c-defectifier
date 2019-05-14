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
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

ORRN_DB = {
    "task_name": "Test01_simple_try",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": 1000,
    "defects": {
        "ORRN": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 1,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

OILN_1 = {
    "task_name": "Test02_OILN",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test02_OILN",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "OILN": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 3,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        },
        "OILN": {

        }
    }
}

OILN_1_DB = {
    "task_name": "Test02_OILN_DB",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "OILN": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 3,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        },
        "OILN": {}
    }
}

OILN_2 = {
    "task_name": "Test02_OILN",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test02_OILN",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "OILN": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 3,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        },
        "OILN": {
            "OILN_add_and": 0.1,
            "OILN_add_or": 0.2,
            "OILN_del_and": 0.1,
            "OILN_del_or": 0.2,
            "OILN_negate_cond": 0.4
        }
    }
}

OILN_3 = {
    "task_name": "Test02_OILN",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test02_OILN",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "OILN_add_and": 0.1,
        "OILN_add_or": 0.2,
        "OILN_del_and": 0.1,
        "OILN_del_or": 0.2,
        "OILN_negate_cond": 0.4
    },
    "repeat_min": 1,
    "repeat_max": 3,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        },
        "OILN": {

        }
    }
}

SRIF_1 = {
    "task_name": "Test03_SRIF",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test03_SRIF",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "SRIF_replace_var": 0.3,
        "SRIF_to_expr": 0.4,
        "SRIF_wrap_func_call": 0.2,
        "SRIF_unwrap_func_call": 0.1,
    },
    "repeat_min": 2,
    "repeat_max": 3,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        },
        "OILN": {

        }
    }
}

SRIF_1_DB = {
    "task_name": "Test03_SRIF",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "SRIF": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

SDFN_1 = {
    "task_name": "Test04_SDFN",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test04_SDFN",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "SDFN": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

SDFN_1_DB = {
    "task_name": "Test04_SDFN",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "SDFN": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

OAIS_1 = {
    "task_name": "Test05_OAIS",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test05_OAIS",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "OAIS": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

OAIS_1_DB = {
    "task_name": "Test05_OAIS",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "OAIS": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

STYP_1 = {
    "task_name": "Test06_STYP",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test06_STYP",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "STYP": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

STYP_1_DB = {
    "task_name": "Test06_STYP",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "STYP": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

SMOV_1 = {
    "task_name": "Test07_SMOV",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test07_SMOV",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "SMOV": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

SMOV_1_DB = {
    "task_name": "Test07_SMOV",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "SMOV": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

OFPO_1_DB = {
    "task_name": "Test08_OFPO",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "OFPO": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
    }
}

OFPO_1= {
    "task_name": "Test08_OFPO",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/exp_src/Test08_OFPO",
    "src_type": "files",
    "sift_option": "",
    "limit": 1,
    "defects": {
        "OFPO": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        }
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
    "task_name": "prob_test_db",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "OFPO": 0.1,
        "OILN": 0.3,
        "SRIF": 0.3,
        "ORRN": 0.2,
        "STYP": 0.1
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)]
        },
        "SRIF": {
            "SRIF_replace_var": 0.7,
            "SRIF_to_expr": 0.3
        }
    }
}

DCCR_DB = {
    "task_name": "Test09_DCCR",
    "src_dir": "/home/alex/PycharmProjects/c-defectifier/dataset/c_data_ok.db",
    "src_type": "db",
    "sift_option": "",
    "limit": -1,
    "defects": {
        "DCCR": 1.0
    },
    "repeat_min": 1,
    "repeat_max": 2,
    "specifications": {
        "random_picker": {
            "random_int_list": [0, 1, 2, 3, 5, 10, 20, 30, 40, 50, 100],
            "random_chr_list": [chr(i) for i in range(128)],
            "replacement_offset": [-4, -2, -1, 1, 2, 4]
        },
        "DCCR": {
            "DCCR_to_const": 0.8,
            "DCCR_to_var": 0.2
        }
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
    task_name = "Test09_DCCR_DB"
    conf = DCCR_DB
    generate_experiment_config(task_name)
