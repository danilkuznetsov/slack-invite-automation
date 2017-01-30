#!/usr/bin/env bash

echo "**** install requirements"
pip2 install requests
echo "**** start python"
python ../src/server.py

