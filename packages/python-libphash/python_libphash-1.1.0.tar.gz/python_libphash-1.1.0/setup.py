import os
import sys
from setuptools import setup

# Force the working directory to the project root
project_root = os.path.dirname(os.path.abspath(__file__))
os.chdir(project_root)
sys.path.insert(0, project_root)

setup(
    cffi_modules=["src/libphash/_build.py:ffibuilder"],
)
