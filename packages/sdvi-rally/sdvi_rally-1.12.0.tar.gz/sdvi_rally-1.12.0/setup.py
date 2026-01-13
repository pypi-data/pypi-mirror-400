import os

import setuptools

from rally import __version__

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(THIS_DIR, 'README.md')) as readme:
    long_description = readme.read()

# Note: distutils will complain about the long_description_content_type. It does not cause any problems.
#  It is a known deficiency and will not be fixed.
setuptools.setup(
    name='sdvi-rally',
    license='Proprietary',
    version=__version__,
    author='SDVI Corp',
    description='Rally Python SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(exclude=['test', 'test.*', 'DocstringStyle.md', 'conftest.py']),
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    py_modules=['rally.tools.cli'],
    install_requires=['Click', 'certifi'],
    entry_points='''
        [console_scripts]
        rally=rally.tools:cmd
    ''',
    package_data={'': ['LICENSE', 'README.md', 'RELEASE']},
    include_package_data=True
)
