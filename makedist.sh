#!/bin/sh -x

VERSION=`grep 'VERSION =' uptodate.py | cut -d\" -f 2`
darcs dist --dist-name uptodate-$VERSION
bzme -f uptodate-$VERSION.tar.gz
