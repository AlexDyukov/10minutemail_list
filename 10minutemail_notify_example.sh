#!/usr/bin/env bash

ERROR10MINUTE=$(cat ~/10minutemail.error); [[ ! -z $ERROR10MINUTE ]] && export DISPLAY=:0 && notify-send "10minutemail" "$ERROR10MINUTE"
