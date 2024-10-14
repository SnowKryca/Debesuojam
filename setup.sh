#!/bin/bash

APP_NAME="webcloud"
APP_DIR="/var/www/$APP_NAME"
VENV_DIR="$APP_DIR/venv"
GUNICORN_SERVICE="/etc/systemd/system/$APP_NAME.service"

echo "Updating system and installing dependencies"
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3-pip python3-venv

echo "Setting up virtual environment and installing dependencies"
python3 -m venv $VENV_DIR
source $VENV_DIR/bin/activate
pip install -r $APP_DIR/requirements.txt

echo "Setting ownership for security"
sudo chown -R www-data:www-data $APP_DIR

echo "Configuring Gunicorn service"
cat << EOF | sudo tee $GUNICORN_SERVICE
[Unit]
Description=Gunicorn instance to serve $APP_NAME
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
ExecStart=$VENV_DIR/bin/gunicorn -w 3 -b 0.0.0.0:8000 "webapp:create_app()"

[Install]
WantedBy=multi-user.target
EOF

echo "Starting and enabling Gunicorn service"
sudo systemctl daemon-reload
sudo systemctl start $APP_NAME
sudo systemctl enable $APP_NAME

echo "Setup complete! Your Flask app is running on Gunicorn and listening on port 8000."