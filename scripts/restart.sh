#!/bin/bash

sudo stop server1
sudo stop server
sudo service nginx stop
sudo start server1
sudo start server
sudo service nginx start
