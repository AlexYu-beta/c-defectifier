# c-defectifier
a train dataset generator for semantic program fix

#### step 1: configure a task
- @ ./experiment/exp_config.py
- edit your configurations
- run exp_config.py

#### step 2: launch the task and generate the dataset
- @ ./experiment/exp_driver.py
- make some simple modifications, like editing task_name
- run exp_driver.py

#### step 3: evaluate the dataset
- @ ./utils/evaluator.py
- make some simple modifications, like editing task_name
- run evaluator.py

#### step extra: evaluate the model fix
- @ ./utils/test_runner.py
- run test_runner.py