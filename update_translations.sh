#!/bin/sh -x

xgettext -Lpython `find -name '*.py' | grep -v _darcs | grep -v build | grep -v setup` -s -o locale/uptodate.pot

for po in `find -name '*.po' | grep -v _darcs` ; do
   msgmerge -s -U $po locale/uptodate.pot
done
