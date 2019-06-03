import os
import json
import re
from utils.fs_util import get_config, remove_folder
from utils.db_util import DBConnection
from utils.sqls import *
import subprocess as sp
import timeout_decorator

config_dict = get_config()


@timeout_decorator.timeout(2, use_signals=False)
def run_single_test(problem_id, count):
    """

    :param problem_id:
    :return:
    """
    if not count:
        count = 1
    cout_path = config_dict["project_path"] + "/cout/" + problem_id
    test_input = cout_path + "/" + str(count) + ".in"
    test_output = cout_path + "/" + str(count) + ".out"
    sentence_1 = "cd " + cout_path + " && " + "./code.o < " + test_input
    try:
        cmd_1 = sp.check_output(sentence_1, shell=True)
    except Exception:
        return "WA"
    else:
        sentence_2 = "cat " + test_output
        try:
            cmd_2 = sp.check_output(sentence_2, shell=True)
        except Exception:
            return "WA: weird"
        else:
            try:
                cmd_1 = re.sub(b'\n', b'\r\n', cmd_1, flags=re.I)
            except Exception:
                print("WA: weird")
            if cmd_1 == cmd_2:
                return "PASS"
            else:
                return "WA"


def run_tests(problem_id, code):
    """

    :param problem_id:
    :param code:
    :return:
    """
    cout_path = config_dict["project_path"] + "/cout/" + problem_id
    # clear cout folder
    if os.path.exists(cout_path):
        remove_folder(cout_path)
    # create cout folder
    if not os.path.exists(cout_path):
        os.makedirs(cout_path)
    code = code.strip("\'")
    dotc = open(cout_path + "/code.c", "w")
    dotc.write(code)
    dotc.close()
    try:
        sentence = "gcc " + cout_path + "/code.c" + " -o " + cout_path + "/code.o"
        cmd = sp.check_output(sentence, shell=True)
    except sp.CalledProcessError:
        print("cannot compile " + problem_id + "!")
        return False
    db_origin_path = config_dict["dataset_path"] + "/problem_testcase.db"
    db_origin = DBConnection(db_origin_path)
    QUERY = QUERY_TESTCASE + " where pt.problem_id=" + problem_id + ";"
    item = db_origin.execute(QUERY, "").fetchall()
    len_item = len(item)
    if len_item == 0:
        print("no such a problem")
        return False
    test_cases = json.loads(item[0][6].strip("\'"))
    count = 0
    correct_count = 0
    for test_case in test_cases:
        count += 1
        input = test_case["input"]
        output = test_case["output"]
        try:
            print("TestCase " + str(count) + ": ", end="")
            dotin = open(cout_path + "/" + str(count) + ".in", "w")
            dotout = open(cout_path + "/" + str(count) + ".out", "w")
            dotin.write(input)
            dotout.write(output)
            dotin.close()
            dotout.close()
            result = run_single_test(problem_id, count)
            print(result)
            if result == "PASS":
                correct_count += 1
        except Exception:
            print("TLE")
            kill_sentence = "pgrep code.o | xargs kill -9"
            sp.call(kill_sentence, shell=True)
    ret = correct_count / count
    return ret


if __name__ == '__main__':
    code = r"""'#include<stdio.h>
int main()
{
   int n,k,i,j,a[100],t=0,c=-1;
   scanf("%d %d",&n,&k);
   for(i=0;i<n;i++){
        scanf("%d",&a[i]);
        t=t+a[i];
        if(t>8){k=k-8;t=t-8;}
        else{ k=k-t;t=0;}
        if(k<=0){
            c=i+1;
            break;
        }
   }
   if(n*8<k)printf("%d\n",-1);
   else {
    printf("%d\n",c);
   }
   return 0;
}

'"""
    correctness = run_tests("117992", code)
    print("correctness: " + str(format(correctness*100, ".2f")) + "%")
