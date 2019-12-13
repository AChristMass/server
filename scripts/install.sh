#!/bin/bash
echo ""
echo "Installing requirements..."
pip3 install -r requirements.txt || { echo>&2 "ERROR: pip3 install -r requirements.txt failed"; exit 1; }
echo "Done !"

echo ""
echo "Installing BIM Server..."
mkdir "BIMserver"
mkdir "BIMserver/home"
wget "http://mirrors.ircam.fr/pub/apache/tomcat/tomcat-8/v8.5.50/bin/apache-tomcat-8.5.50.tar.gz" -O "BIMserver/tomcat.tar.gz" || { echo>&2 "ERROR: tomcat download failed"; exit 1; }
tar -xzvf "BIMserver/tomcat.tar.gz" -C "BIMserver" || { echo>&2 "ERROR: tomcat extract failure"; exit 1; }
mv "BIMserver/apache-tomcat-8.5.50" "BIMserver/tomcat-8" || { echo>&2 "ERROR: could'nt rename tomcat directory"; exit 1; }
wget "https://github.com/opensourceBIM/BIMserver/releases/download/v1.5.180/bimserverwar-1.5.180.war" -O "BIMserver/tomcat-8/webapps/bimserver.war" || { echo>&2 "ERROR: BIM server download failure"; exit 1; }
echo "Done !"

echo ""
echo "Configuring database..."
python3 manage.py makemigrations || { echo>&2 "ERROR: python3 manage.py makemigrations failed"; exit 1; }
python3 manage.py migrate || { echo>&2 "ERROR: python3 manage.py migrate failed"; exit 1; }
echo "Done !"
