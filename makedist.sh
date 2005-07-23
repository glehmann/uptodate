#!/bin/sh -x


for po in `find -name '*.po'` ; do
   d=`dirname $po`
   cd $d
   msgfmt -c -v  uptodate.po -o uptodate.mo
   cd -
done

darcs dist --dist-name uptodate-`cat version`
bzme -f uptodate-`cat version`.tar.gz
