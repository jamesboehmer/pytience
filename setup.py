from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('test-requirements.txt') as f:
    test_requirements = f.read().splitlines()

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='pytience',
    version='0.0.3',
    packages=find_packages(exclude=['test']),
    url='https://github.com/jamesboehmer/pytience',
    license='GPLv3',
    author='James Boehmer',
    author_email='james.boehmer@jamesboehmer.com',
    description='A collection of patience solitaire card games.',
    entry_points={
        'console_scripts': ['klondike = pytience.cmd.klondike:play']
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires='>=3.7',
    install_requires=requirements,
    tests_require=test_requirements,
    test_suite='nose.collector',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment"
    ],

)
