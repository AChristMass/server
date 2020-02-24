#!/bin/bash
echo ""
echo "Installing requirements..."
pip install -r requirements.txt || { echo>&2 "ERROR: pip3 install -r requirements.txt failed"; exit 1; }
echo "Done !"

echo ""
echo "Creating RobotMissionIfc directory...."
if [ ! -d RobotMissionIfc ]; then
    mkdir RobotMissionIfc || { echo>&2 "ERROR: Can't create RobotMissionIfc" ; exit 1; }
fi

echo ""
echo "Configuring database..."
python3 manage.py makemigrations || { echo>&2 "ERROR: python3 manage.py makemigrations failed"; exit 1; }
python3 manage.py migrate || { echo>&2 "ERROR: python3 manage.py migrate failed"; exit 1; }
echo "Done !"

