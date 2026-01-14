import os
import pathlib

import pkg_resources
from setuptools import find_packages
from setuptools import setup

# read the long description from README.md
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

version = "0.3.12"

version = f"{version}{os.environ.get('PIP_VERSION_POSTFIX', '')}"

# read the requirements from requirements.txt
requirements = []
with pathlib.Path("requirements.txt").open() as requirements_txt:
    requirements = [str(requirement) for requirement in pkg_resources.parse_requirements(requirements_txt)]

setup(
    name="gitlab-runner-tart-driver",
    version=version,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/schmieder.matthias/gitlab-runner-tart-driver",
    author="Matthias Schmieder",
    author_email="schmieder.matthias@gmail.com",
    entry_points={"console_scripts": ["gitlab-runner-tart-driver = gitlab_runner_tart_driver.cli:start"]},
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=requirements,
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control",
    ],
)
