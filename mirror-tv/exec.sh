#!/bin/sh

set -x

EXECFOLDER=$1
EXECSCRIPT=$2
ENVFOLDER=.venv

if cd $EXECFOLDER \
    && . ./$ENVFOLDER/bin/activate \
    && python3 $EXECSCRIPT \
    && echo "$EXECSCRIPT is finished"; then exit 0; else echo "$EXECSCRIPT failed"； echo "$EXECSCRIPT failed" > /dev/termination-log; exit 1; fi
