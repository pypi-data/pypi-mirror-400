"""
A setuptools based setup module.
Based on:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

import yaml
import setuptools  # type: ignore


def get_version(version_file_loc):
    with open(version_file_loc, 'r') as stream:
        data = yaml.load(stream, yaml.SafeLoader)
        return (data.get('version'))


setuptools.setup(
    name='elements-api',
    version=get_version('ops/conda-recipe/conda_build_config.yaml'),
    description='Elements API Client',
    package_dir={'': 'src/py'},
    packages=setuptools.find_packages('src/py', exclude=[
        'mocked_services',
        'oi_papi',
        'oi_papi.*'
    ]),
    install_requires=['grpcio', 'grpcio-status', 'requests']
)
