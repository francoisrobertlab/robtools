from setuptools import setup, find_packages

setup(
    name='RobTools',
    version='2.0-SNAPSHOT',
    packages=find_packages(),
    author='Christian Poitras',
    author_email='christian.poitras@ircm.qc.ca',
    description='Tools to analyze next-generation sequencing (NGS) data',
    keywords='bioinformatics, NGS',
    url='https://github.com/francoisrobertlab/robtools',
    license='GNU General Public License version 3',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License version 3'
    ],
    install_requires=[
        'click>=7.0',
        'pandas>=0.25.0',
        'pyBigWig>=0.3.17',
        'matplotlib>=3.1.1',
        'scipy>=1.3.2',
        'lmfit>=1.0.0'
    ],
    entry_points={
        'console_scripts': [
            'chectools = checseqtools.chectools:chectools',
            'mnasetools = mnaseseqtools.mnasetools:mnasetools',
            'robtools = robtools.robtools:robtools'
        ]
    }
)
