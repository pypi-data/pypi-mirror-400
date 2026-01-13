"""
Setup script for PyOptima.
"""

from setuptools import setup

# For direct invocation (python setup.py), we still need setup()
if __name__ == "__main__":
    from setuptools import find_packages

    setup(
        packages=find_packages(),
    )

