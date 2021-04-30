from subprocess import check_call
from sys import platform

def copy2clip(txt):
    if platform == 'darwin':
        cmd='echo '+txt.strip()+'|pbcopy'
        return check_call(cmd, shell=True)
    else:
        cmd='echo '+txt.strip()+'|clip'
        return check_call(cmd, shell=True)
