#!/usr/bin/env python

from setuptools import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

def req_file(filename):
    with open(filename) as f:
        content = f.readlines()
        content = filter(lambda x: not x.startswith("#"), content)
    return [x.strip() for x in content]

setup_requirements = [ ]
test_requirements = [ ]

setup(
    author="ian johnson",
    author_email='ionox0@gmail.com',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="fgbio_postprocessing",
    entry_points={
        'console_scripts': [
            'simplex_filter=fgbio_postprocessing.cli:filter_simplex',
        ],
    },
    install_requires=req_file("requirements.txt"),
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    package_data={
        "": ['requirements.txt', 'requirements_dev.txt'],
    },
    keywords='fgbio_postprocessing',
    name='fgbio_postprocessing',
    packages=find_packages(include=['fgbio_postprocessing', 'fgbio_postprocessing.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/ionox0/fgbio_postprocessing',
    version='0.3.0',
    zip_safe=False,
)
