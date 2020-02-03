#!/bin/bash
echo ""
echo "Installing requirements..."
pip3 install -r requirements.txt || { echo>&2 "ERROR: pip3 install -r requirements.txt failed"; exit 1; }
echo "Done !"

echo ""
wget "https://github.com/opensourceBIM/BIMserver/releases/download/v1.5.180/bimserverwar-1.5.180.war" -O "BIMserver/tomcat-8/webapps/bimserver.war" || { echo>&2 "ERROR: BIM server download failure"; exit 1; }
echo "Done !"

echo ""
echo "Configuring database..."
python3 manage.py makemigrations || { echo>&2 "ERROR: python3 manage.py makemigrations failed"; exit 1; }
python3 manage.py migrate || { echo>&2 "ERROR: python3 manage.py migrate failed"; exit 1; }
echo "Done !"
