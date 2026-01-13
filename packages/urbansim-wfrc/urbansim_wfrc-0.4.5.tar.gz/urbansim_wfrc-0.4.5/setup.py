import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="urbansim_wfrc",
    version="0.4.5",
    author="WFRC_Analytics",
    author_email="josh.reynolds@wfrc.utah.gov",
    description="Urbansim library originally by Paul Waddell, customized by WFRC Analytics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/WFRCAnalytics/urbansim-wfrc',
    packages=setuptools.find_packages(exclude=['*.tests']),
    classifiers=[
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: BSD License'
    ],
    python_requires='>=3.6',
    install_requires=[
        #'numpy >= 1.8.0',
        'orca_wfrc >= 0.0.1',
        #'pandas = 0.25.1',
        #'pandana = 0.6.1',
        'patsy >= 0.4.1',
        'prettytable >= 0.7.2',
        'pyyaml >= 3.10',
        'scipy >= 1.0',
        'simpledbf >= 0.2.6',
        'statsmodels >= 0.8, <0.11; python_version <"3.6"',
        'statsmodels >= 0.8; python_version >="3.6"',
        'toolz >= 0.8.1',
        'zbox'
    ]
)