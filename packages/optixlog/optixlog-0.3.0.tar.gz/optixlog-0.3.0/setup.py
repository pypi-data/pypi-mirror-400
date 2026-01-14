from setuptools import setup, find_packages;

setup(
    name='optixlog',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'requests',
        'numpy',
        'matplotlib',
        'pillow',
        'rich',
    ],
    extras_require={
        'mpi': ['mpi4py'],
        'meep': ['meep'],
    },
)