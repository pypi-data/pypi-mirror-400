#!/bin/bash
PRJ=pyovf

# PY=python3.10
# PY=python3.11
# PY=python3.12
# PY=python3.13
PY=python3.14

# $PY -m venv venv_$PY
source venv_$PY/bin/activate
# pip install -U pip setuptools wheel build twine

#* Manually define version (the rest is full automatic)
VERSION='0.2.6'

git pull
echo "__version__ = '$VERSION'" > $PRJ/_version.py
git add -A && git commit -m "Auto-commit for version v$VERSION"
git push
git tag -a "v$VERSION" -m "version $VERSION"
git push origin --tags

#? Check if VERSION is tagged properly
VER_CHK=$(git describe --tags --abbrev=0 | sed -E -e 's/^v//' -e 's/(.*)-.*/\1/')
if [ "$VER_CHK" = "$VERSION" ]
then
    echo "Build package..."
    export VERSION #! used inside setup.py during build
    python -m build; rm -rf build; rm -rf $PRJ.egg-info

    python -m twine upload --repository gitlab_$PRJ dist/*$VERSION* --verbose #* For my GitLab.flavio.be
    # python -m twine upload --repository testpypi dist/*$VERSION* --verbose #* For test PyPI
    # python -m twine upload --repository pypi dist/*$VERSION* --verbose #! For PyPI
else
    echo "Something went wrong :-("
fi
