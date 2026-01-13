import setuptools

long_description = '''
`extto` is a package for extracting data from text files\n\n

Please see the `extto` documentation for more details.
'''

# DO NOT EDIT THIS NUMBER!
# IT IS AUTOMATICALLY CHANGED BY python-semantic-release
__version__ = '1.1.0'

setuptools.setup(
    name='extto',
    version=__version__,
    author='Jon Kragskow',
    author_email='jgck20@bath.ac.uk',
    description='A package for extracting data from text files',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://extto.kragskow.group',
    project_urls={
        'Bug Tracker': 'https://gitlab.com/kragskow-group/extto/issues',
        'Documentation': 'https://extto.kragskow.group'
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    package_dir={'': '.'},
    packages=setuptools.find_packages(),
    python_requires='>=3.10',
    install_requires=[]
)
