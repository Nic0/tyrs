#!/bin/sh

VERS="0.4.2"
DEV="0.4.3-dev"
DATE="2011-09-20"
EMAIL="nicolas.caen@gmail.com"

HTML="asciidoc \
    --conf-file=layout1.conf \
    --attribute stylesdir=css \
    --attribute iconsdir=images/icons \
    --attribute scriptsdir=javascripts \
    --backend=xhtml11 \
    --attribute icons \
    --attribute=date=$DATE \
    --attribute=email=$EMAIL"


$HTML --attribute=revision=$VERS --attribute=devel=$DEV \
--attribute=date=$DATE index.txt
$HTML --attribute=revision=$VERS quick_start.txt
$HTML --attribute=revision=$VERS -a toc -a numbered reference.txt
$HTML --attribute=revision=$VERS screenshot.txt
