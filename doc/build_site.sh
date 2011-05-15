#!/bin/sh

VERS="0.1.4"
DATE="2011-05-15"
EMAIL="nicolas.caen@gmail.com"

HTML="asciidoc --attribute icons --attribute=revision=$VERS
--attribute=date=$DATE --attribute=email=$EMAIL"

$HTML quick_start.txt
$HTML -a toc -a numbered reference.txt
