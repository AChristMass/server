import subprocess
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



cmd = f"java -jar BIMserver/bimserver.jar port={settings.BIM_PORT} home={settings.BIM_HOME}"
print(cmd)
out, err = command(cmd)
