#! /bin/bash

mkdir log
touch log/com1.txt
touch log/com2.txt
touch log/lidar.txt
touch log/lpa.txt
touch log/main.txt

echo 'starting setup INTech CDR 2022 2023'

python3 -m venv ./venv
echo 'venv created'

source ./venv/bin/activate

echo -n 'check path:'
which python

pip install -r requirements.txt
echo 'all module installed'

deactivate
echo 'module installed'
