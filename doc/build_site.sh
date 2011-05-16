#!/bin/sh

VERS="0.1.3"
DEV="0.1.4-dev"
DATE="2011-05-15"
EMAIL="nicolas.caen@gmail.com"

HTML="asciidoc \
    --conf-file=layout1.conf \
    --attribute stylesdir=css \
    --attribute scriptsdir=javascripts \
    --backend=xhtml11 \
    --attribute icons \
    --attribute=date=$DATE \
    --attribute=email=$EMAIL"

$HTML --attribute=revision=$VERS quick_start.txt
$HTML --attribute=revision=$VERS -a toc -a numbered reference.txt
#$HTML --attribute=revision=$DEV -a toc -a numbered reference-dev.txt
