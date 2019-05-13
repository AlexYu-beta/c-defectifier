from __future__ import print_function
import os
import sys

from utils.fs_util import init_experiment_fs, generate_exp_output, config_dict, generate_exp_output_db
from utils.db_util import DBConnection
from utils.code_util import parse_header_body
from utils.sqls import *
from utils.random_picker import random_pick, get_randint
from pycparser import c_parser, c_generator
from pycparser.plyparser import ParseError
from defect.defectify import defectify
from utils.logger import Logger


sys.path.extend(['.', '..'])
generator = c_generator.CGenerator


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
                headers, body = parse_header_body(code)
                parser = c_parser.CParser()
                ast = parser.parse(body)
            for i in range(get_randint(repeat_min, repeat_max)):
                defect = random_pick(defects, prob)
                success = defectify(ast, task_name, defect, logger, exp_spec_dict)
                if success:
                    count += 1
                    generate_exp_output(str(count) + ".c", task_name, ast, headers)
                else:
                    logger.log_nothing()
        logger.write_log()
    elif src_type == "db":
        db_origin_path = config_dict["dataset_path"] + "/" + "c_data_ok.db"
        db_target_path = config_dict["exp_output_path"] + "/" + task_name + "/" + task_name+ ".db"
        db_origin = DBConnection(db_origin_path)
        db_target = DBConnection(db_target_path)
        # drop table
        # db_target.execute(DROP_DEFECTIFY, "")
        # create table
        db_target.execute(CREATE_DEFECTIFY, "")
        sift_option = exp_cfg["sift_option"]
        limit = exp_cfg["limit"]
        QUERY = QUERY_ALL
        QUERY_ADD = r'''where '''
        SIFT_COND = []
        if type(sift_option) is dict:
            for k, v in sift_option.items():
                SIFT_COND.append(k + " == " + v)
            QUERY = QUERY + QUERY_ADD + " and ".join(SIFT_COND)
        if limit != "":
            limit_num = int(limit)
            if limit_num >0:
                QUERY = QUERY + " limit " + str(limit) + ";"
        else:
            QUERY = QUERY + ";"
        item_list = db_origin.execute(QUERY, "").fetchall()
        # access to database
        count = 0
        for item in item_list:
            item = list(item)
            submit_id = item[0]
            problem_id = item[5]
            code = item[-1].strip('\'')
            code = code.replace('\r', '')
            headers, body = parse_header_body(code)
            parser = c_parser.CParser()
            try:
                ast = parser.parse(body)
                code = generate_exp_output_db(ast, headers)
            except ParseError:
                print("PE")
                # print(generator.visit(ast))
                continue
            success = False
            success_times = 0
            for i in range(get_randint(repeat_min, repeat_max)):
                success = False
                tries = 0
                while not success:
                    tries += 1
                    if tries > 10:
                        break
                    defect = random_pick(defects, prob)
                    success = defectify(ast, task_name, defect, logger, exp_spec_dict)
                if success:
                    success_times += 1
            if success_times == 0:
                logger.log_nothing()
            else:
                count += 1
                gen_code = generate_exp_output_db(ast, headers)
                # print(gen_code)
                db_target.execute(INSERT_DEFECTIFY, (count, problem_id, submit_id, code, gen_code))
        logger.write_log()
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
    code = r'''
    int main()
{
  int n;
  int m;
  scanf("%d %d", &n, &m);
  int i;
  int j;
  int k;
  char a[n][m];
  for (i = 0; i < n; i++)
  {
    scanf("%s", &a[i]);
  }

  i = 0;
  j = 0;
  int o = 0;
  int p = 0;
  int c = 0;
  int t = 0;
  int mt = m * n;
  int b[((m < n) ? (n) : (m)) + 1];
  for (i = 2; i < (((m < n) ? (n) : (m)) + 1); i++)
  {
    if (b[i] != 1)
    {
      b[i] = 0;
      j = 2;
      while ((i * j) < (((m < n) ? (n) : (m)) + 1))
      {
        b[i * j] = 1;
        j++;
      }

    }

  }

  i = 0;
  j = 0;
  for (k = 2; k <= ((((m < n) ? (n) : (m)) / 2) + 1); k++)
  {
    t = 0;
    if (b[k] == 0)
    {
      for (i = 0; i < n; i = i + k)
      {
        for (j = 0; j < m; j = j + k)
        {
          c = 0;
          for (o = 0; o < k; o++)
          {
            for (p = 0; p < k; p++)
            {
              if (((i + o) < n) && ((j + p) < m))
              {
                if (a[i + o][j + p] == '1')
                {
                  c++;
                }

              }

            }

            if ((((c * 2) > (k * k)) && (((t + (k * k)) - c) >= mt)) || (((c * 2) <= (k * k)) && ((t + c) >= mt)))
              break;

          }

          if ((2 * c) != (k * k))
            t += (k * k) - c;
          else
            t += c;

          if (t >= mt)
            break;

        }

      }

      if (mt > t)
      {
        mt = t;
      }

    }

  }

  printf("%d\n", mt);
  return 0;
}
    '''
    code_1 = r'''
    int main(){
    int i,n,sum;
    sum = 0;
    for (i = 0; i < n; i++)
    {
        sum += i;
        if (sum > 100)
        {
            break;
        }

    }
}
    '''
    parser = c_parser.CParser()
    ast = parser.parse(code_1)
    print(ast)
    # logger = Logger("test")
    # exp_spec_dict = {
    #     "OEDE": {
    #         "from": '='
    #     }
    # }
    # defectify(ast, "test", "test", logger, exp_spec_dict)


if __name__ == '__main__':
    task_name = "Test04_SDFN_DB"
    drive(task_name)
    # test()
