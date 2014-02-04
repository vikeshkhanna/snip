from distutils.core import setup
import os, shutil

if not os.path.isfile('snip'):
	    shutil.copyfile('snip.py', 'snip')

setup(  name = 'snip',
	scripts = [
		'snip'
	    ]
)

os.remove('snip')
