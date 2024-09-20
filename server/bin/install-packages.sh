echo installing luncho_pypyenv with pypy3

deactivate 2>/dev/null || true
if [ "`which pypy3`" == "" ]; then
    brew install pypy3
fi
if [ "`which virtualenv`" == "" ]; then
    pip install virtualenv
fi

if [ ! -e luncho_pypyenv ]; then
   virtualenv --python pypy3 luncho_pypyenv
fi

. luncho_pypyenv/bin/activate
pip install -U -r requirements-pypy.txt


echo installing luncho_pyenv with Python 3.9

deactivate 2>/dev/null || true
if [ "`which python3`" == "" ]; then
    brew install python3
fi
if [ ! -e luncho_pyenv ]; then
   virtualenv --python python3 luncho_pyenv
fi

. luncho_pyenv/bin/activate
pip install -U -r requirements.txt

. luncho_pypyenv/bin/activate
