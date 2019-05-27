from __future__ import print_function
import os
import sys
import json

from utils.fs_util import init_experiment_fs, generate_exp_output, config_dict, generate_exp_output_db
from utils.db_util import DBConnection
from utils.code_util import parse_header_body, code_diff
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
        db_target_path = config_dict["exp_output_path"] + "/" + task_name + "/" + task_name + ".db"
        left_file = config_dict["exp_output_path"] + "/" + task_name + "/left"
        right_file = config_dict["exp_output_path"] + "/" + task_name + "/right"
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
            headers, body, sharp_defines = parse_header_body(code)
            parser = c_parser.CParser()
            try:
                ast = parser.parse(body)
                code = generate_exp_output_db(ast, headers)
                headers, body, sharp_defines = parse_header_body(code)
                ast = parser.parse(body)
            except ParseError:
                print("PE")
                # print(generator.visit(ast))
                continue
            success = False
            success_times = 0
            annotations = {}
            line_nums = []
            code_before = code
            code_after = None
            for i in range(get_randint(repeat_min, repeat_max)):
                success = False
                tries = 0
                while not success:
                    tries += 1
                    if tries > 500:
                        break
                    defect = random_pick(defects, prob)
                    success = defectify(ast, task_name, defect, logger, exp_spec_dict, line_nums)
                if success:
                    success["line_num"] += len(headers.split("\n")) - sharp_defines
                    # perform annotation check
                    line_num_checked = str(success["line_num"])
                    code_after = generate_exp_output_db(ast, headers)
                    success["line_code"] = code_before.split("\n")[success["line_num"] - 1]
                    success["line_code_def"] = code_after.split("\n")[success["line_num"] - 1]
                    code_diff_info = code_diff(code_before, code_after)
                    if code_diff_info.startswith(line_num_checked, 2, len(code_diff_info)):
                        success_times += 1
                        annotations[str(success_times)] = success
                        line_nums.append(int(line_num_checked))
                        code_before = code_after
                    else:
                        continue

            if success_times == 0:
                logger.log_nothing()
            else:
                count += 1
                gen_code = generate_exp_output_db(ast, headers)
                # for j in range(1, success_times + 1):
                #     annotation = annotations[str(j)]
                #     annotation["line_code"] = code.split("\n")[annotation["line_num"] - 1]
                #     annotation["line_code_def"] = gen_code.split("\n")[annotation["line_num"] - 1]
                # # print(gen_code)
                db_target.execute(INSERT_DEFECTIFY, (count, problem_id, submit_id, code, gen_code, json.dumps(annotations), "UNCHECKED"))
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
    int i;
    sum = 0;
    for (i = 0; i < 100; i++)
    {
        sum += i;
        if (sum > 100)
        {
            break;
        }

    }
    printf("%d\n", sum);
}
    '''

    code_t = '''int main()
{
  unsigned long n;
  scanf("%lu", &n);
  long *a = malloc(n * (sizeof(long)));
  long *b = malloc(n * (sizeof(long)));
  long i;
  unsigned long long brSektora = 0;
  long pocetak;
  long prethodni;
  for (i = 0; i < n; i++)
  {
    scanf("%ld", &a[i]);
    b[a[i] - 1] = i;
    if (a[i] == 1)
      pocetak = i;

  }

  prethodni = pocetak;
  for (i = 1; i < n; i++)
  {
    if ((b[i] - b[i - brSektora]) > 0)
      brSektora += b[i] - b[i - 1];
    else
      brSektora += b[i - 1] - b[i];

  }

  printf("%llu", brSektora);
  return 0;
}'''
    code_2 = '''int main() {
    int a, b;
    while(scanf("%d%d", &a, &b) > 0) {
        int t = 0;
        int d = 240 - b;
        int c = 5;
        while(d-c >= 0 && t < a) {
            t++;
            c += (t+1) * 5;
        }
        printf("%d\n", t);
    }
    return 0;
}'''
    headers, body, sharp_defines = parse_header_body(code_2)
    parser = c_parser.CParser()
    try:
        ast = parser.parse(body)
        code_2 = generate_exp_output_db(ast, headers)
        print(code_2)
        headers, body, sharp_defines = parse_header_body(code_2)
        ast = parser.parse(body)
    except ParseError:
        print("PE")
        # print(generator.visit(ast))
    print(len(body.split("\n")))


if __name__ == '__main__':
    task_name = "comprehensive_db_test"
    drive(task_name)
    # test()
