#! /usr/bin/env python
import os
from setuptools import setup, find_packages

# to run the module do the following command:
# python setup.py sdist

# To upload to twine:
# twine upload dist/<the .tar.gz file>


def get_dependencies():
    """This function reads the requirements.txt file and creates a list of packages to be installed before Learner can
    be installed. In practice, we should be defining a separate dependencies in the setup because the requirements file
    is too restrictive but this is fine for now. As long as the users use docker containers or virtual environments,
    this should't cause any issues.

    :return: a list of libraries/packages to install when installing Learner.
    """
    with open('requirements.txt') as f:
        required = f.read().splitlines()
    return required


def compile_learner():
    """Go through each package and modules, and compile them.

    :return: None
    """
    setup(
        name='clearner',
        version='1.0.2',
        description="Learner is a software platform for building production-ready machine learning models without writing any codes.",
        author="Prizmi LLC",
        author_email="contact@prizmi.ai",
        python_requires='>=3.12,<3.13',
        url="https://prizmi.ai/learner/home",
        license="Other",
        classifiers=[
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "License :: Other/Proprietary License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.12",
        ],
        install_requires=get_dependencies(),
        packages=find_packages(exclude=("tests.*", "tests", "docs.*", "docs")),
        package_data={'learner.schema': ['*.json']},
        entry_points={
            'console_scripts': ['learner=main:main'],
        },
        include_package_data=True,
    )


def clean_up():
    os.system('rm -r *.egg-info')


if __name__ == "__main__":
    compile_learner()
    clean_up()
