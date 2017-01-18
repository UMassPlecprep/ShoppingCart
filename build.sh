#!/bin/bash

sudo rsync -av --exclude='build.sh' --exclude='tochange.txt' ~/testing/ ~/plecprepShoppingCart/

sudo sed -ie 's/\/testing/\/plecprepShoppingCart/g' ~/plecprepShoppingCart/server.py
sudo sed -ie 's/port=8888/port=8080/g' ~/plecprepShoppingCart/server.py

sudo kill $(pgrep python)
sudo python ~/plecprepShoppingCart/server.py &
