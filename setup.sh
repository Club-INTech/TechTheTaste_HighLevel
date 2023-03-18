#!/bin/bash

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
