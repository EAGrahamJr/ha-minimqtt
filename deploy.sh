#!/bin/sh

TARGET="/media/$(id -u -n)/CIRCUITPY"
find . -name __pycache__ src --exec rm -rf {} \;
cp -av src/ha_minimqtt $TARGET
