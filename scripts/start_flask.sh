bash server_deploy.sh
export FLASK_APP=~/vagabond/server/vagabond/__main__.py
source ~/vagabond/server/vagabond/env/bin/activate
pip3 install -r ~/vagabond/server/requirements.txt
flask run --port 1236
