#!/bin/bash

if [ $1 ]
then
    TAG=v$1
    git push --delete origin $TAG; git tag -d $TAG
else
    echo "You must provide a version X.Y.Z"
fi
