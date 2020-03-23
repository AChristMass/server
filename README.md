[![travis-ci](https://travis-ci.com/AChristMass/server.svg?branch=master)](https://travis-ci.com/AChristMass/server/)
[![codecov](https://codecov.io/gh/AChristMass/server/branch/master/graph/badge.svg)](https://codecov.io/gh/AChristMass/server)


# Projet RobotMission

### How to setup

First of all you need to setup your python environment for the project.
You need to :

- [Install Postgresql](https://www.tutorialspoint.com/postgresql/postgresql_environment.htm)
- [Setup database](https://www.tutorialspoint.com/postgresql/postgresql_create_database.htm), default settings are (if you change any, change it in robotmissions/settings.py) :
    * 'NAME':     'robotmissions_db'
    * 'USER':     'robotmissions_user'
    * 'PASSWORD': 'missions'
    * 'HOST':     'localhost'
- [Install Anaconda](https://docs.anaconda.com/anaconda/install/)
- Create environment with command `conda create --name robotmissions` 
(you can check your environments with `conda info --envs`)
- Activate environment with `conda activate robotmissions` (you can deactivate with `conda deactivate`)
- Run command `conda install -c conda-forge ifcopenshell`
- Run bash script **install.sh** in **scripts** folder of this git repository

### How to run 

To run the project you can launch :

`python manage.py runserver`

### How to dev

/!\ version linked can not be up to date /!\
Read as much as you can about [Django framework](https://docs.djangoproject.com/en/3.0/)

### How to deploy

On your server [Install nginx](https://docs.nginx.com/nginx/admin-guide/installing-nginx/installing-nginx-open-source/)
then copy nginx conf that is in **deploy/robotmisions.conf** in **etc/nginx/conf.d** folder of your server and restart nginx.

You can now run the project on your server.

### Miscellaneous

- A server may still be running at http://35.210.237.250/