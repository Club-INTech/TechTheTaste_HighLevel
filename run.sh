#!/bin/bash

echo  $1
echo '---------------------------------- start robot ----------------------------------'
echo  $1

echo '--------------------------------- activate venv ---------------------------------'
echo  $1
source ./venv/bin/activate

# should add something for the version of the robot
echo '----------------------------- start of python script ----------------------------'
python3 src/mainProcess/launcher.py


