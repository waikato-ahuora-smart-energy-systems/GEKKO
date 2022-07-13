# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from codecs import open
import os

here = os.path.abspath(os.path.dirname(__file__))
long_description = """GEKKO
=====

GEKKO is a python package for machine learning and optimization, specializing in
dynamic optimization of differential algebraic equations (DAE) systems. It is coupled 
with large-scale solvers APOPT and IPOPT for linear, quadratic, nonlinear, and mixed integer 
programming. Capabilities include machine learning, discrete or continuous state space
models, simulation, estimation, and control.

Gekko models consist of equations and variables that create a symbolic representation of the
problem for a single data point or single time instance. Solution modes then create the full model
over all data points or time horizon. Gekko supports a wide range of problem types, including:

- Linear programming (LP)
- Quadratic programming (QP)
- Nonlinear programming (NLP)
- Mixed-integer linear programming (MILP)
- Mixed-integer quadratic programming (MIQP)
- Mixed-integer nonlinear programming (MINLP)
- Differential algebraic equations (DAEs)
- Mathematical programming with complementarity constraints (MPCCs)
- Data regression / Machine learning
- Moving Horizon Estimation (MHE)
- Model Predictive Control (MPC)
- Real-Time Optimization (RTO)
- Sequential or Simultaneous DAE solution

Gekko compiles the model into byte-code and provides sparse derivatives to the solver with
automatic differentiation. Gekko is built for industrially hardened control and optimization on Windows,
Linux, MacOS, ARM processors, or any other platform that runs Python. Options are available for local,
edge, or cloud computing.

"""

def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

#gather all files for GUI support
gui_files = package_files('gekko/static')
#add APM executable file
extra_files = gui_files + ['bin/apm.exe','bin/apm','bin/apm_arm','bin/apm_mac']

# versions: a (alpha), b (beta), rc (release candidate)
# update version here, __init__.py, and create a GitHub release
setup(name='gekko',
    version='1.0.4',
    description='Machine learning and optimization for dynamic systems',
    long_description=long_description,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    keywords='differential deep learning reinforcement optimization mixed-integer',
    url='https://github.com/BYU-PRISM/GEKKO',
    author='BYU PRISM Lab',
    author_email='john_hedengren@byu.edu',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        #'flask',
        #'flask_cors',
        'numpy>=1.8'#,
        #'ujson',
    ],
    package_data={'gekko': extra_files},
    python_requires='>=2.6',
    zip_safe=False)
