CREATE_SIFT_SET = r'''
create table submit
(
  id                TEXT
    primary key,
  submit_url        TEXT,
  submit_time       TEXT,
  user_id           TEXT,
  user_name         TEXT,
  problem_id        TEXT,
  problem_url       TEXT,
  problem_name      TEXT,
  problem_full_name TEXT,
  language          TEXT,
  status            TEXT,
  error_test_id     TEXT,
  time              TEXT,
  memory            TEXT,
  code              TEXT
);
'''

SIFT_OK = r'''
select t.* from submit t where t.status == "OK";
'''

ITEM_WRITE = r'''
insert into submit(id, submit_url, submit_time, user_id, user_name, problem_id, problem_url, problem_name, problem_full_name, language, status, error_test_id, time, memory, code)
values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?);
'''

QUERY_ALL = r'''
select t.* from submit t'''

DROP_DEFECTIFY = r'''
drop table defectify;'''

CREATE_DEFECTIFY = r'''
create table defectify
(
  id                TEXT
    primary key,
  submit_id         TEXT,
  code              TEXT,
  gen_code          TEXT
);
'''

INSERT_DEFECTIFY = r'''
insert into defectify(id, submit_id, code, gen_code)
values (?,?,?,?);
'''
