#!/bin/bash

echo '----------start robot------------------'
echo  $1


echo '-------------activate venv-------------------'
source ./venv/bin/activate

# should add something for the version of the robot

echo '----------------start of python script-------------'
python3 src/mainProcess/launcher.py


