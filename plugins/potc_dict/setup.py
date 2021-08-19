from distutils.core import setup

from setuptools import find_packages

_package_name = 'potc_dict'
setup(
    # information
    name=_package_name,
    version='0.0.1b1',
    packages=find_packages(
        include=(_package_name, "%s.*" % _package_name)
    ),

    # environment
    python_requires=">=3.6",
    install_requires=[
        'potc',
    ],
    entry_points={
        'potc_plugin': [
            'pretty_dict=potc_dict.plugin:rules'
        ]
    },
)
