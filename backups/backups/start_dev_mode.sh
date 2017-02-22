#!/bin/bash

sudo cp /etc/nginx/conf.d/one_server_default.conf /etc/nginx/conf.d/default.conf

sudo service nginx restart
