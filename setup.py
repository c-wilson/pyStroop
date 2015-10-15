from distutils.core import setup

files = []

setup(name='olfactometry',
      version='0.1',
      description="Simple PyQt4 program to demonstrate the Stroop effect.",
      author='Chris Wilson',
      packages=['strooper'], requires=['PyQt4'])
