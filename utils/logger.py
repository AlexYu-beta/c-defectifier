import time
import json
from utils.fs_util import get_config


class Logger:
    """
    use a logger to collect log items and write once to log file
    """

    def __init__(self, task_name):
        self.task_name = task_name
        self.log_items = []
        config_dict = get_config()
        self.config_file = config_dict["exp_config_path"] + "/" + task_name + ".json"
        self.log_file = config_dict["log_path"] + "/" + task_name + ".log.json"

    def generic_op_logging(self, def_type, position, current_op, replace_op):
        """
        generic operator-based logging function
        :param def_type:            generic defectify type
        :param position:            position to plant a defect
        :param current_op:          original operator
        :param replace_op:          replacing operator
        :param task_name:           experiment task name
        :return:
        """
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

        log_item = {
            "timestamp": timestamp,
            "line_num": position.line,
            "column_num": position.column,
            "def_type": def_type,
            "parameters": {
                "current_op": current_op,
                "replace_op": replace_op
            }
        }
        self.log_items.append(log_item)

    def log_ORRN(self, position, current_op, replace_op):
        self.generic_op_logging("ORRN", position, current_op, replace_op)

    def log_OEDE(self, position, current_op, replace_op, task_name):
        self.generic_op_logging("OEDE", position, current_op, replace_op)

    def log_OILN(self, position, pattern):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_item = {
            "timestamp": timestamp,
            "line_num": position.line,
            "column_num": position.column,
            "def_type": "OILN",
            "parameters": {
                "action": pattern
            }
        }
        self.log_items.append(log_item)

    def log_SRIF(self, position, pattern):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_item = {
            "timestamp": timestamp,
            "line_num": position.line,
            "column_num": position.column,
            "def_type": "SRIF",
            "parameters": {
                "action": pattern
            }
        }
        self.log_items.append(log_item)

    def log_SDFN(self, position, pattern):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_item = {
            "timestamp": timestamp,
            "line_num": position.line,
            "column_num": position.column,
            "def_type": "SDFN",
            "parameters": {
                "action": pattern
            }
        }
        self.log_items.append(log_item)

    def log_OAIS(self, position):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        log_item = {
            "timestamp": timestamp,
            "line_num": position.line,
            "column_num": position.column,
            "def_type": "OAIS",
            "parameters": {
                "action": None
            }
        }
        self.log_items.append(log_item)

    def write_log(self):
        ret = {
            "task_name": self.task_name,
            "exp_conf_dir": self.config_file,
            "log_list": self.log_items
        }
        with open(self.log_file, "w") as f:
            json.dump(ret, f)
