# coding: utf-8

from setuptools import setup, find_packages


def readme():
    """Read the README file"""
    with open('README.rst', encoding='utf-8') as f:
        return f.read()


setup(
    name='cadnaPromise',
    version='0.3.9',
    description='Precision auto-tuning of floating-point variables in program',
    long_description=readme(),
    long_description_content_type='text/x-rst',

    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: C",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Operating System :: MacOS",
    ],

    keywords='computer arithmetic mixed-precision precision auto-tuning',
    url='https://github.com/PEQUAN/cadnaPromise',

    author='LIP6 PEQUAN team',
    author_email='thibault.hilaire@lip6.fr; fabienne.jezequel@lip6.fr',

    license='GNU General Public License v3.0',

    packages=find_packages(),

    include_package_data=True,
    package_data={
        "cadnaPromise.promise": ["extra/*"],

        "cadnaPromise": [
            "deltadebug/*",
            "cadna/*",
            "cache/*",
        ],
    },

    install_requires=[
        'colorlog',
        'colorama',
        'tqdm',
        'regex',
        'pyyaml',
        'docopt-ng',
    ],

    tests_require=[
        'pytest',
        'pytest-cov',
    ],

    setup_requires=[
        'setuptools',
        'colorlog',
        'colorama',
        'regex',
    ],

    extras_require={
        'with_doc': [
            'sphinx',
            'sphinx_bootstrap_theme',
        ],
    },

    # ------------------------------------------------------------
    # entry points
    # ------------------------------------------------------------
    entry_points={
        'console_scripts': [
            'promise=cadnaPromise.run:runPromise',
            'activate-promise=cadnaPromise.install:activate',
            'deactivate-promise=cadnaPromise.install:deactivate',
            'load_CADNA_PATH=cadnaPromise.run:loadCADNA',
            'promise-batch=cadnaPromise.run:run_experiment_and_plot',
        ]
    },

    zip_safe=False,
)
