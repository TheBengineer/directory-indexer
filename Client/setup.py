__author__ = 'boh01'


from distutils.core import setup

try:
    import py2exe
except:
    print "Cannot import py2exe. Download and install it from here:\nhttp://sourceforge.net/projects/py2exe/"
    exit()


setup(
    options = {'py2exe': {'compressed': False}},
    windows = [{'script': "main.py"}],

)

