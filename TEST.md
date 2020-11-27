How to make a single file out of your program

Using this: https://gehrcke.de/2014/02/distributing-a-python-command-line-application/

### Create package inside virtualenv
virtualenv --python=/usr/bin/python3 testGit3
source testGit3/bin/activate
python setup.py install
use git3 command

## Upload to Pypi

python setup.py sdist
ls dist -> there should be a tar.gz file

## Register your project with Pypi

pip3 install twine
twine upload dist/cmdline-bootstrap-0.2.0.tar.gz 
