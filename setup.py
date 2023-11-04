from setuptools import find_packages, setup

from pathlib import Path
from fakeurldetector.version import __version__


def get_requirements():
    requirements_list = []

    with Path("requirements.txt").open() as reqs:
        for install in reqs:
            if install.startswith("#"):
                continue
            requirements_list.append(install.strip())

    return requirements_list


README = Path("Readme.md").read_text()

setup(
    name='URLRakshak',
    version=__version__,
    packages=find_packages(),
    long_description=README,
    long_description_content_type="text/markdown",
    url='https://github.com/ViswanathBalusu/SafeURLInspector',
    license='GPL3.0',
    author='viswanathbalusu',
    author_email='ckvbalusu@gmail.com',
    include_package_data=True,
    description='Fake URL Inspector',
    platforms="any",
    install_requires=get_requirements(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: POSIX :: Linux",
        "Development Status :: 5 - Production/Stable"
    ],
    package_data={
        "": ["data/model.pkl"],
    },
    python_requires=">=3.11",
    scripts=['scripts/URLRakshak'],
)
