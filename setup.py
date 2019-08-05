import codecs
import os
from setuptools import setup


def read_file(name):
    with codecs.open(
            os.path.join(os.path.dirname(__file__), name), 'r', 'utf-8') as f:
        return f.read().strip()


setup(name='waterflows',
      version='0.1',
      description='Hydrological modelling in Python',
      url='https://github.com/jannefiluren/waterflows',
      author='Jan Magnusson',
      author_email='jan.magnusson@gmail.com',
      license='MIT',
      packages=['waterflows'],
      install_requires=read_file('requirements.txt').splitlines(),
      zip_safe=False)
