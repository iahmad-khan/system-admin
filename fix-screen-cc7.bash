#!/bin/bash

#fixes the screen resolution problem on centos7
gtf 1600 900 60 -x
xrandr --newmode "1600x900" 119.00  1600 1696 1864 2128  900 901 904 932  -HSync +Vsync
xrandr --addmode VGA1 1600x900
xrandr --output VGA1 --mode 1600x900
