#!/bin/sh -x

VERSION=`grep 'VERSION =' uptodate.py | cut -d\" -f 2`

# darcs changes > ChangeLog
perl -pi -e "s/^%define version\s+.+$/%define version\t\t$VERSION/g" uptodate.spec
rm -f predist.sh makedist.sh

# compile translation files
for po in `find -name '*.po'` ; do
   d=`dirname $po` 
   cd $d
   msgfmt -c -v  uptodate.po -o uptodate.mo
   cd -
done

