echo "Installing virtual environment"
python3.10 -m venv venv
source venv/bin/activate
python3 --version
pip install -r requirements.txt
python -m unidic download

echo "Opening app"
#python3 GUI.py