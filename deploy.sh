#!/bin/sh

TARGET="/media/$(id -u -n)/CIRCUITPY"
find src -name __pycache__ -exec rm -rf {} \;
cp -av src/ha_minimqtt $TARGET
