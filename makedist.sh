#!/bin/sh

darcs dist --dist-name uptodate-`cat version`
bzme -f uptodate-`cat version`.tar.gz
