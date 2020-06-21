#!/bin/sh

export PO_USER_KEY=""
export PO_API_TOKEN=""

./wrap.py --days 2020-07-01 2020-07-02 --dtb-path $HOME/somewhere
