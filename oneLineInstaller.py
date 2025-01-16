import os
import subprocess
from sys import platform


def linuxInstaller():
    if not os.path.exists('.venv') and not os.path.exists('venv'):
        # Run the command to create a virtual environment
        subprocess.run(["python3.10", "-m", "venv", "venv"], check=True)
        subprocess.run(["venv/bin/python", "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        subprocess.run(["venv/bin/python", "-m", "unidic", "download"], check=True)

def windowsInstaller():
    if not os.path.exists('.venv') or not os.path.exists('venv'):
        subprocess.run("python -m venv venv", check=True)
        subprocess.run(r"venv\Scripts\python.exe -m pip install -r requirements.txt", check=True)
        subprocess.run(r"venv\Scripts\python.exe -m unidic download", check=True)

if __name__ == "__main__":
    if platform == "linux" or platform == "linux2":
        linuxInstaller()
    else:
        print("This program has not been tested on Windows.")
        windowsInstaller()