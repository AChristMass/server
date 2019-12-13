import json
import subprocess

import requests
from django.conf import settings



def command(cmd):
    p = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True
    )
    out, err = p.communicate()
    if p.returncode:
        raise RuntimeError(f"Return code : {str(p.returncode)} - {err.decode()} {out.decode()}")
    return out, err



def launch_tomcat():
    out, err = command("./BIMserver/tomcat-8/bin/startup.sh")
    return out.decode(), err.decode()



def stop_tomcat():
    out, err = command("./BIMserver/tomcat-8/bin/shutdown.sh")
    return out.decode(), err.decode()



def retrieve_token(response):
    j = json.loads(response)
    if "response" in j and "result" in j["response"]:
        return j["response"]["result"]
    return None


def setup_bim(timeout=10):
    data = {
        "request": {
            "interface":  "AdminInterface",
            "method":     "setup",
            "parameters": {
                "siteAddress":       settings.BIM["url"],
                "serverName":        "robotmissions",
                "serverDescription": "Des missions pour des robots",
                "serverIcon":        "/img/bimserver.png",
                "adminName":         settings.BIM["name"],
                "adminUsername":     settings.BIM["mail"],
                "adminPassword":     settings.BIM["password"]
            }
        }
    }
    response = requests.post("http://localhost:8080/bimserver/json", json=data, timeout=timeout)
    return response



def login(timeout=10):
    data = {
        "request": {
            "interface":  "AuthInterface",
            "method":     "login",
            "parameters": {
                "username": settings.BIM["mail"],
                "password": settings.BIM["password"],
            }
        }
    }
    response = requests.post(settings.BIM["api"], json=data, timeout=timeout)
    return response



def setup_plugin(token):
    data = {
        "token":   token,
        "request": {
            "interface":  "PluginInterface",
            "method":     "installPluginBundleFromUrl",
            "parameters": {
                "url": settings.BIM["smartevac"],
                "installAllPluginsForAllUsers": "false",
                "installAllPluginsForNewUsers": "false"
            }
        }
    }
    response = requests.post(settings.BIM["api"], json=data)
    return response
