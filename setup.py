from setuptools import setup, find_packages

setup(
    name='htool',
    version='1.0.1',
    description=('Create and manipulate HTML as objects.'),
    long_description=('HyperText Object-Oriented Layer: create and manipulate '
                      'HTML documents using Python objects.'),
    url='https://github.com/kynikos/htool',
    author='Dario Giovannetti',
    author_email='dev@dariogiovannetti.net',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',  # noqa
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='html web development',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
)
