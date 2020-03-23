[![travis-ci](https://travis-ci.com/AChristMass/server.svg?branch=master)](https://travis-ci.com/AChristMass/server/)
[![codecov](https://codecov.io/gh/AChristMass/server/branch/master/graph/badge.svg)](https://codecov.io/gh/AChristMass/server)


# Projet RobotMission

### How to setup

First of all you need to setup your python environment for the project.
You need to :

- [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
- Create environment with command `conda create --name robotmissions` 
(you can check your environments with `conda info --envs`)
- Activate environment with `conda activate robotmissions` (you can deactivate with `conda deactivate`)
- Run command `conda install -c conda-forge ifcopenshell`
- Run bash script **install.sh** in **scripts** folder of this git repository
- [Install Postgresql](https://www.tutorialspoint.com/postgresql/postgresql_environment.htm)
- [Setup database](https://www.tutorialspoint.com/postgresql/postgresql_create_database.htm), default settings are (if you change any, change it in robotmissions/settings.py) :
    * 'NAME':     'robotmissions_db'
    * 'USER':     'robotmissions_user'
    * 'PASSWORD': 'missions'
    * 'HOST':     'localhost'
    
### How to run 

To run the project you can launch :
